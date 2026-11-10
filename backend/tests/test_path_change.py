from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import delete, select, update

from app.models import PathChangeRequest, UpdateHistory, User
from scripts import seed_content, seed_journey

ME = "/api/v1/me/path-change"
ADMIN = "/api/v1/admin/path-requests"


@pytest.fixture(scope="module", autouse=True)
def roadmaps(database):
    seed_content.main()
    seed_journey.main()


@pytest.fixture(autouse=True)
def clean(db):
    yield
    db.execute(delete(PathChangeRequest))
    db.commit()


def path_of(client):
    return client.get("/api/v1/auth/me").json()["path"]


def age_last_change(db, days):
    """Pretend the student's last change happened this many days ago."""
    db.execute(update(UpdateHistory).where(UpdateHistory.entity_type == "user_path")
               .values(created_at=datetime.now(UTC) - timedelta(days=days)))
    db.commit()


def test_first_change_is_free_and_immediate(client, student):
    assert client.get(ME).json()["free_left"] == 1
    body = client.post(ME, json={"path": "doctor"}).json()
    assert body["result"] == "changed" and path_of(client) == "doctor"
    assert client.get("/api/v1/me/saved-progress").json()["path"] == "doctor"


def test_progress_is_kept_when_the_path_changes(client, student):
    client.put("/api/v1/me/saved-progress", json={"steps": {"5": {"note": "proof"}}, "skills": ["clear-speaking"]})
    client.post(ME, json={"path": "doctor"})
    saved = client.get("/api/v1/me/saved-progress").json()
    assert saved["steps"]["5"]["note"] == "proof" and saved["skills"] == ["clear-speaking"]


def test_a_second_change_waits_six_months_with_no_admin(client, student, db):
    client.post(ME, json={"path": "doctor"})
    early = client.post(ME, json={"path": "pilot"})
    assert early.status_code == 409 and "change your path again from" in early.json()["detail"]
    assert client.get(ME).json()["next_change_on"] is not None and path_of(client) == "doctor"
    age_last_change(db, 183)
    assert client.get(ME).json()["next_change_on"] is None
    assert client.post(ME, json={"path": "pilot"}).json()["result"] == "changed" and path_of(client) == "pilot"
    assert db.scalar(select(PathChangeRequest)) is None   # nothing ever waits for an admin


def test_bad_choices_are_refused(client, student):
    assert client.post(ME, json={"path": "web-developer"}).status_code == 422   # already the path
    assert client.post(ME, json={"path": "not-a-career"}).status_code == 422
    assert client.post(ME, json={"path": "doctor", "reason": "x" * 301}).status_code == 422


def test_old_requests_can_still_be_answered(client, student, admin_client, db):
    user = db.scalar(select(User).where(User.email == "asha@example.com"))
    db.add(PathChangeRequest(user_id=user.id, from_path="web-developer", to_path="pilot", reason="Older request"))
    db.commit()
    request_id = admin_client.get(ADMIN).json()[0]["id"]
    assert admin_client.post(f"{ADMIN}/{request_id}", json={"approve": True}).json()["status"] == "approved"
    assert path_of(client) == "pilot"


def test_students_cannot_answer_requests(client, student):
    assert client.get(ADMIN).status_code == 403
    assert client.post(f"{ADMIN}/1", json={"approve": True}).status_code == 403

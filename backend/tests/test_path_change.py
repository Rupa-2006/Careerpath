import pytest
from sqlalchemy import delete, select

from app.models import PathChangeRequest, User
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


def test_first_change_is_free_and_immediate(client, student):
    assert client.get(ME).json()["free_left"] == 1
    body = client.post(ME, json={"path": "doctor"}).json()
    assert body["result"] == "changed" and path_of(client) == "doctor"
    assert client.get(ME).json()["free_left"] == 0
    assert client.get("/api/v1/me/saved-progress").json()["path"] == "doctor"


def test_progress_is_kept_when_the_path_changes(client, student):
    client.put("/api/v1/me/saved-progress", json={"steps": {"5": {"note": "proof"}}, "skills": ["clear-speaking"]})
    client.post(ME, json={"path": "doctor"})
    saved = client.get("/api/v1/me/saved-progress").json()
    assert saved["steps"]["5"]["note"] == "proof" and saved["skills"] == ["clear-speaking"]


def test_after_the_free_change_it_becomes_a_request(client, student):
    client.post(ME, json={"path": "doctor"})
    assert client.post(ME, json={"path": "pilot"}).status_code == 422   # a reason is needed now
    body = client.post(ME, json={"path": "pilot", "reason": "I want to fly"}).json()
    assert body["result"] == "requested" and path_of(client) == "doctor"
    latest = client.get(ME).json()["latest"]
    assert latest["status"] == "pending" and latest["to_path"] == "pilot"
    assert client.post(ME, json={"path": "nurse", "reason": "again"}).status_code == 409   # one at a time


def test_bad_choices_are_refused(client, student):
    assert client.post(ME, json={"path": "web-developer"}).status_code == 422   # already the path
    assert client.post(ME, json={"path": "not-a-career"}).status_code == 422
    assert client.post(ME, json={"path": "doctor", "reason": "x" * 301}).status_code == 422


def test_admin_approves_and_the_path_changes(client, student, admin_client):
    client.post(ME, json={"path": "doctor"})
    client.post(ME, json={"path": "pilot", "reason": "I want to fly"})
    waiting = admin_client.get(ADMIN).json()
    assert waiting[0]["status"] == "pending" and waiting[0]["student_email"] == "asha@example.com"
    decided = admin_client.post(f"{ADMIN}/{waiting[0]['id']}", json={"approve": True}).json()
    assert decided["status"] == "approved" and path_of(client) == "pilot"
    assert admin_client.post(f"{ADMIN}/{waiting[0]['id']}", json={"approve": False}).status_code == 409


def test_admin_rejects_and_nothing_changes(client, student, admin_client):
    client.post(ME, json={"path": "doctor"})
    client.post(ME, json={"path": "pilot", "reason": "I want to fly"})
    request_id = admin_client.get(ADMIN).json()[0]["id"]
    admin_client.post(f"{ADMIN}/{request_id}", json={"approve": False})
    assert path_of(client) == "doctor" and client.get(ME).json()["latest"]["status"] == "rejected"


def test_students_cannot_answer_requests(client, student):
    assert client.get(ADMIN).status_code == 403
    assert client.post(f"{ADMIN}/1", json={"approve": True}).status_code == 403


def test_deleting_the_account_deletes_its_requests(client, student, db):
    from tests.conftest import PASSWORD
    client.post(ME, json={"path": "doctor"})
    client.post(ME, json={"path": "pilot", "reason": "I want to fly"})
    client.request("DELETE", "/api/v1/me", json={"password": PASSWORD})
    assert db.scalar(select(PathChangeRequest)) is None and db.scalar(select(User)) is None

import pytest
from sqlalchemy import select

from app.models import User
from scripts import seed_content, seed_journey

URL = "/api/v1/me/saved-progress"

GOOD = {
    "path": "web-developer",
    "path_from": "area=engineering&course=btech-cse",
    "steps": {"12": {"on": "2026-11-01", "note": "Built a portfolio page"}, "13": {"on": "2026-11-05"}},
    "skills": ["python-basics", "clear-speaking", "python-basics"],
}


@pytest.fixture(scope="module", autouse=True)
def roadmaps(database):
    seed_content.main()
    seed_journey.main()


def test_needs_login(client):
    assert client.get(URL).status_code == 401
    assert client.put(URL, json=GOOD).status_code == 401


def test_new_account_starts_with_the_path_chosen_at_sign_up(client, student):
    body = client.get(URL).json()
    assert body["path"] == "web-developer" and body["steps"] == {} and body["skills"] == []
    assert client.get("/api/v1/auth/me").json()["path"] == "web-developer"


def test_sign_up_needs_a_real_career(client):
    base = {"username": "newstudent", "email": "new@example.com", "password": "Another-Strong-99"}
    assert client.post("/api/v1/auth/register", json=base).status_code == 422
    assert client.post("/api/v1/auth/register", json={**base, "path": "not-a-career"}).status_code == 422


def test_the_path_stays_fixed(client, student):
    saved = client.put(URL, json={**GOOD, "path": "doctor"}).json()
    assert saved["path"] == "web-developer" and "12" in saved["steps"]


def test_saves_and_returns_everything(client, student, db):
    saved = client.put(URL, json=GOOD).json()
    assert saved["path"] == "web-developer" and saved["saved_at"]
    assert saved["steps"]["12"] == {"on": "2026-11-01", "note": "Built a portfolio page"}
    assert saved["skills"] == ["clear-speaking", "python-basics"]   # duplicates removed
    assert client.get(URL).json()["steps"] == saved["steps"]
    assert db.scalar(select(User).where(User.email == "asha@example.com")).saved_progress["path"] == "web-developer"


@pytest.mark.parametrize("bad", [
    {**GOOD, "path": "Web Developer!"},
    {**GOOD, "steps": {"abc": {}}},
    {**GOOD, "steps": {"12": {"on": "yesterday"}}},
    {**GOOD, "steps": {"12": {"note": "x" * 301}}},
    {**GOOD, "skills": ["<script>"]},
    {**GOOD, "extra": "anything"},
])
def test_refuses_bad_or_oversized_data(client, student, bad):
    assert client.put(URL, json=bad).status_code == 422


def test_each_student_sees_only_their_own(client, student):
    client.put(URL, json=GOOD)
    client.post("/api/v1/auth/logout")
    client.post("/api/v1/auth/register", json={"username": "ravi", "email": "ravi@example.com", "password": "Another-Strong-99", "path": "web-developer"})
    assert client.get(URL).json()["steps"] == {}


def test_deleting_the_account_deletes_the_progress(client, student, db):
    from tests.conftest import PASSWORD
    client.put(URL, json=GOOD)
    assert client.request("DELETE", "/api/v1/me", json={"password": PASSWORD}).status_code == 204
    assert db.scalar(select(User).where(User.email == "asha@example.com")) is None


DIARY = {"id": "e1", "on": "2026-11-09", "at": "2026-11-09T18:00:00Z", "did": "Two Python videos",
         "learned": "How loops work", "next": "Start networking basics", "step": 12}


def test_diary_is_saved_and_returned(client, student):
    saved = client.put(URL, json={**GOOD, "diary": [DIARY]}).json()
    assert saved["diary"][0]["learned"] == "How loops work"
    assert client.get(URL).json()["diary"][0]["next"] == "Start networking basics"


@pytest.mark.parametrize("bad", [
    {**DIARY, "did": "x" * 501},
    {**DIARY, "on": "yesterday"},
    {**DIARY, "id": "<b>"},
    {**DIARY, "mood": "happy"},
])
def test_diary_refuses_bad_entries(client, student, bad):
    assert client.put(URL, json={**GOOD, "diary": [bad]}).status_code == 422


def test_admins_never_see_a_diary(client, student, admin_client):
    client.put(URL, json={**GOOD, "diary": [DIARY]})
    listing = admin_client.get("/api/v1/admin/users").text
    assert "loops" not in listing and "diary" not in listing

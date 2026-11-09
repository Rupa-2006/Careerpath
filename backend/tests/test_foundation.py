from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, update

from app.core.security import SESSION_COOKIE
from app.main import app
from app.models import UpdateHistory, User, UserSession
from tests.conftest import PASSWORD

API = "/api/v1"


def login(client, email="asha@example.com", password=PASSWORD):
    return client.post(f"{API}/auth/login", json={"email": email, "password": password})


# ---------- Reference data ----------

def test_health(client):
    assert client.get(f"{API}/health").json() == {"status": "ok"}


def test_all_states_and_union_territories(client):
    regions = client.get(f"{API}/reference/states").json()
    kinds = [region["kind"] for region in regions]
    assert kinds.count("state") == 28
    assert kinds.count("union_territory") == 8
    assert {"Andhra Pradesh", "Ladakh", "Puducherry", "Nagaland"} <= {region["name"] for region in regions}


def test_streams_keep_local_names_and_subjects(client):
    streams = {stream["slug"]: stream for stream in client.get(f"{API}/reference/streams").json()}
    assert "MPC" in streams["science-maths"]["aliases"]
    assert {"Physics", "Chemistry", "Biology", "English"} == {s["name"] for s in streams["science-biology"]["subjects"]}


def test_seed_can_run_twice(client):
    from scripts import seed_reference
    seed_reference.main()
    assert len(client.get(f"{API}/reference/states").json()) == 36


# ---------- Sign up and log in ----------

def test_register_logs_in_and_never_returns_the_password(client, student):
    assert student["role"] == "student"
    assert "password" not in str(student)
    assert client.get(f"{API}/auth/me").json()["email"] == "asha@example.com"


def test_password_is_hashed(client, student, db):
    stored = db.scalar(select(User).where(User.email == "asha@example.com")).password_hash
    assert stored.startswith("$argon2id$")
    assert PASSWORD not in stored


def test_session_token_is_stored_hashed(client, student, db):
    token = client.cookies[SESSION_COOKIE]
    assert db.scalar(select(func.count()).select_from(UserSession).where(UserSession.token_hash == token)) == 0


def test_cookie_is_protected(career, client):
    response = client.post(f"{API}/auth/register", json={"email": "b@example.com", "password": PASSWORD, "path": "web-developer"})
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie


def test_email_is_case_insensitive(career, client, student):
    client.post(f"{API}/auth/logout")
    assert login(client, "ASHA@Example.com").status_code == 200
    duplicate = client.post(f"{API}/auth/register", json={"email": "Asha@example.com", "password": PASSWORD, "path": "web-developer"})
    assert duplicate.status_code == 409


@pytest.mark.parametrize("password", ["short", "1234567890123", "password123", "asha-is-great-1"])
def test_weak_passwords_are_refused(career, client, password):
    response = client.post(f"{API}/auth/register", json={"email": "asha@example.com", "password": password, "path": "web-developer"})
    assert response.status_code == 422


def test_invalid_email_is_refused(career, client):
    assert client.post(f"{API}/auth/register", json={"email": "nope", "password": PASSWORD, "path": "web-developer"}).status_code == 422


def test_wrong_password_and_unknown_email_look_the_same(client, student):
    client.post(f"{API}/auth/logout")
    wrong = login(client, password="Wrong-Password-99")
    unknown = login(client, email="nobody@example.com")
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_logout_really_ends_the_session(client, student):
    token = client.cookies[SESSION_COOKIE]
    assert client.post(f"{API}/auth/logout").status_code == 204
    client.cookies.set(SESSION_COOKIE, token)
    assert client.get(f"{API}/auth/me").status_code == 401


def test_expired_session_is_refused(client, student, db):
    db.execute(update(UserSession).values(expires_at=datetime.now(UTC) - timedelta(minutes=1)))
    db.commit()
    assert client.get(f"{API}/auth/me").status_code == 401


def test_made_up_cookie_is_refused(client):
    client.cookies.set(SESSION_COOKIE, "made-up")
    assert client.get(f"{API}/auth/me").status_code == 401


# ---------- Rate limits ----------

def test_login_locks_after_five_wrong_passwords(client, student):
    client.post(f"{API}/auth/logout")
    for _ in range(5):
        assert login(client, password="Wrong-Password-99").status_code == 401
    assert login(client).status_code == 429


def test_lock_only_affects_that_email(career, client, student):
    client.post(f"{API}/auth/logout")
    for _ in range(5):
        login(client, password="Wrong-Password-99")
    client.post(f"{API}/auth/register", json={"email": "ravi@example.com", "password": PASSWORD, "path": "web-developer"})
    client.post(f"{API}/auth/logout")
    assert login(client, "ravi@example.com").status_code == 200


def test_good_login_resets_the_count(client, student):
    client.post(f"{API}/auth/logout")
    for _ in range(4):
        login(client, password="Wrong-Password-99")
    assert login(client).status_code == 200
    client.post(f"{API}/auth/logout")
    for _ in range(4):
        login(client, password="Wrong-Password-99")
    assert login(client).status_code == 200


def test_too_many_signups_from_one_place_are_refused(career, client):
    codes = [
        client.post(f"{API}/auth/register", json={"email": f"s{i}@example.com", "password": PASSWORD, "path": "web-developer"}).status_code
        for i in range(11)
    ]
    assert codes[:10] == [201] * 10 and codes[10] == 429


# ---------- Forged requests and headers ----------

def test_request_without_client_header_is_blocked():
    with TestClient(app) as plain:
        assert plain.post(f"{API}/auth/login", json={}).status_code == 403


def test_request_from_another_site_is_blocked(client):
    response = client.post(
        f"{API}/auth/login", json={"email": "a@example.com", "password": PASSWORD},
        headers={"Origin": "https://evil.example"},
    )
    assert response.status_code == 403


def test_our_own_frontend_is_allowed(client, student):
    client.post(f"{API}/auth/logout")
    response = client.post(
        f"{API}/auth/login", json={"email": "asha@example.com", "password": PASSWORD},
        headers={"Origin": "http://localhost:5173"},
    )
    assert response.status_code == 200


def test_security_headers(client):
    headers = client.get(f"{API}/health").headers
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["x-frame-options"] == "DENY"
    assert headers["cache-control"] == "no-store"
    assert headers["content-security-policy"] == "default-src 'none'"


# ---------- Profile ----------

def test_save_state_and_stream(client, student):
    region = client.get(f"{API}/reference/states").json()[0]["id"]
    stream = client.get(f"{API}/reference/streams").json()[0]["id"]
    saved = client.patch(f"{API}/me", json={"region_id": region, "stream_id": stream}).json()
    assert (saved["region_id"], saved["stream_id"]) == (region, stream)
    assert client.get(f"{API}/auth/me").json()["region_id"] == region


def test_field_left_out_is_kept_and_null_clears_it(client, student):
    stream = client.get(f"{API}/reference/streams").json()[0]["id"]
    client.patch(f"{API}/me", json={"stream_id": stream, "name": "Asha"})
    assert client.patch(f"{API}/me", json={"name": "Asha K"}).json()["stream_id"] == stream
    assert client.patch(f"{API}/me", json={"stream_id": None}).json()["stream_id"] is None


def test_unknown_state_is_refused(client, student):
    assert client.patch(f"{API}/me", json={"region_id": 999999}).status_code == 422


def test_student_cannot_make_themselves_admin(client, student):
    assert client.patch(f"{API}/me", json={"role": "admin"}).json()["role"] == "student"


def test_profile_needs_login(client):
    assert client.patch(f"{API}/me", json={"name": "X"}).status_code == 401


def test_change_password_logs_out_other_devices(client, student):
    with TestClient(app, headers={"X-CareerPath-Client": "web"}) as phone:
        assert login(phone).status_code == 200
        new = "Green-Window-Seven-8"
        response = client.post(f"{API}/me/password", json={"current_password": PASSWORD, "new_password": new})
        assert response.status_code == 204
        assert phone.get(f"{API}/auth/me").status_code == 401
    assert client.get(f"{API}/auth/me").status_code == 200
    client.post(f"{API}/auth/logout")
    assert login(client, password=new).status_code == 200


def test_change_password_needs_the_current_one(client, student):
    response = client.post(f"{API}/me/password", json={"current_password": "wrong", "new_password": "Green-Window-Seven-8"})
    assert response.status_code == 403


def test_delete_account_needs_password(client, student, db):
    assert client.request("DELETE", f"{API}/me", json={"password": "wrong"}).status_code == 403
    assert db.scalar(select(func.count()).select_from(User)) == 1


def test_delete_account_removes_everything(client, student, db):
    assert client.request("DELETE", f"{API}/me", json={"password": PASSWORD}).status_code == 204
    assert db.scalar(select(func.count()).select_from(User)) == 0
    assert db.scalar(select(func.count()).select_from(UserSession)) == 0


# ---------- Admin ----------

@pytest.mark.parametrize("path", ["/admin/summary", "/admin/users"])
def test_admin_pages_refuse_strangers_and_students(career, client, path):
    assert client.get(API + path).status_code == 401
    client.post(f"{API}/auth/register", json={"email": "asha@example.com", "password": PASSWORD, "path": "web-developer"})
    assert client.get(API + path).status_code == 403


def test_summary_shows_real_counts(admin_client):
    summary = admin_client.get(f"{API}/admin/summary").json()
    assert summary["admins"] == 1 and summary["students"] == 0 and summary["regions"] == 36


def test_user_search_treats_percent_as_plain_text(admin_client):
    assert admin_client.get(f"{API}/admin/users", params={"q": "%"}).json()["total"] == 0
    assert admin_client.get(f"{API}/admin/users", params={"q": "admin@"}).json()["total"] == 1


def test_user_list_never_includes_password_hashes(admin_client):
    assert "argon2" not in admin_client.get(f"{API}/admin/users").text


def test_deactivating_a_user_logs_them_out_and_is_recorded(admin_client, client, student, db):
    response = admin_client.patch(f"{API}/admin/users/{student['id']}", json={"is_active": False})
    assert response.json()["is_active"] is False
    assert client.get(f"{API}/auth/me").status_code == 401
    client.cookies.clear()
    assert login(client).status_code == 401
    assert db.scalar(select(UpdateHistory).where(UpdateHistory.entity_id == student["id"])).changes == {"is_active": False}


def test_admin_cannot_lock_themselves_out(admin_client):
    me = admin_client.get(f"{API}/auth/me").json()
    assert admin_client.patch(f"{API}/admin/users/{me['id']}", json={"role": "student"}).status_code == 400

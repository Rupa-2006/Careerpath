import re

import pytest

from app.api import auth
from tests.conftest import PASSWORD

API = "/api/v1/auth"
NEW_PASSWORD = "Quiet-Harbour-7731"


@pytest.fixture
def outbox(monkeypatch):
    """Catches emails instead of printing or sending them."""
    sent = []
    monkeypatch.setattr(auth, "send_email", lambda to, subject, body: sent.append((to, subject, body)) or True)
    return sent


def code_in(mail) -> str:
    return re.search(r"\b(\d{6})\b", mail[2]).group(1)


def test_log_in_with_username_or_email(client, student):
    client.post(f"{API}/logout")
    assert client.post(f"{API}/login", json={"login": "asha", "password": PASSWORD}).status_code == 200
    client.post(f"{API}/logout")
    assert client.post(f"{API}/login", json={"login": "ASHA@example.com", "password": PASSWORD}).status_code == 200
    assert client.get(f"{API}/me").json()["username"] == "asha"


def test_wrong_password_gives_one_message(client, student):
    client.post(f"{API}/logout")
    wrong = client.post(f"{API}/login", json={"login": "asha", "password": "Wrong-Password-99"})
    unknown = client.post(f"{API}/login", json={"login": "nobody", "password": "Wrong-Password-99"})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json()["detail"] == unknown.json()["detail"]


@pytest.mark.parametrize("name", ["ab", "has space", "UPPER!", "a" * 21, "emoji😀"])
def test_bad_usernames_are_refused(client, career, name):
    body = {"username": name, "email": "new@example.com", "password": "Another-Strong-99", "path": "web-developer"}
    assert client.post(f"{API}/register", json=body).status_code == 422


def test_usernames_are_unique_and_lowercase(client, student):
    client.post(f"{API}/logout")
    body = {"username": "Asha", "email": "second@example.com", "password": "Another-Strong-99", "path": "web-developer"}
    assert client.post(f"{API}/register", json=body).status_code == 409


def test_password_cannot_contain_the_username(client, career):
    body = {"username": "kiranraj", "email": "k@example.com", "password": "kiranraj-Long-99", "path": "web-developer"}
    assert client.post(f"{API}/register", json=body).status_code == 422


def test_reset_password_with_a_code(client, student, outbox):
    client.post(f"{API}/logout")
    assert client.post(f"{API}/forgot-password", json={"email": "asha@example.com"}).status_code == 200
    code = code_in(outbox[0])
    reset = client.post(f"{API}/reset-password", json={"email": "asha@example.com", "code": code, "new_password": NEW_PASSWORD})
    assert reset.status_code == 200
    assert client.post(f"{API}/login", json={"login": "asha", "password": PASSWORD}).status_code == 401
    assert client.post(f"{API}/login", json={"login": "asha", "password": NEW_PASSWORD}).status_code == 200
    again = client.post(f"{API}/reset-password", json={"email": "asha@example.com", "code": code, "new_password": "Another-Strong-99"})
    assert again.status_code == 400   # a code works once


def test_unknown_email_gets_the_same_answer_and_no_mail(client, student, outbox):
    known = client.post(f"{API}/forgot-password", json={"email": "asha@example.com"}).json()
    unknown = client.post(f"{API}/forgot-password", json={"email": "nobody@example.com"}).json()
    assert known == unknown and len(outbox) == 1


def test_wrong_codes_lock_after_five_tries(client, student, outbox):
    client.post(f"{API}/forgot-password", json={"email": "asha@example.com"})
    code = code_in(outbox[0])
    wrong = "000000" if code != "000000" else "111111"
    for _ in range(5):
        client.post(f"{API}/reset-password", json={"email": "asha@example.com", "code": wrong, "new_password": NEW_PASSWORD})
    right = client.post(f"{API}/reset-password", json={"email": "asha@example.com", "code": code, "new_password": NEW_PASSWORD})
    assert right.status_code == 400


def test_reset_logs_out_everywhere(client, student, outbox):
    client.post(f"{API}/forgot-password", json={"email": "asha@example.com"})
    client.post(f"{API}/reset-password", json={"email": "asha@example.com", "code": code_in(outbox[0]), "new_password": NEW_PASSWORD})
    assert client.get(f"{API}/me").status_code == 401


def test_forgot_username_emails_it(client, student, outbox):
    client.post(f"{API}/forgot-username", json={"email": "asha@example.com"})
    assert "asha" in outbox[0][2] and outbox[0][0] == "asha@example.com"


def test_forgot_pages_are_rate_limited(client, student, outbox):
    codes = [client.post(f"{API}/forgot-username", json={"email": "asha@example.com"}).status_code for _ in range(6)]
    assert codes[-1] == 429

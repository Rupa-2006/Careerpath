import pytest
from sqlalchemy import select

from app.core.config import get_settings
from app.models import Scholarship
from scripts import seed_content, seed_scholarships
from scripts.content import SOURCES
from scripts.scholarships_content import SCHOLARSHIPS

API = "/api/v1"


@pytest.fixture(scope="module", autouse=True)
def content(database):
    seed_content.main()


@pytest.fixture
def show_all(monkeypatch):
    monkeypatch.setattr(get_settings(), "show_unpublished", True)


@pytest.fixture
def loaded(db):
    seed_scholarships.main()
    db.expire_all()
    return db


def test_every_source_exists():
    assert all(row[-1] in SOURCES for row in SCHOLARSHIPS)


def test_records_wait_for_review(loaded):
    assert {item.status for item in loaded.scalars(select(Scholarship))} == {"pending_verification"}


def test_students_see_nothing_until_published(client, loaded):
    assert client.get(f"{API}/scholarships").json() == []


def test_list_shows_source_and_status(client, loaded, show_all):
    rows = client.get(f"{API}/scholarships").json()
    assert len(rows) == len(SCHOLARSHIPS)
    assert all(row["source"]["url"] and row["status"] == "pending_verification" for row in rows)


def test_both_states_have_a_scholarship_with_rules(client, loaded, show_all):
    rows = {row["state"]: row for row in client.get(f"{API}/scholarships").json() if row["state"]}
    assert set(rows) == {"AP", "TS"}
    assert all("₹" in row["who_can_apply"] for row in rows.values())


def test_running_the_load_again_keeps_review_status(loaded):
    item = loaded.scalar(select(Scholarship).where(Scholarship.slug == "pm-vidyalaxmi"))
    item.status = "published"
    loaded.commit()
    seed_scholarships.main()
    loaded.expire_all()
    assert loaded.scalar(select(Scholarship.status).where(Scholarship.slug == "pm-vidyalaxmi")) == "published"
    item = loaded.scalar(select(Scholarship).where(Scholarship.slug == "pm-vidyalaxmi"))
    item.status = "pending_verification"
    loaded.commit()

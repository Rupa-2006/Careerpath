import pytest
from sqlalchemy import select

from app.core.config import get_settings
from app.models import CourseListing
from scripts import seed_content, seed_course_list
from scripts.content import COURSES, SOURCES
from scripts.course_list_data import COURSE_LIST

URL = "/api/v1/course-list"


@pytest.fixture(scope="module", autouse=True)
def content(database):
    seed_content.main()
    seed_course_list.main()


@pytest.fixture
def show_all(monkeypatch):
    monkeypatch.setattr(get_settings(), "show_unpublished", True)


def test_every_row_has_a_real_source_and_state():
    assert all(row[6] in SOURCES and row[3] in ("AP", "TS", "India") for row in COURSE_LIST)


def test_every_detail_link_goes_to_a_real_course():
    slugs = {course["slug"] for course in COURSES}
    assert {row[5] for row in COURSE_LIST if row[5]} <= slugs


def test_no_row_is_listed_twice_for_a_state():
    assert len({(row[0], row[3]) for row in COURSE_LIST}) == len(COURSE_LIST)


def test_students_see_nothing_until_published(client):
    assert client.get(URL).json() == []


def test_list_shows_when_unpublished_records_are_allowed(client, show_all):
    rows = client.get(URL).json()
    assert len(rows) == len(COURSE_LIST)
    assert all(row["source"]["url"] for row in rows)


def test_running_the_load_again_keeps_review_status(db):
    row = db.scalar(select(CourseListing).limit(1))
    row.status = "published"
    db.commit()
    seed_course_list.main()
    db.expire_all()
    assert db.get(CourseListing, row.id).status == "published"
    row.status = "pending_verification"
    db.commit()

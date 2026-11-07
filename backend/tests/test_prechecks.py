import pytest
from sqlalchemy import select, update

from app.models import EntranceExam
from scripts import seed_content, seed_journey, seed_prechecks, seed_scholarships
from scripts.prechecked import PRECHECKED

URL = "/api/v1/admin/review"


@pytest.fixture(scope="module", autouse=True)
def content(database):
    seed_content.main()
    seed_journey.main()
    seed_scholarships.main()
    seed_prechecks.main()


def marked(admin_client):
    return {(item["entity"], item["title"]) for item in admin_client.get(f"{URL}?status=pending_verification").json() if item["prechecked"]}


def test_only_the_listed_records_are_marked(admin_client):
    assert marked(admin_client) == set(PRECHECKED)


def test_marking_publishes_nothing(admin_client):
    assert admin_client.get(f"{URL}?status=published").json() == []


def test_changed_text_loses_its_mark(admin_client, db):
    exam = db.scalar(select(EntranceExam).where(EntranceExam.slug == "tg-ecet"))
    original = exam.summary
    exam.summary = "Changed after the check."
    db.commit()
    assert ("exam", "TG ECET") not in marked(admin_client)
    db.execute(update(EntranceExam).where(EntranceExam.slug == "tg-ecet").values(summary=original))
    db.commit()
    assert ("exam", "TG ECET") in marked(admin_client)


def test_students_cannot_read_the_review_queue(client):
    assert client.get(f"{URL}?status=pending_verification").status_code == 401

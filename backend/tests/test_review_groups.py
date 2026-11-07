import pytest
from sqlalchemy import func, select, update

from app.models import EntranceExam, Field, UpdateHistory, VerificationRecord
from scripts import seed_content

API = "/api/v1"
URL = f"{API}/admin/review-group"


@pytest.fixture(scope="module", autouse=True)
def content(database):
    seed_content.main()


@pytest.fixture(autouse=True)
def back_to_waiting(db):
    yield
    db.rollback()
    db.execute(update(EntranceExam).values(status="pending_verification"))
    db.commit()


def exam_ids(db, limit=3):
    return list(db.scalars(select(EntranceExam.id).order_by(EntranceExam.id).limit(limit)))


def statuses(db, ids):
    db.expire_all()
    return list(db.scalars(select(EntranceExam.status).where(EntranceExam.id.in_(ids))))


def test_publishes_the_group_and_students_can_see_it(admin_client, client, db):
    ids = exam_ids(db)
    response = admin_client.post(f"{URL}/exam", json={"ids": ids, "checked": True})
    assert response.json() == {"published": 3, "skipped": 0}
    assert len(client.get(f"{API}/exams").json()) == 3


def test_refused_unless_the_admin_confirms_checking(admin_client, db):
    ids = exam_ids(db)
    assert admin_client.post(f"{URL}/exam", json={"ids": ids, "checked": False}).status_code == 422
    assert admin_client.post(f"{URL}/exam", json={"ids": ids}).status_code == 422
    assert set(statuses(db, ids)) == {"pending_verification"}


def test_only_the_records_shown_are_published(admin_client, db):
    ids = exam_ids(db, 4)
    admin_client.post(f"{URL}/exam", json={"ids": ids[:2], "checked": True})
    assert statuses(db, ids).count("published") == 2


def test_students_and_visitors_cannot_use_it(client, student, db):
    assert client.post(f"{URL}/exam", json={"ids": exam_ids(db), "checked": True}).status_code == 403


def test_forged_requests_are_blocked(admin_client, db):
    response = admin_client.post(
        f"{URL}/exam", json={"ids": exam_ids(db), "checked": True},
        headers={"X-CareerPath-Client": "web", "Origin": "https://evil.example"},
    )
    assert response.status_code == 403


def test_records_with_no_source_are_skipped(admin_client, db):
    ids = exam_ids(db)
    keep = db.scalar(select(EntranceExam.source_id).where(EntranceExam.id == ids[0]))
    db.execute(update(EntranceExam).where(EntranceExam.id == ids[0]).values(source_id=None))
    db.commit()
    assert admin_client.post(f"{URL}/exam", json={"ids": ids, "checked": True}).json() == {"published": 2, "skipped": 1}
    db.expire_all()
    assert db.get(EntranceExam, ids[0]).status == "pending_verification"
    db.execute(update(EntranceExam).where(EntranceExam.id == ids[0]).values(source_id=keep))
    db.commit()


def test_an_out_of_date_record_is_not_published_by_accident(admin_client, db):
    ids = exam_ids(db)
    admin_client.post(f"{API}/admin/review/exam/{ids[0]}", json={"status": "outdated"})
    assert admin_client.post(f"{URL}/exam", json={"ids": ids, "checked": True}).json() == {"published": 2, "skipped": 1}
    db.expire_all()
    assert db.get(EntranceExam, ids[0]).status == "outdated"


def test_each_record_keeps_its_own_history(admin_client, db):
    ids = exam_ids(db)
    admin_client.post(f"{URL}/exam", json={"ids": ids, "checked": True})
    wanted = [str(item) for item in ids]
    condition = (VerificationRecord.entity_type == "exam", VerificationRecord.entity_id.in_(wanted), VerificationRecord.note == "Published as a group")
    assert db.scalar(select(func.count()).select_from(VerificationRecord).where(*condition)) == 3
    assert db.scalar(select(func.count()).select_from(UpdateHistory).where(UpdateHistory.entity_type == "exam", UpdateHistory.entity_id.in_(wanted))) == 3


def test_unknown_group_and_empty_list_are_refused(admin_client, db):
    assert admin_client.post(f"{URL}/user", json={"ids": [1], "checked": True}).status_code == 404
    assert admin_client.post(f"{URL}/exam", json={"ids": [], "checked": True}).status_code == 422


def test_a_group_of_fields_works_too(admin_client, db):
    ids = list(db.scalars(select(Field.id).order_by(Field.id).limit(2)))
    assert admin_client.post(f"{URL}/field", json={"ids": ids, "checked": True}).json()["published"] == 2
    db.execute(update(Field).values(status="pending_verification"))
    db.commit()


def test_a_group_can_be_larger_than_500_records(admin_client, db):
    response = admin_client.post(f"{URL}/exam", json={"ids": [*exam_ids(db), *range(100000, 100600)], "checked": True})
    assert response.status_code == 200
    assert response.json()["published"] == len(exam_ids(db, 3))

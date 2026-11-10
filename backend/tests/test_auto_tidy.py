from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy import delete, select

from app.models import Field, SourceWatch
from app.watch import check_one, is_important
from scripts.auto_tidy import tidy

PAGE = "<p>" + "Welcome to the official admissions site of the university. " * 5 + "</p>"


@pytest.fixture
def clean(db):
    yield db
    db.rollback()
    db.execute(delete(SourceWatch).where(SourceWatch.url.like("https://example.test/%")))
    db.execute(delete(Field).where(Field.slug == "tidy-test"))
    db.commit()


@pytest.mark.parametrize("summary, important", [
    ("Added: Data last refreshed on : 11/8/2026", False),
    ("Added: 359.33 Crores", False),
    ("Added: Visitors: 120345", False),
    ("Added: Home | About us | Contact", False),
    ("Added: TG EAPCET 2027 notification released", True),
    ("Added: Last date to apply extended", True),
    ("Removed: Eligibility: 45% in Intermediate", True),
])
def test_only_important_changes_count(summary, important):
    assert is_important(summary) is important


def test_small_page_changes_do_not_alert(clean):
    watch = SourceWatch(name="Test", url="https://example.test/a", affects="test")
    check_one(watch, lambda _: PAGE)
    assert check_one(watch, lambda _: PAGE + "<p>Photo gallery updated with new pictures</p>") == "minor" and not watch.needs_review
    assert check_one(watch, lambda _: PAGE + "<p>Admission notification for 2027 released</p>") == "changed"
    assert watch.needs_review


def test_old_alerts_and_waiting_records_clear_themselves(clean):
    db = clean
    old = SourceWatch(name="Old", url="https://example.test/old", affects="test", needs_review=True,
                      last_changed_at=datetime.now(UTC) - timedelta(days=40))
    new = SourceWatch(name="New", url="https://example.test/new", affects="test", needs_review=True,
                      last_changed_at=datetime.now(UTC) - timedelta(days=2))
    waiting = Field(slug="tidy-test", name="Tidy test", tagline="", what_is_it="", what_you_learn="", who_can_choose="",
                    required_skills="", further_education="", status="pending_verification", last_updated=date.today() - timedelta(days=40))
    db.add_all([old, new, waiting])
    db.commit()
    result = tidy(db)
    assert result["alerts cleared"] >= 1 and result["waiting records set aside"] >= 1
    db.expire_all()
    assert not db.get(SourceWatch, old.id).needs_review and db.get(SourceWatch, new.id).needs_review
    assert db.scalar(select(Field).where(Field.slug == "tidy-test")).status == "outdated"

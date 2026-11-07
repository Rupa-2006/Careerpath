from datetime import date

import pytest
from sqlalchemy import delete, select

from app.models import CourseListing, ImportantDate, Source, SourceWatch
from app.sync import DOST_URL, MIN_COURSES, check_dates, dost_courses, sync_dost


def table(names):
    rows = "".join(f"<tr><td>{i}</td><td>( ) --&gt; {name}</td><td>3</td></tr>" for i, name in enumerate(names))
    return f"<table>{rows}</table>"


REAL = [f"B.A (Subject {i})" for i in range(MIN_COURSES + 5)]


@pytest.fixture
def clean(db):
    yield db
    db.rollback()
    db.execute(delete(CourseListing))
    db.execute(delete(SourceWatch))
    db.execute(delete(ImportantDate))
    db.execute(delete(Source).where(Source.url == "https://example.test/exam"))
    db.commit()


def test_reads_names_and_lengths():
    assert dost_courses(table(["B.Sc. Life Science (CBCS)"])) == {"B.Sc. Life Science (CBCS)": "3"}


def test_new_courses_are_added_and_published(clean):
    assert "105 added" in sync_dost(clean, lambda _: table(REAL))
    row = clean.scalar(select(CourseListing).where(CourseListing.name == "B.A (Subject 0)"))
    assert row.status == "published" and row.state == "TS" and row.group_name == "Arts"
    assert "0 added" in sync_dost(clean, lambda _: table(REAL))


def test_removed_courses_are_never_deleted_only_flagged(clean):
    sync_dost(clean, lambda _: table(REAL))
    result = sync_dost(clean, lambda _: table(REAL[1:]))
    assert "1 to check" in result
    assert clean.scalar(select(CourseListing).where(CourseListing.name == "B.A (Subject 0)")) is not None
    alert = clean.scalar(select(SourceWatch).where(SourceWatch.url == f"{DOST_URL}#removed"))
    assert alert.needs_review and "B.A (Subject 0)" in alert.change_summary


def test_a_broken_page_changes_nothing(clean):
    sync_dost(clean, lambda _: table(REAL))
    assert "nothing changed" in sync_dost(clean, lambda _: table(REAL[:3]))
    assert len(clean.scalars(select(CourseListing)).all()) == len(REAL)


def test_a_site_that_fails_changes_nothing(clean):
    def broken(_):
        raise OSError("down")
    assert "could not read" in sync_dost(clean, broken)


def test_date_announcements_are_suggested_never_set(clean):
    source = Source(name="Test exam site", url="https://example.test/exam", is_official=True)
    item = ImportantDate(title="TG EAPCET 2027", certainty="NOT_ANNOUNCED", status="published", source=source, checked_on=date.today())
    clean.add(item)
    clean.commit()
    page = "<p>" + "Welcome to the official site. " * 10 + "</p><p>TG EAPCET 2027 Notification released</p>"
    assert "1 may" in check_dates(clean, lambda _: page)
    clean.expire_all()
    assert clean.get(ImportantDate, item.id).certainty == "NOT_ANNOUNCED"
    assert clean.scalar(select(SourceWatch).where(SourceWatch.url.like("%#date-%"))).needs_review


def test_last_years_academic_year_is_not_an_announcement(clean):
    source = Source(name="Test exam site", url="https://example.test/exam", is_official=True)
    clean.add(ImportantDate(title="TG EAPCET 2027", certainty="NOT_ANNOUNCED", status="published", source=source, checked_on=date.today()))
    clean.commit()
    page = "<p>" + "Welcome to the official site. " * 10 + "</p><p>Admissions for the academic year 2026-2027 schedule</p>"
    assert "0 may" in check_dates(clean, lambda _: page)

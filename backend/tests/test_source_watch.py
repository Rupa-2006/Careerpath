import pytest
from sqlalchemy import delete

from app.models import SourceWatch
from app.watch import check_one, page_text, what_changed

URL = "/api/v1/admin/watches"
PAGE = "<html><body><script>var x=1</script><p>" + "Official rule text. " * 20 + "</p><p>Last date is 10 May</p></body></html>"


@pytest.fixture
def watch(db):
    item = SourceWatch(name="Test page", url="https://example.test/rules", affects="A rule")
    db.add(item)
    db.commit()
    yield item
    db.rollback()
    db.execute(delete(SourceWatch))
    db.commit()


def test_scripts_and_visitor_counters_are_ignored():
    assert page_text("<p>Hello</p><script>secret()</script>") == "Hello"
    assert page_text("<p>No. of Visitors: 123</p>") == page_text("<p>No. of Visitors: 456</p>")


def test_live_counters_are_ignored_but_dates_are_kept():
    assert page_text("<p>917</p><p>Seats</p>") == page_text("<p>916</p><p>Seats</p>")
    assert page_text("<p>10-05-2026</p>") != page_text("<p>20-05-2026</p>")


def test_first_visit_saves_the_page_without_an_alert(watch):
    assert check_one(watch, lambda _: PAGE) == "new"
    assert watch.needs_review is False


def test_same_page_gives_no_alert(watch):
    check_one(watch, lambda _: PAGE)
    assert check_one(watch, lambda _: PAGE) == "same"
    assert watch.needs_review is False


def test_a_changed_page_alerts_and_says_what_changed(watch):
    check_one(watch, lambda _: PAGE)
    assert check_one(watch, lambda _: PAGE.replace("10 May", "20 May")) == "changed"
    assert watch.needs_review is True
    assert "20 May" in watch.change_summary and "10 May" in watch.change_summary


def test_a_blank_page_is_never_a_change(watch):
    check_one(watch, lambda _: PAGE)
    assert check_one(watch, lambda _: "<div id=root></div>") == "unreadable"
    assert watch.needs_review is False and watch.last_error


def test_a_failed_site_keeps_the_saved_page(watch):
    check_one(watch, lambda _: PAGE)
    saved = watch.content_hash

    def broken(_):
        raise OSError("site down")

    assert check_one(watch, broken) == "failed"
    assert watch.content_hash == saved and "site down" in watch.last_error


def test_binary_junk_is_never_stored(watch):
    assert check_one(watch, lambda _: "\x00" * 500) == "unreadable"
    assert watch.last_text is None


def test_summary_marks_added_and_removed():
    assert what_changed("old line", "new line") == "Removed: old line\nAdded: new line"


def test_admin_can_clear_an_alert(admin_client, db, watch):
    check_one(watch, lambda _: PAGE)
    check_one(watch, lambda _: PAGE.replace("10 May", "20 May"))
    db.commit()
    row = next(item for item in admin_client.get(URL).json() if item["id"] == watch.id)
    assert row["needs_review"] is True
    assert admin_client.post(f"{URL}/{watch.id}/reviewed").status_code == 200
    db.expire_all()
    assert db.get(SourceWatch, watch.id).needs_review is False


def test_students_cannot_read_alerts(client):
    assert client.get(URL).status_code == 401

"""
Every college below is invented for testing, is named as such, and only exists in the
temporary test database. Real college data only ever comes from the official file.
"""
import pytest
from openpyxl import Workbook
from sqlalchemy import func, select, text

from app.college_import import ImportRefused, publish_batch, stage_file
from app.core.database import engine
from app.models import College, CollegeStaging, ImportBatch, UpdateHistory
from scripts import seed_content

API = "/api/v1"
HEADERS = ["AISHE Code", "Name of the Institution", "State", "District", "Year of Establishment",
           "Location", "College Type", "Management", "Affiliated University Name", "Affiliated University Type"]


def row(code, name="Test College Alpha", state="Kerala", district="Test District", year=1990):
    return [code, name, state, district, year, "Urban", "Affiliated", "Private Un-Aided", "Test University", "State Public"]


def write_file(tmp_path, rows, name="colleges.xlsx", headers=HEADERS, blank_rows_above=0):
    workbook = Workbook()
    sheet = workbook.active
    for _ in range(blank_rows_above):
        sheet.append(["Directory of colleges"])
    sheet.append(headers)
    for item in rows:
        sheet.append(item)
    path = tmp_path / name
    workbook.save(path)
    return path


@pytest.fixture(autouse=True)
def clean_colleges():
    yield
    with engine.begin() as connection:
        connection.execute(text("truncate colleges, college_staging, import_batches, college_courses, college_facts, branches cascade"))


@pytest.fixture(scope="module", autouse=True)
def catalogue(database):
    seed_content.main()


def publish(db, path, **options):
    batch = stage_file(db, path)
    publish_batch(db, batch, None, **options)
    return batch


def college(db, code):
    db.expire_all()
    return db.scalar(select(College).where(College.aishe_code == code))


# ---------- Import safety ----------

def test_staging_shows_students_nothing(client, db, tmp_path):
    batch = stage_file(db, write_file(tmp_path, [row("C-1")]))
    assert batch.status == "pending" and batch.rows_new == 1
    assert client.get(f"{API}/colleges").json()["total"] == 0


def test_publishing_applies_the_batch_and_clears_staging(client, db, tmp_path):
    publish(db, write_file(tmp_path, [row("C-1"), row("C-2", "Test College Beta")]))
    assert client.get(f"{API}/colleges").json()["total"] == 2
    assert db.scalar(select(func.count()).select_from(CollegeStaging)) == 0
    saved = college(db, "C-1")
    assert saved.source.is_official and saved.last_updated is not None and saved.status == "published"


def test_rejected_batch_changes_nothing(admin_client, client, db, tmp_path):
    batch = stage_file(db, write_file(tmp_path, [row("C-1")]))
    assert admin_client.post(f"{API}/admin/imports/{batch.id}/reject").json()["status"] == "rejected"
    assert client.get(f"{API}/colleges").json()["total"] == 0


def test_repeat_of_the_live_file_is_refused(db, tmp_path):
    path = write_file(tmp_path, [row("C-1")])
    publish_batch(db, stage_file(db, path), None)
    with pytest.raises(ImportRefused, match="already published"):
        stage_file(db, path)


def test_rejected_file_can_be_imported_again(admin_client, db, tmp_path):
    path = write_file(tmp_path, [row("C-1")])
    batch = stage_file(db, path)
    admin_client.post(f"{API}/admin/imports/{batch.id}/reject")
    assert stage_file(db, path).rows_new == 1


def test_small_loss_needs_no_override_but_counts_live_colleges_not_ids(db, tmp_path):
    rows = [row(f"C-{n}") for n in range(20)]
    publish(db, write_file(tmp_path, rows, "first.xlsx"))
    publish(db, write_file(tmp_path, rows[:19], "second.xlsx"))
    publish(db, write_file(tmp_path, rows[:18], "third.xlsx"))
    assert db.scalar(select(func.count()).select_from(College).where(College.status == "published")) == 18


def test_only_one_batch_can_wait_for_review(db, tmp_path):
    stage_file(db, write_file(tmp_path, [row("C-1")], "one.xlsx"))
    with pytest.raises(ImportRefused, match="waiting"):
        stage_file(db, write_file(tmp_path, [row("C-2")], "two.xlsx"))


def test_wrong_file_is_refused(db, tmp_path):
    with pytest.raises(ImportRefused, match="expected columns"):
        stage_file(db, write_file(tmp_path, [["a", "b"]], headers=["Student", "Marks"]))


def test_file_with_no_good_rows_is_refused(db, tmp_path):
    with pytest.raises(ImportRefused, match="No usable rows"):
        stage_file(db, write_file(tmp_path, [row("C-1", state="Atlantis")]))


def test_bad_rows_are_rejected_with_reasons_and_good_rows_kept(db, tmp_path):
    batch = stage_file(db, write_file(tmp_path, [
        row("C-1"), row("C-1", "Duplicate"), row("C-2", state="Atlantis"), row(None), row("C-3", name=None),
    ]))
    assert batch.rows_new == 1 and batch.rows_rejected == 4
    assert any("Atlantis" in problem for problem in batch.problems)
    assert any("twice" in problem for problem in batch.problems)


def test_header_is_found_below_title_rows(db, tmp_path):
    assert stage_file(db, write_file(tmp_path, [row("C-1")], blank_rows_above=3)).rows_new == 1


def test_old_state_names_are_understood(db, tmp_path):
    publish(db, write_file(tmp_path, [
        row("C-1", state="ORISSA"), row("C-2", state="Pondicherry"), row("C-3", state="Andaman & Nicobar Islands"),
    ]))
    assert college(db, "C-1").region.name == "Odisha"
    assert college(db, "C-2").region.name == "Puducherry"
    assert college(db, "C-3").region.name == "Andaman and Nicobar Islands"


def test_impossible_year_is_dropped_not_invented(db, tmp_path):
    publish(db, write_file(tmp_path, [row("C-1", year=3020), row("C-2", year="Not known"), row("C-3", year="1985-86")]))
    assert college(db, "C-1").year_established is None
    assert college(db, "C-2").year_established is None
    assert college(db, "C-3").year_established == 1985


# ---------- Change detection ----------

def test_second_import_reports_real_changes(db, tmp_path):
    publish(db, write_file(tmp_path, [row("C-1"), row("C-2", "Test College Beta")], "first.xlsx"))
    batch = stage_file(db, write_file(tmp_path, [
        row("C-1"), row("C-2", "Test College Beta Renamed"), row("C-3", "Test College Gamma"),
    ], "second.xlsx"))
    assert (batch.rows_new, batch.rows_changed, batch.rows_unchanged, batch.rows_missing) == (1, 1, 1, 0)
    assert college(db, "C-2").name == "Test College Beta"   # nothing changes until it's approved
    publish_batch(db, batch, None)
    assert college(db, "C-2").name == "Test College Beta Renamed"


def test_missing_college_is_marked_outdated_never_deleted(client, db, tmp_path):
    rows = [row(f"C-{n}") for n in range(20)]
    publish(db, write_file(tmp_path, rows, "first.xlsx"))
    publish(db, write_file(tmp_path, rows[:-1], "second.xlsx"))
    assert college(db, "C-19").status == "outdated"
    assert client.get(f"{API}/colleges").json()["total"] == 19


def test_college_that_returns_is_published_again(db, tmp_path):
    rows = [row(f"C-{n}") for n in range(20)]
    publish(db, write_file(tmp_path, rows, "first.xlsx"))
    publish(db, write_file(tmp_path, rows[:-1], "second.xlsx"))
    publish(db, write_file(tmp_path, rows, "third.xlsx"))
    assert college(db, "C-19").status == "published"


def test_suspiciously_short_file_needs_an_override(admin_client, client, db, tmp_path):
    rows = [row(f"C-{n}") for n in range(20)]
    publish(db, write_file(tmp_path, rows, "first.xlsx"))
    batch = stage_file(db, write_file(tmp_path, rows[:5], "second.xlsx"))
    response = admin_client.post(f"{API}/admin/imports/{batch.id}/publish")
    assert response.status_code == 409 and "unusually many" in response.json()["detail"]
    assert client.get(f"{API}/colleges").json()["total"] == 20
    assert admin_client.post(f"{API}/admin/imports/{batch.id}/publish", params={"allow_large_removal": True}).status_code == 200


def test_reimport_keeps_admin_added_details(admin_client, db, tmp_path):
    publish(db, write_file(tmp_path, [row("C-1")], "first.xlsx"))
    saved = college(db, "C-1")
    admin_client.patch(f"{API}/admin/colleges/{saved.id}/website", json={"website": "https://college.example.test/"})
    publish(db, write_file(tmp_path, [row("C-1", "Test College Alpha Renamed")], "second.xlsx"))
    assert college(db, "C-1").website == "https://college.example.test/"


# ---------- Browsing ----------

def fill(db, tmp_path):
    publish(db, write_file(tmp_path, [
        row("C-1", "Test College Alpha", "Kerala", "District One"),
        row("C-2", "Test College Beta", "Kerala", "District Two"),
        row("C-3", "Test College 100% Gamma", "Ladakh", "District Three"),
    ]))


def region_id(client, name):
    return next(r["id"] for r in client.get(f"{API}/reference/states").json() if r["name"] == name)


def test_search_and_filters(client, db, tmp_path):
    fill(db, tmp_path)
    kerala = region_id(client, "Kerala")
    assert client.get(f"{API}/colleges", params={"q": "beta"}).json()["total"] == 1
    assert client.get(f"{API}/colleges", params={"q": "100%"}).json()["total"] == 1
    assert client.get(f"{API}/colleges", params={"q": "%"}).json()["total"] == 1
    assert client.get(f"{API}/colleges", params={"region": kerala}).json()["total"] == 2
    assert client.get(f"{API}/colleges", params={"region": kerala, "district": "District Two"}).json()["total"] == 1
    assert client.get(f"{API}/colleges", params={"management": "Nothing"}).json()["total"] == 0


def test_filters_list_only_real_values(client, db, tmp_path):
    fill(db, tmp_path)
    filters = client.get(f"{API}/colleges/filters", params={"region": region_id(client, "Kerala")}).json()
    assert filters["districts"] == ["District One", "District Two"]
    assert filters["managements"] == ["Private Un-Aided"]


def test_pagination(client, db, tmp_path):
    publish(db, write_file(tmp_path, [row(f"C-{n}", f"Test College {n:02}") for n in range(45)]))
    first = client.get(f"{API}/colleges", params={"size": 20}).json()
    last = client.get(f"{API}/colleges", params={"size": 20, "page": 3}).json()
    assert (first["total"], first["pages"], len(first["colleges"]), len(last["colleges"])) == (45, 3, 20, 5)


def test_unknown_details_stay_empty(client, db, tmp_path):
    fill(db, tmp_path)
    saved = client.get(f"{API}/colleges/{college(db, 'C-1').id}").json()
    assert saved["website"] is None and saved["offerings"] == [] and saved["facts"] == []
    assert saved["source"]["is_official"]


def test_compare(client, db, tmp_path):
    fill(db, tmp_path)
    one, two = college(db, "C-1").id, college(db, "C-2").id
    response = client.get(f"{API}/colleges/compare", params={"ids": f"{two},{one}"})
    assert [item["aishe_code"] for item in response.json()] == ["C-2", "C-1"]
    assert client.get(f"{API}/colleges/compare", params={"ids": str(one)}).status_code == 422
    assert client.get(f"{API}/colleges/compare", params={"ids": f"{one},{one}"}).status_code == 422
    assert client.get(f"{API}/colleges/compare", params={"ids": f"{one},999999"}).status_code == 404
    assert client.get(f"{API}/colleges/compare", params={"ids": "1;drop"}).status_code == 422


# ---------- Sourced details ----------

SOURCED = {"academic_year": "2026-27", "source_name": "College prospectus", "source_url": "https://college.example.test/prospectus"}


def test_offering_needs_a_source_and_year(admin_client, db, tmp_path):
    fill(db, tmp_path)
    target = college(db, "C-1").id
    assert admin_client.post(f"{API}/admin/colleges/{target}/offerings", json={"course_slug": "btech-cse"}).status_code == 422
    bad_year = {**SOURCED, "academic_year": "soon", "course_slug": "btech-cse"}
    assert admin_client.post(f"{API}/admin/colleges/{target}/offerings", json=bad_year).status_code == 422
    bad_url = {**SOURCED, "source_url": "javascript:alert(1)", "course_slug": "btech-cse"}
    assert admin_client.post(f"{API}/admin/colleges/{target}/offerings", json=bad_url).status_code == 422


def test_added_offering_shows_its_source_and_filters_colleges(admin_client, client, db, tmp_path):
    fill(db, tmp_path)
    target = college(db, "C-1").id
    response = admin_client.post(
        f"{API}/admin/colleges/{target}/offerings", json={**SOURCED, "course_slug": "btech-cse", "branch": "AI and Data Science"}
    )
    assert response.status_code == 201
    shown = client.get(f"{API}/colleges/{target}").json()["offerings"][0]
    assert shown["branch"] == "AI and Data Science" and shown["academic_year"] == "2026-27"
    assert shown["source"]["url"] == SOURCED["source_url"]
    assert client.get(f"{API}/colleges", params={"course": "btech-cse"}).json()["total"] == 1


def test_fact_is_recorded_and_can_be_removed(admin_client, client, db, tmp_path):
    fill(db, tmp_path)
    target = college(db, "C-1").id
    fact = admin_client.post(f"{API}/admin/colleges/{target}/facts", json={**SOURCED, "kind": "fees", "value": "Test fee text"}).json()
    assert client.get(f"{API}/colleges/{target}").json()["facts"][0]["value"] == "Test fee text"
    assert db.scalar(select(UpdateHistory).where(UpdateHistory.action == "fact_added")) is not None
    assert admin_client.delete(f"{API}/admin/colleges/facts/{fact['id']}").status_code == 204
    assert client.get(f"{API}/colleges/{target}").json()["facts"] == []


def test_unknown_fact_kind_is_refused(admin_client, db, tmp_path):
    fill(db, tmp_path)
    target = college(db, "C-1").id
    assert admin_client.post(f"{API}/admin/colleges/{target}/facts", json={**SOURCED, "kind": "rumour", "value": "abc"}).status_code == 422


@pytest.mark.parametrize("method,path", [
    ("get", "/admin/imports"), ("post", "/admin/imports/1/publish"), ("post", "/admin/imports/1/reject"),
    ("post", "/admin/colleges/1/offerings"), ("post", "/admin/colleges/1/facts"),
    ("patch", "/admin/colleges/1/website"), ("delete", "/admin/colleges/facts/1"),
])
def test_college_admin_is_admin_only(client, student, method, path):
    assert getattr(client, method)(API + path).status_code == 403


def test_batch_cannot_be_reviewed_twice(admin_client, db, tmp_path):
    batch = publish(db, write_file(tmp_path, [row("C-1")]))
    assert admin_client.post(f"{API}/admin/imports/{batch.id}/reject").status_code == 409


def test_imports_list_shows_counts_and_problems(admin_client, db, tmp_path):
    stage_file(db, write_file(tmp_path, [row("C-1"), row("C-2", state="Atlantis")]))
    listed = admin_client.get(f"{API}/admin/imports").json()[0]
    assert listed["rows_new"] == 1 and listed["rows_rejected"] == 1 and "Atlantis" in listed["problems"][0]


def test_no_real_or_sample_colleges_are_ever_seeded(db):
    assert db.scalar(select(func.count()).select_from(College)) == 0
    assert db.scalar(select(func.count()).select_from(ImportBatch)) == 0

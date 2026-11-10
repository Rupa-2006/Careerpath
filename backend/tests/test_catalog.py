import pytest
from sqlalchemy import select

from app.core.config import get_settings
from app.models import Course, EligibilityCriterion, Field, Source, Stream, UpdateHistory, VerificationRecord
from scripts import content, seed_content

API = "/api/v1"


@pytest.fixture(scope="module", autouse=True)
def catalogue(database):
    seed_content.main()


@pytest.fixture
def show_all(monkeypatch):
    """The labelled development view. Real students only ever get the published view."""
    monkeypatch.setattr(get_settings(), "show_unpublished", True)


def stream_id(db, slug):
    return db.scalar(select(Stream).where(Stream.slug == slug)).id


def region_id(client, name):
    return next(r["id"] for r in client.get(f"{API}/reference/states").json() if r["name"] == name)


def subject_ids(client, *slugs):
    subjects = {s["slug"]: s["id"] for s in client.get(f"{API}/reference/subjects").json()}
    return ",".join(str(subjects[slug]) for slug in slugs)


def eligibility(client, slug, **params):
    return client.get(f"{API}/courses/{slug}", params=params).json()["eligibility"]


# ---------- Publishing gate ----------

def test_students_see_nothing_until_it_is_published(client):
    assert client.get(f"{API}/courses").json()["total"] == 0
    assert client.get(f"{API}/fields").json() == []
    assert client.get(f"{API}/courses/mbbs").status_code == 404
    assert client.get(f"{API}/exams").json() == []


def test_development_view_labels_every_record(client, show_all):
    courses = client.get(f"{API}/courses").json()["courses"]
    assert len(courses) == len(content.COURSES)
    assert {course["status"] for course in courses} == {"pending_verification"}


def test_development_view_can_never_run_in_production(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "show_unpublished", True)
    monkeypatch.setattr(settings, "environment", "production")
    assert settings.visible_statuses == ("published",)


def test_publishing_a_course_shows_it_and_records_who_did_it(admin_client, client, db):
    course = db.scalar(select(Course).where(Course.slug == "ca"))
    response = admin_client.post(f"{API}/admin/review/course/{course.id}", json={"status": "published", "note": "Checked"})
    assert response.status_code == 200
    try:
        assert client.get(f"{API}/courses").json()["total"] == 1
        record = db.scalar(select(VerificationRecord).where(VerificationRecord.entity_id == str(course.id)))
        assert record.status == "published" and record.note == "Checked" and record.reviewer_id is not None
        assert db.scalar(select(UpdateHistory).where(UpdateHistory.action == "status_change")).changes == {
            "status": ["pending_verification", "published"]
        }
    finally:
        admin_client.post(f"{API}/admin/review/course/{course.id}", json={"status": "pending_verification"})


def test_unpublished_rule_is_not_used_even_on_a_published_course(admin_client, client, db):
    course = db.scalar(select(Course).where(Course.slug == "ca"))
    admin_client.post(f"{API}/admin/review/course/{course.id}", json={"status": "published"})
    try:
        assert eligibility(client, "ca")["status"] == "no_rule"
    finally:
        admin_client.post(f"{API}/admin/review/course/{course.id}", json={"status": "pending_verification"})


def test_cannot_publish_without_a_source(admin_client, db):
    field = db.scalar(select(Field).where(Field.slug == "other"))
    source_id = field.source_id
    field.source_id = None
    db.commit()
    try:
        assert admin_client.post(f"{API}/admin/review/field/{field.id}", json={"status": "published"}).status_code == 422
    finally:
        field.source_id = source_id
        db.commit()


def test_review_is_admin_only(client, student):
    assert client.get(f"{API}/admin/review").status_code == 403
    assert client.post(f"{API}/admin/review/course/1", json={"status": "published"}).status_code == 403


def test_review_queue_lists_every_kind_of_record(admin_client):
    entities = {item["entity"] for item in admin_client.get(f"{API}/admin/review").json()}
    assert {"field", "course", "exam", "criterion"} <= entities


def test_unknown_review_target(admin_client):
    assert admin_client.post(f"{API}/admin/review/user/1", json={"status": "published"}).status_code == 404


def test_bad_status_is_refused(admin_client, db):
    course = db.scalar(select(Course).where(Course.slug == "ca"))
    assert admin_client.post(f"{API}/admin/review/course/{course.id}", json={"status": "hacked"}).status_code == 422


# ---------- Eligibility ----------

@pytest.mark.parametrize("stream,course,expected", [
    ("science-maths", "btech-cse", "eligible"),
    ("science-biology", "btech-cse", "not_eligible"),
    ("commerce-maths", "btech-cse", "not_eligible"),
    ("arts", "btech-cse", "not_eligible"),
    ("science-biology", "mbbs", "eligible"),
    ("science-maths", "mbbs", "not_eligible"),
    ("science-both", "mbbs", "eligible"),
    ("science-maths", "bpharm", "eligible"),
    ("science-biology", "bpharm", "eligible"),
    ("commerce", "bpharm", "not_eligible"),
    ("arts", "ca", "eligible"),
    ("science-biology", "ca", "eligible"),
    ("science-maths", "cpl", "eligible"),
    ("science-biology", "cpl", "not_eligible"),
    ("arts", "bsc-hha", "eligible"),
    ("science-maths", "bs-ms", "eligible"),
    ("science-biology", "bs-ms", "eligible"),
    ("commerce-maths", "bs-ms", "not_eligible"),
    ("arts", "nda", "eligible"),
    ("science-maths", "nda", "eligible"),
])
def test_eligibility_by_stream(client, db, show_all, stream, course, expected):
    assert eligibility(client, course, stream=stream_id(db, stream))["status"] == expected


def test_refusal_says_what_is_missing(client, db, show_all):
    result = eligibility(client, "btech-cse", stream=stream_id(db, "science-biology"))
    assert "Mathematics" in result["missing"]


def test_three_of_four_rule(client, show_all):
    assert eligibility(client, "bs-ms", subjects=subject_ids(client, "physics", "chemistry", "biology"))["status"] == "eligible"
    result = eligibility(client, "bs-ms", subjects=subject_ids(client, "physics", "chemistry", "english"))
    assert result["status"] == "not_eligible" and "3 of" in result["missing"][0]


def test_exact_subjects_beat_the_stream(client, db, show_all):
    result = eligibility(
        client, "btech-cse", stream=stream_id(db, "arts"), subjects=subject_ids(client, "physics", "mathematics", "biotechnology")
    )
    assert result["status"] == "eligible"


def test_no_rule_is_never_a_yes(client, db, show_all):
    result = eligibility(client, "bca", stream=stream_id(db, "science-maths"))
    assert result["status"] == "no_rule" and "confirmed rule" in result["message"]


def test_subjects_unknown_asks_instead_of_guessing(client, db, show_all):
    assert eligibility(client, "mbbs")["status"] == "need_subjects"
    assert eligibility(client, "mbbs", stream=stream_id(db, "vocational"))["status"] == "need_subjects"


def test_state_rule_only_applies_in_that_state(client, db, show_all):
    andhra, kerala = region_id(client, "Andhra Pradesh"), region_id(client, "Kerala")
    science = stream_id(db, "science-biology")
    assert eligibility(client, "bsc-agri", stream=science, region=kerala)["status"] == "no_rule"
    assert eligibility(client, "bsc-agri", stream=science, region=andhra)["status"] == "check"


def test_never_promises_admission(client, db, show_all):
    for course in client.get(f"{API}/courses", params={"stream": stream_id(db, "science-both")}).json()["courses"]:
        message = course["eligibility"]["message"].lower()
        assert "guarantee" not in message and "you will get" not in message


def test_open_to_me_filter_hides_only_real_refusals(client, db, show_all):
    arts = stream_id(db, "arts")
    slugs = {c["slug"] for c in client.get(f"{API}/courses", params={"stream": arts, "open_to_me": True}).json()["courses"]}
    assert "btech-cse" not in slugs and "mbbs" not in slugs
    assert {"ca", "ba-llb", "bca"} <= slugs   # bca has no confirmed rule, so it must not be hidden


# ---------- Browsing ----------

def test_every_field_has_a_page_and_an_explanation(client, show_all):
    fields = client.get(f"{API}/fields").json()
    assert len(fields) == 19
    for field in fields:
        detail = client.get(f"{API}/fields/{field['slug']}").json()
        assert detail["what_is_it"] and detail["who_can_choose"] and detail["source"]["url"].startswith("https://")


def test_field_course_counts_are_real(client, show_all):
    counts = {field["slug"]: field["course_count"] for field in client.get(f"{API}/fields").json()}
    assert counts["law"] == 1 and counts["engineering"] == 19 and counts["diploma"] == 1


def test_search_and_filters(client, show_all):
    assert {c["slug"] for c in client.get(f"{API}/courses", params={"q": "pilot"}).json()["courses"]} == {"cpl"}
    assert client.get(f"{API}/courses", params={"q": "%"}).json()["total"] == 0
    assert {c["slug"] for c in client.get(f"{API}/courses", params={"field": "law"}).json()["courses"]} == {"ba-llb"}
    assert {c["slug"] for c in client.get(f"{API}/courses", params={"exam": "neet-ug"}).json()["courses"]} == {"mbbs", "bsc-nursing", "bds", "bams", "bhms", "bums"}


def test_bad_subject_list_is_refused(client, show_all):
    assert client.get(f"{API}/courses", params={"subjects": "1;drop table"}).status_code == 422


def test_course_detail_has_rules_exams_and_sources(client, show_all):
    course = client.get(f"{API}/courses/nda").json()
    assert {rule["label"] for rule in course["criteria"]} == {"Army wing", "Air Force and Naval wings"}
    assert course["exams"][0]["name"] == "NDA and NA Examination"
    assert all(rule["source"]["is_official"] for rule in course["criteria"])


def test_compare_keeps_order_and_needs_two_or_three(client, show_all):
    response = client.get(f"{API}/courses/compare", params={"slugs": "mbbs,bsc-nursing,bpharm"})
    assert [c["slug"] for c in response.json()] == ["mbbs", "bsc-nursing", "bpharm"]
    assert client.get(f"{API}/courses/compare", params={"slugs": "mbbs"}).status_code == 422
    assert client.get(f"{API}/courses/compare", params={"slugs": "mbbs,mbbs"}).status_code == 422
    assert client.get(f"{API}/courses/compare", params={"slugs": "a,b,c,d"}).status_code == 422
    assert client.get(f"{API}/courses/compare", params={"slugs": "mbbs,nothing"}).status_code == 404


# ---------- Content rules ----------

def test_every_record_cites_an_official_source(db):
    assert all(source.is_official and source.url.startswith("https://") for source in db.scalars(select(Source)))
    for model in (Course, Field, EligibilityCriterion):
        assert all(record.source_id for record in db.scalars(select(model)))


def test_seeded_records_are_never_pre_approved():
    assert "published" not in {getattr(rule, "status", None) for rule in content.COURSES}


def test_reseeding_keeps_review_status(admin_client, db):
    course = db.scalar(select(Course).where(Course.slug == "bba"))
    admin_client.post(f"{API}/admin/review/course/{course.id}", json={"status": "verified"})
    seed_content.main()
    seed_content.main(overwrite=True)
    db.expire_all()
    assert db.scalar(select(Course).where(Course.slug == "bba")).status == "verified"
    admin_client.post(f"{API}/admin/review/course/{course.id}", json={"status": "pending_verification"})


def test_overwrite_keeps_a_rule_and_its_status(admin_client, db):
    rule = db.scalar(select(EligibilityCriterion).where(EligibilityCriterion.label == "Army wing"))
    admin_client.post(f"{API}/admin/review/criterion/{rule.id}", json={"status": "verified"})
    seed_content.main(overwrite=True)
    db.expire_all()
    assert db.get(EligibilityCriterion, rule.id).status == "verified"
    admin_client.post(f"{API}/admin/review/criterion/{rule.id}", json={"status": "pending_verification"})

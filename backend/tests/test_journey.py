import itertools
from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.orm import selectinload

from app.api.journey import rank_courses, web_links
from app.core.config import get_settings
from app.core.database import engine
from app.eligibility import check
from app.models import (
    Course,
    EligibilityCriterion,
    EligibilityGroup,
    ImportantDate,
    QuizOption,
    QuizQuestion,
    QuizResult,
    Report,
    Roadmap,
    RoadmapStep,
    Stream,
    TechnologyUpdate,
    Translation,
    UserStepProgress,
)
from scripts import seed_content, seed_journey
from scripts.check_links import classify
from scripts.fetch_updates import parse_feed
from tests.conftest import PASSWORD

API = "/api/v1"
ALL = ("published", "verified", "pending_verification")


@pytest.fixture(scope="module", autouse=True)
def journey(database):
    seed_content.main()
    seed_journey.main()


@pytest.fixture(autouse=True)
def clean_rows():
    yield
    with engine.begin() as connection:
        connection.execute(text("truncate reports"))
        connection.execute(text("delete from technology_updates where not is_tool"))
        connection.execute(text("delete from important_dates where title like 'Test%'"))


@pytest.fixture
def show_all(monkeypatch):
    monkeypatch.setattr(get_settings(), "show_unpublished", True)


def first_step(db, slug="web-developer"):
    roadmap = db.scalar(select(Roadmap).where(Roadmap.slug == slug))
    return db.scalar(select(RoadmapStep).where(RoadmapStep.roadmap_id == roadmap.id).order_by(RoadmapStep.year, RoadmapStep.semester, RoadmapStep.position))


def stream_id(db, slug):
    return db.scalar(select(Stream).where(Stream.slug == slug)).id


# ---------- Roadmaps ----------

def test_roadmaps_wait_for_review(client):
    assert client.get(f"{API}/roadmaps").json() == []
    assert client.get(f"{API}/roadmaps/doctor").status_code == 404


def test_every_course_from_the_first_version_keeps_its_roadmap(client, show_all):
    roadmaps = client.get(f"{API}/roadmaps").json()
    assert len(roadmaps) == 34 and sum(item["step_count"] for item in roadmaps) == 313


def test_roadmap_detail_and_years(client, show_all):
    doctor = client.get(f"{API}/roadmaps/doctor").json()
    assert doctor["years"] == 5 and doctor["uses_semesters"] is False and "mbbs" in doctor["course_slugs"]
    assert doctor["steps"][0]["year"] == 1 and all(step["done"] is False for step in doctor["steps"])


def test_telugu_roadmap_has_no_english_left(client, show_all):
    roadmap = client.get(f"{API}/roadmaps/web-developer", params={"lang": "te"}).json()
    assert "వెబ్" in roadmap["name"]
    for step in roadmap["steps"]:
        for field in ("title", "why", "build_task"):
            assert any("ఀ" <= char <= "౿" for char in step[field]), step[field]


def test_english_is_the_default(client, show_all):
    assert client.get(f"{API}/roadmaps/web-developer").json()["name"].startswith("Web Developer")


def test_unknown_language_is_refused(client, show_all):
    assert client.get(f"{API}/roadmaps", params={"lang": "xx"}).status_code == 422


def test_only_web_links_are_shown():
    assert web_links("https://a.example/\njavascript:alert(1)\n\nhttp://b.example/") == ["https://a.example/", "http://b.example/"]


def test_publish_requires_review_and_records_it(admin_client, client, db):
    roadmap = db.scalar(select(Roadmap).where(Roadmap.slug == "nurse"))
    assert admin_client.post(f"{API}/admin/review/roadmap/{roadmap.id}", json={"status": "published"}).status_code == 200
    assert [item["slug"] for item in client.get(f"{API}/roadmaps").json()] == ["nurse"]
    admin_client.post(f"{API}/admin/review/roadmap/{roadmap.id}", json={"status": "pending_verification"})


# ---------- Progress ----------

def test_progress_needs_login(client, db):
    assert client.put(f"{API}/me/progress/{first_step(db).id}").status_code == 401


def test_mark_and_undo_a_step(client, student, db, show_all):
    step = first_step(db)
    assert client.put(f"{API}/me/progress/{step.id}").status_code == 204
    assert client.put(f"{API}/me/progress/{step.id}").status_code == 204   # pressing twice is harmless
    roadmap = client.get(f"{API}/roadmaps/web-developer").json()
    assert roadmap["done_count"] == 1 and roadmap["next_step_id"] != step.id
    client.delete(f"{API}/me/progress/{step.id}")
    assert client.get(f"{API}/roadmaps/web-developer").json()["done_count"] == 0


def test_unknown_step_is_refused(client, student):
    assert client.put(f"{API}/me/progress/99999999").status_code == 404


def test_my_progress_shows_the_next_step(client, student, db):
    step = first_step(db)
    client.put(f"{API}/me/progress/{step.id}")
    rows = client.get(f"{API}/me/progress").json()
    assert rows[0]["slug"] == "web-developer" and rows[0]["done"] == 1 and rows[0]["next_step"]


def test_one_students_progress_is_private(client, admin_client, student, db, show_all):
    client.put(f"{API}/me/progress/{first_step(db).id}")
    assert admin_client.get(f"{API}/me/progress").json() == []


def test_reloading_content_keeps_progress(client, student, db):
    step = first_step(db)
    client.put(f"{API}/me/progress/{step.id}")
    seed_journey.main()
    db.expire_all()
    assert db.scalar(select(func.count()).select_from(UserStepProgress).where(UserStepProgress.step_id == step.id)) == 1


def test_reloading_keeps_review_status_and_makes_no_duplicates(admin_client, db):
    roadmap = db.scalar(select(Roadmap).where(Roadmap.slug == "advocate"))
    admin_client.post(f"{API}/admin/review/roadmap/{roadmap.id}", json={"status": "verified"})
    before = db.scalar(select(func.count()).select_from(Translation))
    seed_journey.main()
    db.expire_all()
    assert db.scalar(select(Roadmap).where(Roadmap.slug == "advocate")).status == "verified"
    assert db.scalar(select(func.count()).select_from(RoadmapStep)) == 313
    assert db.scalar(select(func.count()).select_from(Translation)) == before
    admin_client.post(f"{API}/admin/review/roadmap/{roadmap.id}", json={"status": "pending_verification"})


def test_deleting_an_account_removes_progress_and_results(client, student, db, show_all):
    client.put(f"{API}/me/progress/{first_step(db).id}")
    question = db.scalar(select(QuizQuestion).options(selectinload(QuizQuestion.options)).order_by(QuizQuestion.position))
    client.post(f"{API}/quiz/score", json={"answers": {str(question.id): question.options[0].id}})
    assert client.request("DELETE", f"{API}/me", json={"password": PASSWORD}).status_code == 204
    db.expire_all()
    assert db.scalar(select(func.count()).select_from(UserStepProgress)) == 0
    assert db.scalar(select(func.count()).select_from(QuizResult)) == 0


# ---------- Quiz ----------

class TestQuiz:
    # (stream, first words of each answer, the course that must come first)
    STUDENTS = [
        ("science-maths", ["Computers", "Building apps", "4 years", "Yes", "We can", "By building"], "btech-cse"),
        ("science-maths", ["Electronics", "Designing electronics", "4 years", "Yes", "We can", "By building"], "btech-ece"),
        ("science-maths", ["Machines", "Designing and building", "4 years", "Yes", "We can", "By building"], "btech-mech"),
        ("science-biology", ["Biology", "Treating", "5 years", "Yes", "We can", "By hands-on"], "mbbs"),
        ("science-biology", ["Biology", "Treating", "4 years", "Yes", "We can", "By hands-on"], "bsc-nursing"),
        ("science-biology", ["Biology", "Working with medicines", "4 years", "Yes", "We can", "By hands-on"], "bpharm"),
        ("commerce", ["Accounts", "Handling", "5 years", "Yes", "Lower", "By working"], "ca"),
        ("arts", ["History", "Law", "5 years", "Yes", "We can", "By reading"], "ba-llb"),
        ("science-maths", ["Drawing", "Designing buildings", "4 years", "Yes", "We can", "By building"], "b-arch"),
        ("arts", ["Drawing", "Creating products", "4 years", "Yes", "We can", "By building"], "b-des"),
        ("arts", ["History", "Hotels", "3 years", "Yes", "We can", "By hands-on"], "bsc-hha"),
        ("science-maths", ["Machines", "Flying", "4 years", "Yes", "We can", "By hands-on"], "cpl"),
    ]

    def questions(self, db):
        return db.scalars(
            select(QuizQuestion).options(selectinload(QuizQuestion.options).selectinload(QuizOption.courses))
            .order_by(QuizQuestion.position)
        ).all()

    def answers(self, db, starts):
        result = {}
        for question, start in zip(self.questions(db), starts):
            result[str(question.id)] = next(o.id for o in question.options if o.text.startswith(start))
        return result

    def test_each_student_gets_the_course_that_fits(self, client, db, show_all):
        for stream, starts, expected in self.STUDENTS:
            response = client.post(f"{API}/quiz/score", json={"answers": self.answers(db, starts), "stream_id": stream_id(db, stream)})
            assert response.json()["results"][0]["slug"] == expected, starts

    def test_every_course_can_reach_the_top_three_for_a_group_that_can_join(self, db):
        """Tries every possible set of answers, so no course is silently unreachable."""
        questions = self.questions(db)
        lists = [[(q.weight, o) for o in q.options] for q in questions]
        courses = db.scalars(select(Course).options(
            selectinload(Course.criteria).selectinload(EligibilityCriterion.regions),
            selectinload(Course.criteria).selectinload(EligibilityCriterion.groups).selectinload(EligibilityGroup.subjects),
        )).all()
        reached = set()
        for stream in db.scalars(select(Stream).options(selectinload(Stream.subjects))).all():
            if not stream.subjects:
                continue
            subjects = {subject.id for subject in stream.subjects}
            allowed = {c.id for c in courses if check(c, subjects, None, ALL).status != "not_eligible"}
            for chosen in itertools.product(*lists):
                reached |= {item["course"].slug for item in rank_courses(chosen, allowed)[:3]}
        assert reached == {course.slug for course in courses}

    def test_group_rules_are_applied(self, client, db, show_all):
        for slug, banned in (("arts", {"btech-cse", "mbbs"}), ("science-biology", {"btech-cse", "cpl"})):
            for option in db.scalars(select(QuizOption).options(selectinload(QuizOption.question))).all():
                data = {"answers": {str(option.question_id): option.id}, "stream_id": stream_id(db, slug)}
                result = client.post(f"{API}/quiz/score", json=data).json()
                shown = {item["slug"] for item in result["results"]} | {item["slug"] for item in result["also"]}
                assert not shown & banned, option.text

    def test_practical_answers_cannot_beat_a_real_interest(self, client, db, show_all):
        answers = self.answers(db, ["Computers", "Building apps", "3 years", "I prefer", "Lower", "By reading"])
        result = client.post(f"{API}/quiz/score", json={"answers": answers, "stream_id": stream_id(db, "science-maths")}).json()
        assert "ba" not in {item["slug"] for item in result["results"]}

    def test_tied_courses_are_not_hidden(self, client, db, show_all):
        first = self.questions(db)[0]
        option = next(o for o in first.options if o.text.startswith("Biology"))
        result = client.post(f"{API}/quiz/score", json={"answers": {str(first.id): option.id}}).json()
        assert len(result["results"]) + len(result["also"]) == len(option.courses)
        assert result["top_tie"] is True

    def test_answer_from_another_question_is_ignored(self, client, db, show_all):
        one, two = self.questions(db)[:2]
        response = client.post(f"{API}/quiz/score", json={"answers": {str(one.id): two.options[0].id}})
        assert response.status_code == 422

    def test_no_answers_is_refused(self, client, show_all):
        assert client.post(f"{API}/quiz/score", json={"answers": {}}).status_code == 422

    def test_unreviewed_courses_never_reach_real_students(self, client, db):
        answers = self.answers(db, ["Computers", "Building apps", "4 years", "Yes", "We can", "By building"])
        assert client.post(f"{API}/quiz/score", json={"answers": answers}).json()["results"] == []

    def test_reasons_and_roadmaps_are_included(self, client, db, show_all):
        answers = self.answers(db, ["Computers", "Building apps", "4 years", "Yes", "We can", "By building"])
        top = client.post(f"{API}/quiz/score", json={"answers": answers}).json()["results"][0]
        assert top["reasons"] and top["roadmaps"]

    def test_telugu_quiz(self, client, db, show_all):
        assert "ఏ" in client.get(f"{API}/quiz", params={"lang": "te"}).json()[0]["text"]
        answers = self.answers(db, ["Computers", "Building apps", "4 years", "Yes", "We can", "By building"])
        top = client.post(f"{API}/quiz/score", params={"lang": "te"}, json={"answers": answers}).json()["results"][0]
        assert any("ఀ" <= char <= "౿" for char in top["reasons"][0])

    def test_every_option_has_telugu(self, db):
        """The site is English only now; options written before that still keep their Telugu."""
        from scripts.stepora.quiz import QUIZ
        translated = sum(1 for question in QUIZ for option in question[3] if option[1])
        count = db.scalar(select(func.count()).select_from(Translation).where(Translation.entity_type == "quiz_option", Translation.language == "te"))
        assert count == translated

    def test_result_is_saved_for_logged_in_students(self, client, student, db, show_all):
        assert client.get(f"{API}/me/quiz-result").json() is None
        answers = self.answers(db, ["Computers", "Building apps", "4 years", "Yes", "We can", "By building"])
        client.post(f"{API}/quiz/score", json={"answers": answers})
        assert client.get(f"{API}/me/quiz-result").json()["results"][0]["slug"]

    def test_saved_result_survives_a_quiz_reload(self, client, student, db, show_all):
        answers = self.answers(db, ["Computers", "Building apps", "4 years", "Yes", "We can", "By building"])
        client.post(f"{API}/quiz/score", json={"answers": answers})
        seed_journey.main()
        assert client.get(f"{API}/me/quiz-result").json()["results"]


# ---------- Exam dates ----------

def add_date(db, days, source_from, **fields):
    today = date.today()
    item = ImportantDate(
        title=fields.pop("title"), certainty="CONFIRMED", starts_on=today + timedelta(days=days),
        checked_on=fields.pop("checked_on", today), status="published", source=source_from.source, **fields,
    )
    db.add(item)
    db.commit()


def test_past_dates_vanish_and_running_exams_stay(client, db):
    existing = db.scalar(select(ImportantDate).limit(1))
    add_date(db, -1, existing, title="Test yesterday")
    add_date(db, 0, existing, title="Test today")
    add_date(db, -3, existing, title="Test running", ends_on=date.today() + timedelta(days=1))
    titles = {item["title"] for item in client.get(f"{API}/dates").json()["upcoming"]}
    assert titles == {"Test today", "Test running"}


def test_old_check_is_flagged(client, db):
    existing = db.scalar(select(ImportantDate).limit(1))
    add_date(db, 5, existing, title="Test stale", checked_on=date.today() - timedelta(days=31))
    assert client.get(f"{API}/dates").json()["upcoming"][0]["recheck_due"] is True


def test_not_announced_exams_have_no_invented_date(client, db, show_all):
    waiting = client.get(f"{API}/dates").json()["waiting"]
    assert {"NEET UG 2027", "AP EAPCET 2027"} <= {item["title"] for item in waiting}
    assert all(item["starts_on"] is None and item["certainty"] == "NOT_ANNOUNCED" for item in waiting)


def test_dates_follow_the_students_group(client, db, show_all):
    arts = client.get(f"{API}/dates", params={"stream": stream_id(db, "arts")}).json()
    assert "NEET UG 2027" not in {item["title"] for item in arts["waiting"]}
    biology = client.get(f"{API}/dates", params={"stream": stream_id(db, "science-biology")}).json()
    assert "NEET UG 2027" in {item["title"] for item in biology["waiting"]}


def test_dates_in_telugu(client, show_all):
    assert "ఇంకా" in client.get(f"{API}/dates", params={"lang": "te"}).json()["waiting"][0]["note"]


def test_course_filter_for_dates(client, show_all):
    titles = {item["title"] for item in client.get(f"{API}/dates", params={"course": "mbbs"}).json()["waiting"]}
    assert titles == {"NEET UG 2027", "Telangana Intermediate public exams 2027"}


# ---------- Reports ----------

def test_report_is_saved_without_personal_details(client, db):
    assert client.post(f"{API}/reports", json={"page": "/courses/mbbs", "message": "Wrong duration"}).status_code == 204
    assert db.scalar(select(Report)).message == "Wrong duration"


def test_robot_field_is_silently_ignored(client, db):
    response = client.post(f"{API}/reports", json={"page": "/x", "message": "Spam here", "website": "http://spam.example"})
    assert response.status_code == 204
    assert db.scalar(select(func.count()).select_from(Report)) == 0


def test_too_many_reports_are_refused(client):
    codes = [client.post(f"{API}/reports", json={"page": "/x", "message": "Wrong fact"}).status_code for _ in range(6)]
    assert codes == [204] * 5 + [429]


def test_report_page_must_be_a_local_path(client):
    assert client.post(f"{API}/reports", json={"page": "https://evil.example", "message": "abc"}).status_code == 422


def test_admin_can_read_and_resolve_reports(admin_client, client):
    client.post(f"{API}/reports", json={"page": "/x", "message": "Wrong fact"})
    report = admin_client.get(f"{API}/admin/reports").json()[0]
    assert admin_client.post(f"{API}/admin/reports/{report['id']}/resolve").json()["resolved"] is True


def test_students_cannot_read_reports(client, student):
    assert client.get(f"{API}/admin/reports").status_code == 403


# ---------- Updates and job sources ----------

def test_old_headlines_are_hidden(client, db):
    now = datetime.now(UTC)
    db.add(TechnologyUpdate(title="Fresh", link="https://a.example/1", source_name="T", published_at=now))
    db.add(TechnologyUpdate(title="Old", link="https://a.example/2", source_name="T", published_at=now - timedelta(days=60)))
    db.commit()
    updates = client.get(f"{API}/updates").json()
    assert [item["title"] for item in updates["latest"]] == ["Fresh"]
    assert len(updates["tools"]) == 2 and updates["last_collected"]


def test_job_sources_link_out_and_invent_nothing(client):
    sources = client.get(f"{API}/opportunities/sources", params={"lang": "te"}).json()
    assert len(sources) == 4 and all(item["url"].startswith("https://") for item in sources)
    assert any("ఀ" <= char <= "౿" for char in sources[0]["description"])


def test_feed_parsing_keeps_only_safe_links():
    rss = b"""<rss version="2.0"><channel>
      <item><title> Good </title><link>https://a.example/1</link><pubDate>Mon, 02 Nov 2026 10:00:00 GMT</pubDate></item>
      <item><title>Unsafe</title><link>javascript:alert(1)</link></item></channel></rss>"""
    items = parse_feed(rss)
    assert [item["link"] for item in items] == ["https://a.example/1"] and items[0]["title"] == "Good"
    atom = b"""<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>A</title>
      <link rel="alternate" href="https://b.example/1"/><updated>2026-11-02T10:00:00Z</updated></entry></feed>"""
    assert parse_feed(atom)[0]["published"].month == 11


def test_link_check_labels():
    assert [classify(code) for code in (200, 403, 404, None)] == ["ok", "blocks robots", "broken", "no answer"]


def test_telugu_for_a_course(client, show_all):
    assert any("ఀ" <= char <= "౿" for char in client.get(f"{API}/courses/mbbs", params={"lang": "te"}).json()["summary"])
    assert client.get(f"{API}/courses/mbbs").json()["roadmaps"][0]["slug"] == "doctor"


def test_no_roadmap_is_thin(client):
    """Each roadmap should guide the student through the whole course, not just a few steps."""
    from scripts.stepora.roadmaps import GOALS
    from scripts.stepora.roadmaps_more import MORE_GOALS
    from scripts.stepora.roadmaps_path import PATH_GOALS
    from scripts.stepora.roadmaps_path2 import MORE_PATH_GOALS
    import scripts.seed_journey  # noqa: F401  (adds the extra steps)
    for goal in GOALS + MORE_GOALS + PATH_GOALS + MORE_PATH_GOALS:
        assert len(goal["steps"]) >= 7, goal["slug"]
        places = [(s[0], s[1], s[2]) for s in goal["steps"]]
        assert len(places) == len(set(places)), goal["slug"]

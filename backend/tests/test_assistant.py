import json
from datetime import date, timedelta

import pytest
from sqlalchemy import select

from app import assistant_ai
from app.core.config import get_settings
from app.models import Course, ImportantDate, Stream, Subject
from scripts import seed_content, seed_journey, seed_skills

API = "/api/v1"
URL = f"{API}/assistant/messages"


@pytest.fixture(scope="module", autouse=True)
def content(database):
    seed_content.main()
    seed_journey.main()
    seed_skills.main()


@pytest.fixture
def show_all(monkeypatch):
    monkeypatch.setattr(get_settings(), "show_unpublished", True)


@pytest.fixture
def ai_on(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "assistant_ai", True)
    monkeypatch.setattr(settings, "gemini_api_key", "test-key")


def ask(client, message, **extra):
    response = client.post(URL, json={"message": message, **extra})
    assert response.status_code == 200, response.text
    return response.json()


def subjects(db, *slugs):
    return [db.scalar(select(Subject.id).where(Subject.slug == slug)) for slug in slugs]


def stream_id(db, slug):
    return db.scalar(select(Stream.id).where(Stream.slug == slug))


def titles(reply, kind="course"):
    return [card["title"] for card in reply["cards"] if card["kind"] == kind]


def test_no_login_is_needed_and_unreviewed_records_stay_hidden(client):
    reply = ask(client, "I like coding")
    assert reply["intent"] == "no_data" and reply["cards"] == []
    assert "reviewing" in reply["text"]


def test_published_records_are_the_only_ones_used(admin_client, client, db):
    course = db.scalar(select(Course).where(Course.slug == "bca"))
    assert admin_client.post(f"{API}/admin/review/course/{course.id}", json={"status": "published"}).status_code == 200
    assert titles(ask(client, "I like coding")) == [course.name]
    admin_client.post(f"{API}/admin/review/course/{course.id}", json={"status": "pending_verification"})


def test_interest_gives_several_options_with_reasons(client, show_all):
    reply = ask(client, "I like coding")
    assert reply["intent"] == "options" and len(titles(reply)) >= 2
    assert all("coding" in card["why"] for card in reply["cards"])
    assert all(card["source"]["url"].startswith("https://") for card in reply["cards"])
    assert "aren't in order" in reply["text"]


def test_never_suggests_a_path_the_subjects_rule_out(client, db, show_all):
    arts = subjects(db, "history", "political-science", "english")
    reply = ask(client, "I like computers", subject_ids=arts)
    assert all(card["eligibility"]["status"] != "not_eligible" for card in reply["cards"])
    assert not any(title.startswith("B.Tech") for title in titles(reply))
    assert "I left out" in reply["text"]


def test_a_wide_question_without_subjects_asks_for_them(client, show_all):
    reply = ask(client, "What can I do after Class 12?")
    assert reply["intent"] == "ask_background" and reply["next_questions"]


def test_a_wide_question_with_subjects_covers_different_fields(client, db, show_all):
    reply = ask(client, "What can I do after Class 12?", stream_id=stream_id(db, "science-maths"))
    assert len(reply["cards"]) >= 4
    assert len({card["why"] for card in reply["cards"]}) >= 3


def test_course_question_uses_the_real_rule(client, db, show_all):
    reply = ask(client, "Can I do MBBS?", subject_ids=subjects(db, "mathematics", "physics", "chemistry"))
    assert reply["intent"] == "course"
    assert reply["cards"][0]["eligibility"]["status"] == "not_eligible"
    assert "Biology" in reply["text"]


def test_a_course_answer_shows_another_path_too(client, show_all):
    assert len(ask(client, "Tell me about BCA")["cards"]) >= 2


def test_btech_spelled_differently_is_understood(client, show_all):
    for spelling in ("cse", "B.Tech CSE", "btech cse"):
        assert titles(ask(client, f"tell me about {spelling}"))[0].startswith("B.Tech Computer")


def test_comparing_never_picks_a_winner(client, show_all):
    reply = ask(client, "BCA vs B.Sc Computer Science")
    assert reply["intent"] == "compare" and len(reply["cards"]) == 2
    assert "won't pick" in reply["text"]


def test_courses_are_ordered_by_what_the_student_said(client, show_all):
    reply = ask(client, "I like coding and maths")
    assert "maths and math" not in reply["text"] and "coding and math" in reply["text"]
    assert "Commerce" not in reply["cards"][0]["why"]
    assert next(card for card in reply["cards"] if "Commerce" in card["why"])["why"].startswith("You mentioned math,")


def test_comparing_two_fields_covers_both_and_picks_neither(client, show_all):
    reply = ask(client, "Which is best, engineering or medical?")
    assert reply["intent"] == "compare" and "won't pick" in reply["text"]
    assert {card["to"] for card in reply["cards"]} == {"/explore/engineering", "/explore/medical"}


def test_a_named_exam_shows_its_own_date_only(client, show_all):
    assert all("NEET" in title for title in titles(ask(client, "When is NEET UG?"), "date"))


def test_a_worried_student_gets_kindness_not_a_refusal(client, show_all):
    reply = ask(client, "I am scared of failing")
    assert "normal to feel unsure" in reply["text"] and "14416" in reply["text"]
    assert "I don't have a checked answer" not in reply["text"]


def test_helping_people_includes_healthcare(client, show_all):
    assert any("Medical" in card["why"] for card in ask(client, "I like helping people")["cards"])


def test_exam_question(client, show_all):
    reply = ask(client, "What is JEE Main?")
    assert reply["intent"] == "exam" and reply["cards"][0]["kind"] == "exam"
    assert "National Testing Agency" in reply["text"]


def test_field_question_explains_an_unfamiliar_field(client, show_all):
    reply = ask(client, "What is aviation?")
    assert reply["intent"] == "field" and reply["cards"][0]["to"] == "/explore/aviation"


def test_roadmap_and_skills(client, show_all):
    assert ask(client, "How do I become a nurse roadmap")["cards"]
    assert all(card["kind"] == "skill" for card in ask(client, "what skills should I learn")["cards"])


def test_past_dates_are_never_offered_but_future_ones_are(client, db, show_all):
    day = timedelta(days=30)
    past = ImportantDate(title="Old test date", certainty="CONFIRMED", starts_on=date.today() - day, checked_on=date.today(), status="published")
    ahead = ImportantDate(title="New test date", certainty="CONFIRMED", starts_on=date.today() + day, checked_on=date.today(), status="published")
    db.add_all([past, ahead])
    db.commit()
    found = titles(ask(client, "When are the exams?"), "date")
    db.delete(past)
    db.delete(ahead)
    db.commit()
    assert "Old test date" not in found and "New test date" in found


@pytest.mark.parametrize("question", ["Will I definitely get a job after BCA?", "Is a seat guaranteed?"])
def test_never_promises(client, show_all, question):
    assert "Nobody can promise" in ask(client, question)["text"]


@pytest.mark.parametrize("question,words", [
    ("What is the salary after BCA?", "salary figures"),
    ("What are the fees for MBBS?", "fee"),
    ("What rank do I need for CSE?", "cutoffs"),
    ("Which college has the best placement?", "rank colleges"),
])
def test_admits_what_it_does_not_know(client, show_all, question, words):
    assert words in ask(client, question)["text"]


def test_unknown_question_says_so(client, show_all):
    reply = ask(client, "Who won the cricket match?")
    assert reply["intent"] == "unknown" and "won't guess" in reply["text"] and reply["cards"] == []


@pytest.mark.parametrize("question", ["I failed and I want to die", "thinking about suicide", "ఆత్మహత్య"])
def test_distress_gets_the_helpline_and_no_ai(client, show_all, ai_on, monkeypatch, question):
    monkeypatch.setattr(assistant_ai, "ask_gemini", lambda *args: pytest.fail("must not reach the AI"))
    reply = ask(client, question)
    assert reply["intent"] == "crisis" and "14416" in reply["text"] and reply["cards"] == []


def test_empty_and_long_messages_are_refused(client):
    assert client.post(URL, json={"message": "   "}).status_code == 422
    assert client.post(URL, json={"message": "x" * 501}).status_code == 422


def test_forged_requests_are_blocked(client):
    assert client.post(URL, json={"message": "hi"}, headers={"X-CareerPath-Client": "web", "Origin": "https://evil.example"}).status_code == 403


def test_too_many_questions_are_slowed_down(client, monkeypatch):
    from app.api import assistant as route
    monkeypatch.setattr(route, "MESSAGES_PER_HOUR", 2)
    assert [client.post(URL, json={"message": "hi"}).status_code for _ in range(3)] == [200, 200, 429]


def test_nothing_typed_is_saved(client, db, show_all):
    from sqlalchemy import text
    ask(client, "my secret-phrase-123 question")
    tables = db.execute(text("select tablename from pg_tables where schemaname='public'")).scalars().all()
    assert not [name for name in tables if "assistant" in name or "chat" in name]


# ---------- The optional AI wording ----------

def test_ai_is_off_unless_turned_on(client, show_all, monkeypatch):
    monkeypatch.setattr(assistant_ai, "ask_gemini", lambda *args: pytest.fail("must not reach the AI"))
    assert ask(client, "I like coding")["used_ai"] is False


def test_ai_can_never_run_in_production(ai_on, monkeypatch):
    settings = get_settings()
    assert settings.assistant_ai_on
    monkeypatch.setattr(settings, "environment", "production")
    assert not settings.assistant_ai_on


def test_ai_rewords_but_cards_stay_from_the_database(client, show_all, ai_on, monkeypatch):
    plain = ask(client, "I like coding")
    monkeypatch.setattr(assistant_ai, "ask_gemini", lambda *args: "Coding is a great thing to enjoy. Look at these paths.")
    reply = ask(client, "I like coding")
    assert reply["used_ai"] is True and reply["text"].startswith("Coding is")
    assert reply["cards"] == plain["cards"]


@pytest.mark.parametrize("bad", [
    "These colleges take 95 percent and above.",
    "You will get a job, guaranteed.",
    "Visit https://fake.example for details.",
    "",
    None,
])
def test_unsafe_ai_wording_is_thrown_away(client, show_all, ai_on, monkeypatch, bad):
    monkeypatch.setattr(assistant_ai, "ask_gemini", lambda *args: bad)
    reply = ask(client, "I like coding")
    assert reply["used_ai"] is False and "aren't in order" in reply["text"]


def test_ai_failure_still_answers(client, show_all, ai_on, monkeypatch):
    def broken(*args, **kwargs):
        raise TimeoutError
    monkeypatch.setattr(assistant_ai.urllib.request, "urlopen", broken)
    reply = ask(client, "I like coding")
    assert reply["used_ai"] is False and reply["cards"]


def test_request_keeps_key_in_a_header_and_personal_details_out(ai_on, monkeypatch):
    seen = {}

    class Answer:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, *args):
            return json.dumps({"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}).encode()

    def fake(request, timeout):
        seen.update(url=request.full_url, key=request.get_header("X-goog-api-key"), body=request.data.decode())
        return Answer()

    monkeypatch.setattr(assistant_ai.urllib.request, "urlopen", fake)
    assert assistant_ai.ask_gemini("I am asha@example.com, phone 98765 43210", "facts") == "ok"
    assert seen["key"] == "test-key" and "test-key" not in seen["url"]
    assert "asha@example.com" not in seen["body"] and "98765" not in seen["body"]
    assert get_settings().gemini_model in seen["url"]


# ---------- Andhra Pradesh and Telangana ----------

def region_id(client, name):
    return next(row["id"] for row in client.get(f"{API}/reference/states").json() if row["name"] == name)


def test_each_student_sees_their_own_state_exam(client, db, show_all):
    mpc = stream_id(db, "science-maths")
    telangana = ask(client, "Tell me about B.Tech CSE", stream_id=mpc, region_id=region_id(client, "Telangana"))
    andhra = ask(client, "Tell me about B.Tech CSE", stream_id=mpc, region_id=region_id(client, "Andhra Pradesh"))
    assert "TG EAPCET" in telangana["text"] and "AP EAPCET" not in telangana["text"]
    assert "AP EAPCET" in andhra["text"] and "TG EAPCET" not in andhra["text"]


def test_eamcet_finds_the_students_own_state_exam(client, show_all):
    reply = ask(client, "What is EAMCET?", region_id=region_id(client, "Telangana"))
    assert reply["intent"] == "exam" and reply["cards"][0]["title"] == "TG EAPCET"


def test_telangana_rules_apply_only_in_telangana(client, db, show_all):
    telangana, andhra = region_id(client, "Telangana"), region_id(client, "Andhra Pradesh")
    labels = [rule["label"] for rule in client.get(f"{API}/courses/btech-cse").json()["criteria"]]
    assert "Telangana (TG EAPCET 2026)" in labels
    bipc = ",".join(str(item) for item in subjects(db, "physics", "chemistry", "biology"))
    for region in (telangana, andhra):
        found = client.get(f"{API}/courses/bsc-agri", params={"region": region, "subjects": bipc}).json()
        assert found["eligibility"]["status"] == "check"
    nursing = client.get(f"{API}/courses/bsc-nursing", params={"region": telangana, "subjects": bipc}).json()
    assert nursing["eligibility"]["status"] == "eligible"


def test_new_telangana_records_wait_for_review(client):
    assert not [exam for exam in client.get(f"{API}/exams").json() if exam["slug"].startswith("tg-")]


def test_telangana_dates_are_not_invented(db):
    rows = db.scalars(select(ImportantDate).where(ImportantDate.title.in_(["TG EAPCET 2027", "TG LAWCET 2027", "Telangana Intermediate public exams 2027"]))).all()
    assert len(rows) == 3 and all(row.certainty == "NOT_ANNOUNCED" and row.starts_on is None for row in rows)


def test_students_can_name_a_career_in_their_own_words(client, show_all):
    assert ask(client, "I want to become a hacker")["cards"][0]["title"] == "Cyber Security Analyst"
    assert ask(client, "I want to work in AI")["cards"][0]["title"] == "AI Engineer"


def test_not_wanted_is_respected(client, show_all):
    reply = ask(client, "I like biology but not doctor")
    titles_seen = titles(reply)
    assert titles_seen and "MBBS" not in titles_seen and "Doctor (MBBS)" not in titles_seen


def test_a_hard_subject_leads_to_other_strengths(client, show_all):
    reply = ask(client, "I failed in maths")
    assert reply["cards"] and all("B.Tech" not in card["title"] for card in reply["cards"])


def test_own_interest_comes_before_what_others_want(client, show_all):
    reply = ask(client, "my parents want me to do engineering but I like drawing")
    assert any("Des" in card["title"] or "Fine Arts" in card["title"] or "Arch" in card["title"] for card in reply["cards"])


@pytest.fixture
def local_ai(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "assistant_ai", True)
    monkeypatch.setattr(settings, "assistant_ai_provider", "local")
    monkeypatch.setattr(settings, "gemini_api_key", "")


def test_local_ai_needs_no_key_and_never_calls_gemini(client, show_all, local_ai, monkeypatch):
    monkeypatch.setattr(assistant_ai, "ask_gemini", lambda *args: pytest.fail("must not reach Gemini"))
    monkeypatch.setattr(assistant_ai, "ask_local", lambda *args, **kwargs: "Coding is a great thing to enjoy. Look at these paths.")
    reply = ask(client, "I like coding")
    assert reply["used_ai"] is True and reply["cards"]


def test_local_ai_wording_is_checked_too(client, show_all, local_ai, monkeypatch):
    monkeypatch.setattr(assistant_ai, "ask_local", lambda *args, **kwargs: "You will get a job, guaranteed.")
    assert ask(client, "I like coding")["used_ai"] is False


def test_local_ai_switched_off_still_answers(client, show_all, local_ai, monkeypatch):
    def refused(*args, **kwargs):
        raise assistant_ai.urllib.error.URLError("Ollama is not running")
    monkeypatch.setattr(assistant_ai.urllib.request, "urlopen", refused)
    reply = ask(client, "I like coding")
    assert reply["used_ai"] is False and reply["cards"]



def test_local_ai_only_adds_a_short_opening_and_keeps_our_answer(client, show_all, local_ai, monkeypatch):
    monkeypatch.setattr(assistant_ai, "ask_local", lambda *args, **kwargs: None)
    plain = ask(client, "I like coding")
    monkeypatch.setattr(assistant_ai, "ask_local", lambda *args, **kwargs: "It's great that you enjoy coding.")
    reply = ask(client, "I like coding")
    assert reply["text"] == "It's great that you enjoy coding.\n\n" + plain["text"]
    monkeypatch.setattr(assistant_ai, "ask_local", lambda *args, **kwargs: "word " * 60)
    assert ask(client, "I like coding")["used_ai"] is False

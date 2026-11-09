import pytest
from sqlalchemy import func, select

from app.core.config import get_settings
from app.models import Skill, Source, Translation, UserSkill
from scripts import seed_content, seed_journey, seed_skills
from scripts.skills_content import CATEGORIES, SKILLS
from tests.conftest import PASSWORD

API = "/api/v1"


@pytest.fixture(scope="module", autouse=True)
def content(database):
    seed_content.main()
    seed_journey.main()
    seed_skills.main()


@pytest.fixture
def show_all(monkeypatch):
    monkeypatch.setattr(get_settings(), "show_unpublished", True)


def skill(db, slug="resume"):
    return db.scalar(select(Skill).where(Skill.slug == slug))


def test_skills_wait_for_review(client):
    assert client.get(f"{API}/skills").json() == []


def test_publishing_a_skill_shows_it(admin_client, client, db):
    item = skill(db)
    assert admin_client.post(f"{API}/admin/review/skill/{item.id}", json={"status": "published"}).status_code == 200
    assert [row["slug"] for row in client.get(f"{API}/skills").json()] == ["resume"]
    admin_client.post(f"{API}/admin/review/skill/{item.id}", json={"status": "pending_verification"})


def test_every_category_from_the_brief_has_skills(client, show_all):
    found = {row["category"] for row in client.get(f"{API}/skills").json()}
    assert found == set(CATEGORIES)


def test_every_skill_has_a_project_a_link_and_a_source(client, show_all):
    for row in client.get(f"{API}/skills").json():
        assert row["project"] and row["why"] and row["source"]["url"].startswith("https://")
        assert row["resources"] and all(link["url"].startswith("https://") for link in row["resources"])


def test_filter_by_category(client, show_all):
    rows = client.get(f"{API}/skills", params={"category": "aptitude"}).json()
    assert {row["slug"] for row in rows} == {s[0] for s in SKILLS if s[1] == "aptitude"}
    assert {"quantitative-aptitude", "logical-reasoning"} <= {row["slug"] for row in rows}


def test_career_filter_keeps_general_skills_and_drops_other_careers(client, show_all):
    slugs = {row["slug"] for row in client.get(f"{API}/skills", params={"roadmap": "nurse"}).json()}
    assert "health-safety" in slugs and "resume" in slugs
    assert "python-basics" not in slugs and "cad-drawing" not in slugs


def test_every_roadmap_has_a_skill_of_its_own(client, show_all):
    general = {row["slug"] for row in client.get(f"{API}/skills").json() if row["for_all"]}
    for roadmap in client.get(f"{API}/roadmaps").json():
        slugs = {row["slug"] for row in client.get(f"{API}/skills", params={"roadmap": roadmap["slug"]}).json()}
        assert slugs - general, roadmap["slug"]


TRANSLATED = {s[0] for s in SKILLS if s[3]}   # the site is English only now; newer skills have no Telugu


def test_telugu_has_no_english_left(client, show_all):
    for row in client.get(f"{API}/skills", params={"lang": "te"}).json():
        if row["slug"] not in TRANSLATED:
            continue
        for field in ("why", "project"):   # names such as "Git, GitHub" are products and stay as they are
            assert any("ఀ" <= char <= "౿" for char in row[field]), row[field]


def test_every_skill_is_translated(db):
    count = db.scalar(select(func.count()).select_from(Translation).where(Translation.entity_type == "skill"))
    assert count == len(TRANSLATED) * 3


def test_tracking_needs_login(client, db):
    assert client.put(f"{API}/me/skills/{skill(db).id}", json={"state": "done"}).status_code == 401


def test_mark_learning_then_done_then_clear(client, student, db, show_all):
    item = skill(db)
    state = lambda: next(row["state"] for row in client.get(f"{API}/skills").json() if row["id"] == item.id)
    assert state() is None
    assert client.put(f"{API}/me/skills/{item.id}", json={"state": "learning"}).status_code == 204
    assert state() == "learning"
    client.put(f"{API}/me/skills/{item.id}", json={"state": "done"})
    assert state() == "done"
    assert db.scalar(select(func.count()).select_from(UserSkill)) == 1
    client.delete(f"{API}/me/skills/{item.id}")
    assert state() is None


def test_bad_state_is_refused(client, student, db):
    assert client.put(f"{API}/me/skills/{skill(db).id}", json={"state": "expert"}).status_code == 422


def test_unknown_skill_is_refused(client, student):
    assert client.put(f"{API}/me/skills/99999999", json={"state": "done"}).status_code == 404


def test_one_students_checklist_is_private(client, admin_client, student, db, show_all):
    item = skill(db)
    client.put(f"{API}/me/skills/{item.id}", json={"state": "done"})
    assert next(row["state"] for row in admin_client.get(f"{API}/skills").json() if row["id"] == item.id) is None


def test_reloading_keeps_ticks_and_review_status(admin_client, client, student, db):
    item = skill(db)
    client.put(f"{API}/me/skills/{item.id}", json={"state": "done"})
    admin_client.post(f"{API}/admin/review/skill/{item.id}", json={"status": "verified"})
    seed_skills.main()
    db.expire_all()
    assert skill(db).status == "verified"
    assert db.scalar(select(func.count()).select_from(UserSkill).where(UserSkill.skill_id == item.id)) == 1
    assert db.scalar(select(func.count()).select_from(Skill)) == len(SKILLS)
    admin_client.post(f"{API}/admin/review/skill/{item.id}", json={"status": "pending_verification"})


def test_deleting_an_account_removes_the_checklist(client, student, db):
    client.put(f"{API}/me/skills/{skill(db).id}", json={"state": "done"})
    assert client.request("DELETE", f"{API}/me", json={"password": PASSWORD}).status_code == 204
    db.expire_all()
    assert db.scalar(select(func.count()).select_from(UserSkill)) == 0


def test_all_sources_are_marked_official(db):
    assert all(source.is_official for source in db.scalars(select(Source)))

from datetime import UTC, datetime

import pytest
from sqlalchemy import delete, select

from app.core.config import get_settings
from app.models import Roadmap, TechnologyUpdate
from scripts import seed_content, seed_journey, seed_opportunities
from scripts.fetch_updates import FEEDS
from app.career_growth import CAREER_GROWTH
from scripts.opportunities_content import OPPORTUNITIES

API = "/api/v1"


@pytest.fixture(scope="module", autouse=True)
def content(database):
    seed_content.main()
    seed_journey.main()
    seed_opportunities.main()


@pytest.fixture
def show_all(monkeypatch):
    monkeypatch.setattr(get_settings(), "show_unpublished", True)


def test_every_roadmap_says_what_comes_after_it(db):
    assert {item.slug for item in db.scalars(select(Roadmap))} == set(OPPORTUNITIES)


def test_students_see_nothing_until_published(client):
    assert client.get(f"{API}/career-opportunities", params={"roadmap": "doctor"}).json() == []


def test_each_career_gets_its_own_next_steps(client, show_all):
    rows = client.get(f"{API}/career-opportunities", params={"roadmap": "doctor"}).json()
    assert [row["kind"] for row in rows] == ["jobs", "internship", "study", "government", "own"]
    assert any("NEET PG" in row["detail"] for row in rows)
    assert all(row["url"].startswith("https://") for row in rows)


def test_no_opportunity_promises_a_salary_or_job():
    text = " ".join(" ".join(item) for item in OPPORTUNITIES.values()).lower()
    assert "salary" not in text and "guarantee" not in text and "lakh" not in text


def test_every_feed_names_real_careers():
    assert {career for _, _, careers in FEEDS for career in careers} <= set(OPPORTUNITIES)


def test_news_reaches_only_the_matching_career(client, db):
    db.add(TechnologyUpdate(title="Health news", link="https://example.test/n1", source_name="WHO", careers=["doctor"], published_at=datetime.now(UTC)))
    db.commit()
    assert [row["title"] for row in client.get(f"{API}/updates/career", params={"roadmap": "doctor"}).json()] == ["Health news"]
    assert client.get(f"{API}/updates/career", params={"roadmap": "pilot"}).json() == []
    db.execute(delete(TechnologyUpdate).where(TechnologyUpdate.link == "https://example.test/n1"))
    db.commit()


def test_shared_careers_fit_each_course(client, show_all):
    bca = client.get(f"{API}/courses/bca").json()
    btech = client.get(f"{API}/courses/btech-cse").json()
    assert bca["path_years"] == 3 and "3-year" in bca["path_note"]
    assert btech["path_years"] is None and btech["path_note"]


def test_every_career_shows_how_people_grow(db):
    assert set(CAREER_GROWTH) == {item.slug for item in db.scalars(select(Roadmap))}


def test_growth_reaches_the_page_without_promises(client):
    row = client.get(f"{API}/career-growth", params={"roadmap": "cyber-security-analyst"}).json()
    assert row["first"] == "SOC Analyst" and len(row["ready"]) == 4
    assert client.get(f"{API}/career-growth", params={"roadmap": "unknown"}).json() is None
    text = str(CAREER_GROWTH).lower()
    assert "salary" not in text and "guarantee" not in text

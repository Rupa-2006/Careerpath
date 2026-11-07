import pytest

from app.core.config import get_settings
from scripts import seed_content, seed_journey, seed_tech_changes
from scripts.content import SOURCES
from scripts.tech_changes_content import TECH_CHANGES

URL = "/api/v1/technology-changes"
LEVELS = {"essential", "emerging", "optional", "outdated"}


@pytest.fixture(scope="module", autouse=True)
def content(database):
    seed_content.main()
    seed_journey.main()
    seed_tech_changes.main()


@pytest.fixture
def show_all(monkeypatch):
    monkeypatch.setattr(get_settings(), "show_unpublished", True)


def test_every_change_has_evidence_and_a_level():
    for _, _, level, what, why, learn, source, roadmaps in TECH_CHANGES:
        assert level in LEVELS and what and why and learn and roadmaps and source in SOURCES


def test_students_see_nothing_until_published(client):
    assert client.get(URL).json() == []


def test_list_shows_with_a_source(client, show_all):
    rows = client.get(URL).json()
    assert len(rows) == len(TECH_CHANGES)
    assert all(row["source"]["url"] for row in rows)


def test_a_change_reaches_only_the_careers_it_affects(client, show_all):
    cyber = {row["slug"] for row in client.get(URL, params={"roadmap": "cyber-security-analyst"}).json()}
    assert cyber == {"owasp-top-10-2025", "post-quantum-cryptography"}
    assert client.get(URL, params={"roadmap": "pilot"}).json() == []

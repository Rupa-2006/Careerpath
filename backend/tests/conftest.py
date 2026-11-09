"""Tests run against a real, temporary PostgreSQL server, never the development database."""
import os
import tempfile

import pgserver

_server = pgserver.get_server(tempfile.mkdtemp(), cleanup_mode="delete")
os.environ["DATABASE_URL"] = _server.get_uri().replace("postgresql://", "postgresql+psycopg://")
os.environ["ENVIRONMENT"] = "development"
os.environ["SHOW_UNPUBLISHED"] = "false"   # tests see what a real student sees

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.core.config import BACKEND_DIR  # noqa: E402
from app.core.database import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Roadmap, User  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from scripts import seed_reference  # noqa: E402

PASSWORD = "Tall-River-Lamp-42"


@pytest.fixture(scope="session", autouse=True)
def database():
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    command.upgrade(config, "head")
    seed_reference.main()
    yield
    engine.dispose()
    _server.cleanup()


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    with engine.begin() as connection:
        connection.execute(text("truncate users, sessions, rate_limit_events, update_history, verification_records cascade"))


@pytest.fixture
def client():
    with TestClient(app, headers={"X-CareerPath-Client": "web"}) as test_client:
        yield test_client


@pytest.fixture
def db():
    with SessionLocal() as session:
        yield session


@pytest.fixture
def career():
    """Sign-up needs a career path. Adds one for the test only if the test hasn't loaded the real roadmaps."""
    with SessionLocal() as session:
        made = session.scalar(text("select 1 from roadmaps where slug = 'web-developer'")) is None
        if made:
            session.add(Roadmap(slug="web-developer", name="Web Developer", description="Test career", status="published"))
            session.commit()
    yield
    if made:
        with engine.begin() as connection:
            connection.execute(text("delete from roadmaps where slug = 'web-developer'"))


@pytest.fixture
def student(client, career):
    response = client.post("/api/v1/auth/register", json={"email": "asha@example.com", "password": PASSWORD, "path": "web-developer"})
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def admin_client(db):
    db.add(User(email="admin@example.com", password_hash=hash_password(PASSWORD), role="admin"))
    db.commit()
    with TestClient(app, headers={"X-CareerPath-Client": "web"}) as test_client:
        assert test_client.post(
            "/api/v1/auth/login", json={"email": "admin@example.com", "password": PASSWORD}
        ).status_code == 200
        yield test_client


@pytest.fixture(autouse=True)
def no_ai_unless_a_test_asks(monkeypatch):
    """Tests never use the developer's own AI settings from .env."""
    from app.core.config import get_settings
    settings = get_settings()
    monkeypatch.setattr(settings, "assistant_ai", False)
    monkeypatch.setattr(settings, "assistant_ai_provider", "gemini")

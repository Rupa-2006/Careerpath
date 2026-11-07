from alembic import context
from sqlalchemy import create_engine

from app import models  # noqa: F401  (loads every table)
from app.core.config import get_settings
from app.core.database import Base


def run_migrations() -> None:
    engine = create_engine(get_settings().database_url)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


run_migrations()

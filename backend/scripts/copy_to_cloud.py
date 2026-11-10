"""
Copies every table from this computer's database to another database, such as the online Neon one.
Run:  CLOUD_DATABASE_URL=... python -m scripts.copy_to_cloud
The cloud database must already have the tables (run `alembic upgrade head` against it first) and be empty.
The connection link is read from an environment variable, so it never appears in a file or the screen.
"""
import os
import sys

import psycopg
from sqlalchemy import Integer

from app.core.config import get_settings
from app.models import Base


def plain(url: str) -> str:
    return url.replace("postgresql+psycopg://", "postgresql://", 1)


def main() -> None:
    target = os.environ.get("CLOUD_DATABASE_URL")
    if not target:
        sys.exit("Set CLOUD_DATABASE_URL first.")
    tables = [table for table in Base.metadata.sorted_tables]   # parents before children
    with psycopg.connect(plain(get_settings().database_url)) as source, psycopg.connect(plain(target)) as cloud:
        with cloud.cursor() as cur:
            cur.execute("TRUNCATE " + ", ".join(f'"{t.name}"' for t in tables) + " CASCADE")
        for table in tables:
            columns = ", ".join(f'"{c.name}"' for c in table.columns)
            copied = 0
            with source.cursor().copy(f'COPY "{table.name}" ({columns}) TO STDOUT') as out, \
                    cloud.cursor().copy(f'COPY "{table.name}" ({columns}) FROM STDIN') as into:
                for block in out:
                    into.write(block)
                    copied += 1
            # Keep id counters in step, so new rows online don't clash with copied ones
            for column in table.columns:
                if column.primary_key and isinstance(column.type, Integer) and column.autoincrement is not False:
                    with cloud.cursor() as cur:
                        cur.execute(
                            "SELECT setval(pg_get_serial_sequence(%s, %s), COALESCE(MAX(\"" + column.name + "\"), 0) + 1, false) "
                            f'FROM "{table.name}"', (table.name, column.name),
                        )
        cloud.commit()
        with cloud.cursor() as cur:
            for name in ("courses", "roadmaps", "roadmap_steps", "course_listings", "skills", "users"):
                cur.execute(f"SELECT COUNT(*) FROM {name}")
                print(f"{name}: {cur.fetchone()[0]}")


if __name__ == "__main__":
    main()

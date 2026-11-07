r"""Saves the whole database to backend/backups/careerpath-YYYY-MM-DD.sql and keeps the last 14 copies.

Run: venv\Scripts\python -m scripts.backup_db
Restore into an empty database: psql -h 127.0.0.1 -p 5433 -U <user> -d careerpath -f backups\<file>.sql
"""
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

from sqlalchemy.engine import make_url

from app.core.config import BACKEND_DIR, get_settings

PG_DUMP = BACKEND_DIR / "venv" / "Lib" / "site-packages" / "pgserver" / "pginstall" / "bin" / "pg_dump.exe"
FOLDER = BACKEND_DIR / "backups"
KEEP = 14
# OneDrive copies the backup to the cloud, so the data survives if this laptop breaks.
CLOUD = Path(os.environ.get("OneDrive", "")) / "CareerPath-backups" if os.environ.get("OneDrive") else None


def main() -> None:
    url = make_url(get_settings().database_url)
    FOLDER.mkdir(exist_ok=True)
    target: Path = FOLDER / f"careerpath-{date.today().isoformat()}.sql"
    env = {**os.environ, "PGPASSWORD": url.password or ""}
    command = [str(PG_DUMP), "-h", url.host or "127.0.0.1", "-p", str(url.port or 5432), "-U", url.username or "postgres",
               "--no-owner", "--clean", "--if-exists", "-f", str(target), url.database or "careerpath"]
    result = subprocess.run(command, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        print("Backup failed:", result.stderr.strip())
        sys.exit(1)
    copies = sorted(FOLDER.glob("careerpath-*.sql"))
    for old in copies[:-KEEP]:
        old.unlink()
    if CLOUD:
        CLOUD.mkdir(exist_ok=True)
        (CLOUD / target.name).write_bytes(target.read_bytes())
        for old in sorted(CLOUD.glob("careerpath-*.sql"))[:-KEEP]:
            old.unlink()
    print(f"Backup saved: {target.name} ({target.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

"""
Starts a real PostgreSQL server for local development, with nothing to install:
    python -m scripts.dev_db start
    python -m scripts.dev_db stop

It only listens on this computer, so it needs no password. Production uses a hosted
PostgreSQL through DATABASE_URL and never runs this file.
"""
import subprocess
import sys
from pathlib import Path

import pgserver

from app.core.config import BACKEND_DIR

BIN = Path(pgserver.__file__).parent / "pginstall" / "bin"
DATA = BACKEND_DIR / ".devdb"
# Kept outside the data folder: inside it, crash recovery stalls on a Windows file-sharing conflict
LOG = BACKEND_DIR / ".devdb.log"
PORT = "5433"
START_TIMEOUT_SECONDS = "120"
# Lets the server outlive the window or tool that started it, so closing that can't crash it
DETACHED = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)


def run(tool: str, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run([str(BIN / tool), *args], check=check, capture_output=True, text=True)


def is_running() -> bool:
    return run("pg_ctl", "status", "-D", str(DATA), check=False).returncode == 0


def start() -> None:
    if not DATA.exists():
        run("initdb", "-D", str(DATA), "-U", "postgres", "-A", "trust", "-E", "UTF8", "--locale=C")
    if not is_running():
        # Popen, not run: the server keeps running after this script ends
        subprocess.Popen(
            [str(BIN / "pg_ctl"), "start", "-w", "-t", START_TIMEOUT_SECONDS, "-D", str(DATA), "-l", str(LOG),
             "-o", f"-p {PORT} -h 127.0.0.1"],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=DETACHED,
        ).wait()
    exists = run("psql", "-p", PORT, "-h", "127.0.0.1", "-U", "postgres", "-tAc",
                 "select 1 from pg_database where datname = 'careerpath'").stdout.strip()
    if not exists:
        run("createdb", "-p", PORT, "-h", "127.0.0.1", "-U", "postgres", "careerpath")
    print(f"PostgreSQL is running on 127.0.0.1:{PORT}")


def stop() -> None:
    if is_running():
        run("pg_ctl", "stop", "-D", str(DATA), "-m", "fast")
    print("PostgreSQL stopped")


if __name__ == "__main__":
    {"start": start, "stop": stop}[sys.argv[1] if len(sys.argv) > 1 else "start"]()

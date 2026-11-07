"""
Daily safe sync from official websites:  python -m scripts.sync_official
Runs from the daily update. See app/sync.py for what it may change by itself.
"""
from app.core.database import SessionLocal
from app.sync import check_dates, sync_dost


def main() -> None:
    with SessionLocal() as db:
        print(sync_dost(db))
        print(check_dates(db))


if __name__ == "__main__":
    main()

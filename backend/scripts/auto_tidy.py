"""
Keeps the Admin page clean by itself:  python -m scripts.auto_tidy   (runs in the 9am daily job)

- Page-change alerts nobody looked at for 30 days are cleared. They never change what students see.
- Records still waiting for review after 30 days are set aside as "outdated", so they stay hidden from students
  and stop waiting. Every change is written to the review log, so nothing disappears without a trace.
"""
from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace

from sqlalchemy import select

from app.api.admin import REVIEWABLE, change_status
from app.core.database import SessionLocal
from app.models import SourceWatch

DAYS = 30
SYSTEM = SimpleNamespace(id=None)   # logged as done automatically, not by a person


def tidy(db, today: date | None = None) -> dict[str, int]:
    today = today or date.today()
    cutoff = datetime.combine(today - timedelta(days=DAYS), datetime.min.time(), tzinfo=UTC)
    alerts = 0
    for watch in db.scalars(select(SourceWatch).where(SourceWatch.needs_review.is_(True))):
        if watch.last_changed_at is None or watch.last_changed_at < cutoff:
            watch.needs_review = False
            alerts += 1
    waiting = 0
    for entity, model in REVIEWABLE.items():
        for record in db.scalars(select(model).where(model.status == "pending_verification")):
            added = record.last_updated or today
            if added <= today - timedelta(days=DAYS):
                change_status(db, entity, record, "outdated", SYSTEM,
                              f"Set aside automatically after {DAYS} days without review. Hidden from students.")
                waiting += 1
    db.commit()
    return {"alerts cleared": alerts, "waiting records set aside": waiting}


def main() -> None:
    with SessionLocal() as db:
        result = tidy(db)
    print("Auto tidy:", ", ".join(f"{count} {what}" for what, count in result.items()))


if __name__ == "__main__":
    main()

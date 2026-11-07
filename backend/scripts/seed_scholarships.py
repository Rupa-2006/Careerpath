"""
Loads scholarships and loans:  python -m scripts.seed_scholarships
Safe to run again: records are matched by slug, so review status is kept.
"""
from datetime import date

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import Scholarship
from scripts.content import ACADEMIC_YEAR
from scripts.scholarships_content import SCHOLARSHIPS
from scripts.seed_journey import source_for

CHECKED = date(2026, 11, 5)


def main() -> None:
    with SessionLocal() as db:
        for order, row in enumerate(SCHOLARSHIPS):
            slug, name, run_by, kind, audience, state, who, what, how, url, source = row
            item = db.scalar(select(Scholarship).where(Scholarship.slug == slug))
            if item is None:
                item = Scholarship(slug=slug)
                db.add(item)
            item.name, item.run_by, item.kind, item.audience, item.state = name, run_by, kind, audience, state
            item.who_can_apply, item.what_you_get, item.how_to_apply, item.apply_url = who, what, how, url
            item.sort_order, item.academic_year, item.last_updated = order, ACADEMIC_YEAR, CHECKED
            item.source = source_for(db, source)
        db.commit()
    print(f"Scholarships ready: {len(SCHOLARSHIPS)}. New records await review.")


if __name__ == "__main__":
    main()

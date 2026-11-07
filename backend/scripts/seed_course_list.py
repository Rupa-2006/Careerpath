"""
Loads the full course list:  python -m scripts.seed_course_list
Safe to run again: rows are matched by name and state, so review status is kept.
"""
from datetime import date

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import CourseListing
from scripts.content import ACADEMIC_YEAR
from scripts.course_list_data import COURSE_LIST
from scripts.seed_journey import source_for

CHECKED = date(2026, 11, 6)


def main() -> None:
    with SessionLocal() as db:
        for order, (name, group, duration, state, route, slug, source) in enumerate(COURSE_LIST):
            row = db.scalar(select(CourseListing).where(CourseListing.name == name, CourseListing.state == state))
            if row is None:
                row = CourseListing(name=name, state=state)
                db.add(row)
            row.group_name, row.duration, row.route, row.course_slug = group, duration, route, slug
            row.sort_order, row.academic_year, row.last_updated = order, ACADEMIC_YEAR, CHECKED
            row.source = source_for(db, source)
        db.commit()
    print(f"Course list ready: {len(COURSE_LIST)} entries. New records await review.")


if __name__ == "__main__":
    main()

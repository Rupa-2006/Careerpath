"""
Loads technology changes:  python -m scripts.seed_tech_changes
Run seed_journey first. Safe to run again: records are matched by slug, so review status is kept.
"""
from datetime import date

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import Roadmap, TechChange
from scripts.content import ACADEMIC_YEAR
from scripts.seed_journey import source_for
from scripts.tech_changes_content import TECH_CHANGES

CHECKED = date(2026, 11, 7)


def main() -> None:
    with SessionLocal() as db:
        roadmaps = {item.slug: item for item in db.scalars(select(Roadmap))}
        for order, (slug, title, level, what, why, learn, source, for_roadmaps) in enumerate(TECH_CHANGES):
            item = db.scalar(select(TechChange).where(TechChange.slug == slug))
            if item is None:
                item = TechChange(slug=slug)
                db.add(item)
            item.title, item.level, item.what_changed, item.why_it_matters, item.learn_next = title, level, what, why, learn
            item.sort_order, item.academic_year, item.last_updated = order, ACADEMIC_YEAR, CHECKED
            item.source = source_for(db, source)
            item.roadmaps = [roadmaps[name] for name in for_roadmaps]
        db.commit()
    print(f"Technology changes ready: {len(TECH_CHANGES)}. New records await review.")


if __name__ == "__main__":
    main()

"""
Loads what opens up after each roadmap:  python -m scripts.seed_opportunities
Run seed_journey first. Safe to run again: review status is kept.
"""
from datetime import date

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import CareerOpportunity, Roadmap
from scripts.content import ACADEMIC_YEAR
from scripts.opportunities_content import INTERNSHALA, NCS, NPTEL, OPPORTUNITIES, UPSC
from scripts.seed_journey import source_for

CHECKED = date(2026, 11, 7)


def rows(roles, study, government, own):
    return [
        ("jobs", "Jobs you can look for", roles, NCS),
        ("internship", "Internships and first experience", "Do an internship before you finish, so you have real work to show.", INTERNSHALA),
        ("study", "Further study", study, NPTEL),
        ("government", "Government and public routes", government, UPSC if "UPSC" in government else NCS),
        ("own", "Working for yourself", own, NCS),
    ]


def main() -> None:
    with SessionLocal() as db:
        for slug, data in OPPORTUNITIES.items():
            roadmap = db.scalar(select(Roadmap).where(Roadmap.slug == slug))
            for order, (kind, title, detail, url) in enumerate(rows(*data)):
                item = db.scalar(select(CareerOpportunity).where(CareerOpportunity.roadmap_id == roadmap.id, CareerOpportunity.kind == kind))
                if item is None:
                    item = CareerOpportunity(roadmap_id=roadmap.id, kind=kind)
                    db.add(item)
                item.title, item.detail, item.url, item.sort_order = title, detail, url, order
                item.academic_year, item.last_updated, item.source = ACADEMIC_YEAR, CHECKED, source_for(db, "ncs")
        db.commit()
    print(f"Opportunities ready for {len(OPPORTUNITIES)} careers. New records await review.")


if __name__ == "__main__":
    main()

"""
Saves the pre-check marks:  python -m scripts.seed_prechecks
Run after the content scripts. It never publishes anything. If a record's text changes later, its mark stops counting.
"""
from datetime import date

from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload

from app.api.admin import REVIEWABLE, fingerprint, review_item
from app.core.database import SessionLocal
from app.models import EligibilityCriterion, Precheck
from scripts.prechecked import PRECHECKED

CHECKED = date(2026, 11, 6)


def main() -> None:
    wanted = set(PRECHECKED)
    found = set()
    with SessionLocal() as db:
        db.execute(delete(Precheck))
        for entity, model in REVIEWABLE.items():
            query = select(model).options(joinedload(model.source))
            if entity == "criterion":
                query = query.options(joinedload(EligibilityCriterion.course))
            for record in db.scalars(query).all():
                item = review_item(entity, record)
                if (entity, item.title) in wanted:
                    found.add((entity, item.title))
                    db.add(Precheck(entity_type=entity, entity_id=record.id, fingerprint=fingerprint(item), checked_on=CHECKED))
        db.commit()
    print(f"Pre-check marks saved: {len(found)} of {len(wanted)}. Nothing was published.")
    for entity, title in sorted(wanted - found):
        print(f"Not found: {entity}: {title}")


if __name__ == "__main__":
    main()

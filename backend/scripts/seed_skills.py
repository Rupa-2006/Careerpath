"""
Loads the skill checklist:  python -m scripts.seed_skills
Run seed_journey first. Safe to run again: skills are matched by slug, so review status and students' ticks are kept.
"""
from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.models import LearningResource, Roadmap, Skill
from scripts.content import ACADEMIC_YEAR, CHECKED
from scripts.seed_journey import Telugu, source_for
from scripts.skills_content import SKILLS


def main() -> None:
    with SessionLocal() as db:
        roadmaps = {item.slug: item for item in db.scalars(select(Roadmap))}
        telugu = Telugu(db)
        for order, (slug, category, name, name_te, why, why_te, project, project_te, source, links, for_roadmaps) in enumerate(SKILLS, start=1):
            skill = db.scalar(select(Skill).where(Skill.slug == slug))
            if skill is None:
                skill = Skill(slug=slug)
                db.add(skill)
            skill.category, skill.name, skill.why, skill.project = category, name, why, project
            skill.sort_order, skill.academic_year, skill.last_updated = order, ACADEMIC_YEAR, CHECKED
            skill.source = source_for(db, source)
            skill.roadmaps = [roadmaps[item] for item in for_roadmaps]
            db.flush()
            db.execute(delete(LearningResource).where(LearningResource.skill_id == skill.id))
            db.add_all(LearningResource(skill_id=skill.id, label=label, url=url) for label, url in links)
            telugu.put("skill", skill.id, name=name_te, why=why_te, project=project_te)
        db.commit()
    print(f"Skills ready: {len(SKILLS)}. New skills await review.")


if __name__ == "__main__":
    main()

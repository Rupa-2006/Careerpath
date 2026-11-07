from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload, selectinload

from app.api.catalog import visible
from app.career_growth import CAREER_GROWTH
from app.api.deps import CurrentUser, Db, MaybeUser
from app.models import CareerOpportunity, CourseListing, Roadmap, Scholarship, Skill, TechChange, UserSkill
from app.schemas import CareerGrowthOut, CareerOpportunityOut, CourseListingOut, ScholarshipOut, SkillOut, SkillStatusIn, TechChangeOut
from app.translate import Lang, text_map

router = APIRouter(tags=["skills"])


@router.get("/career-growth", response_model=CareerGrowthOut | None)
def career_growth(roadmap: Annotated[str, Query(max_length=60)]) -> CareerGrowthOut | None:
    found = CAREER_GROWTH.get(roadmap)
    return CareerGrowthOut(first=found[0], next=found[1], senior=found[2], ready=found[3]) if found else None


@router.get("/career-opportunities", response_model=list[CareerOpportunityOut])
def career_opportunities(db: Db, roadmap: Annotated[str, Query(max_length=60)]) -> list[CareerOpportunity]:
    query = (
        select(CareerOpportunity).options(joinedload(CareerOpportunity.source))
        .where(CareerOpportunity.status.in_(visible()), CareerOpportunity.roadmap.has(Roadmap.slug == roadmap))
    )
    return list(db.scalars(query.order_by(CareerOpportunity.sort_order)))


@router.get("/technology-changes", response_model=list[TechChangeOut])
def technology_changes(db: Db, roadmap: Annotated[str, Query(max_length=60)] = "") -> list[TechChange]:
    query = select(TechChange).options(joinedload(TechChange.source)).where(TechChange.status.in_(visible()))
    if roadmap:
        query = query.where(TechChange.roadmaps.any(Roadmap.slug == roadmap))
    return list(db.scalars(query.order_by(TechChange.sort_order)))


@router.get("/course-list", response_model=list[CourseListingOut])
def course_list(db: Db) -> list[CourseListing]:
    query = select(CourseListing).options(joinedload(CourseListing.source)).where(CourseListing.status.in_(visible()))
    return list(db.scalars(query.order_by(CourseListing.sort_order)))


@router.get("/scholarships", response_model=list[ScholarshipOut])
def scholarships(db: Db) -> list[Scholarship]:
    query = select(Scholarship).options(joinedload(Scholarship.source)).where(Scholarship.status.in_(visible()))
    return list(db.scalars(query.order_by(Scholarship.sort_order)))


@router.get("/skills", response_model=list[SkillOut])
def skills(
    db: Db, user: MaybeUser, lang: Lang = "en",
    category: Annotated[str, Query(max_length=20)] = "",
    roadmap: Annotated[str, Query(max_length=60)] = "",
) -> list[SkillOut]:
    query = (
        select(Skill).options(joinedload(Skill.source), selectinload(Skill.resources), selectinload(Skill.roadmaps))
        .where(Skill.status.in_(visible())).order_by(Skill.sort_order)
    )
    if category:
        query = query.where(Skill.category == category)
    if roadmap:
        # A skill with no roadmaps helps in every career, so it stays on every career's list
        query = query.where(Skill.roadmaps.any(Roadmap.slug == roadmap) | ~Skill.roadmaps.any())
    found = db.scalars(query).all()

    words = text_map(db, "skill", [item.id for item in found], lang)
    mine = {}
    if user is not None:
        mine = dict(db.execute(select(UserSkill.skill_id, UserSkill.state).where(UserSkill.user_id == user.id)).all())
    return [
        SkillOut(
            status=item.status, academic_year=item.academic_year, last_updated=item.last_updated, source=item.source,
            id=item.id, slug=item.slug, category=item.category,
            name=words.get((item.id, "name"), item.name),
            why=words.get((item.id, "why"), item.why),
            project=words.get((item.id, "project"), item.project),
            resources=[{"label": link.label, "url": link.url} for link in item.resources],
            for_all=not item.roadmaps, state=mine.get(item.id),
        )
        for item in found
    ]


@router.put("/me/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def set_skill(skill_id: int, data: SkillStatusIn, user: CurrentUser, db: Db) -> None:
    if db.get(Skill, skill_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Skill not found.")
    row = db.scalar(select(UserSkill).where(UserSkill.user_id == user.id, UserSkill.skill_id == skill_id))
    if row is None:
        db.add(UserSkill(user_id=user.id, skill_id=skill_id, state=data.state))
    else:
        row.state = data.state
    db.commit()


@router.delete("/me/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def clear_skill(skill_id: int, user: CurrentUser, db: Db) -> None:
    db.execute(delete(UserSkill).where(UserSkill.user_id == user.id, UserSkill.skill_id == skill_id))
    db.commit()

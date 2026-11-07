from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload, selectinload

from app.api.deps import Db
from app.core.config import get_settings
from app.eligibility import check, group_text
from app.models import Course, EligibilityCriterion, EligibilityGroup, EntranceExam, Field, Roadmap, Stream
from app.translate import Lang, text_map
from app.schemas import (
    CourseDetail,
    CourseList,
    CourseSummary,
    CriterionOut,
    ExamOut,
    FieldDetail,
    FieldSummary,
    GroupOut,
)

router = APIRouter(tags=["catalog"])

# Loads everything the eligibility check needs in a few queries, not one per course
COURSE_LOAD = (
    joinedload(Course.field),
    joinedload(Course.source),
    selectinload(Course.criteria).selectinload(EligibilityCriterion.regions),
    selectinload(Course.criteria).selectinload(EligibilityCriterion.source),
    selectinload(Course.criteria).selectinload(EligibilityCriterion.groups).selectinload(EligibilityGroup.subjects),
)

RegionParam = Annotated[int | None, Query(alias="region")]
StreamParam = Annotated[int | None, Query(alias="stream")]
SubjectsParam = Annotated[str, Query(alias="subjects", max_length=200, pattern=r"^[0-9,]*$")]


def visible() -> tuple[str, ...]:
    return get_settings().visible_statuses


def student_subjects(db: Db, stream_id: int | None, subjects: str) -> set[int] | None:
    """Exact subjects win. Otherwise use the stream's usual subjects, if it has any."""
    chosen = {int(item) for item in subjects.split(",") if item}
    if chosen:
        return chosen
    if stream_id is not None:
        stream = db.scalar(select(Stream).options(selectinload(Stream.subjects)).where(Stream.id == stream_id))
        if stream and stream.subjects:
            return {subject.id for subject in stream.subjects}
    return None


def summary_of(course: Course, subject_ids: set[int] | None, region_id: int | None) -> dict:
    return {
        "status": course.status,
        "academic_year": course.academic_year,
        "last_updated": course.last_updated,
        "source": course.source,
        "slug": course.slug,
        "name": course.name,
        "kind": course.kind,
        "summary": course.summary,
        "duration": course.duration,
        "field_slug": course.field.slug,
        "field_name": course.field.name,
        "eligibility": check(course, subject_ids, region_id, visible()),
    }


def detail_of(db: Db, course: Course, subject_ids: set[int] | None, region_id: int | None, lang: str = "en") -> CourseDetail:
    shown = visible()
    words = text_map(db, "course", [course.id], lang)
    roadmaps = db.scalars(
        select(Roadmap).where(Roadmap.courses.any(Course.id == course.id), Roadmap.status.in_(shown)).order_by(Roadmap.sort_order)
    ).all()
    roadmap_words = text_map(db, "roadmap", [item.id for item in roadmaps], lang)
    summary = summary_of(course, subject_ids, region_id)
    summary["summary"] = words.get((course.id, "summary"), course.summary)
    return CourseDetail(
        **summary,
        what_you_study=words.get((course.id, "what_you_study"), course.what_you_study),
        roadmaps=[{"slug": item.slug, "name": roadmap_words.get((item.id, "name"), item.name)} for item in roadmaps],
        admission=course.admission,
        path_note=course.path_note,
        path_years=course.path_years,
        careers=[career.name for career in course.careers],
        exams=[ExamOut.model_validate(exam) for exam in course.exams if exam.status in shown],
        criteria=[
            CriterionOut(
                status=item.status, academic_year=item.academic_year, last_updated=item.last_updated,
                source=item.source, label=item.label, summary=item.summary, subjects_known=item.subjects_known,
                min_percentage=item.min_percentage, min_percentage_reserved=item.min_percentage_reserved,
                min_age=item.min_age, max_age=item.max_age,
                regions=[region.name for region in item.regions],
                groups=[GroupOut(min_count=group.min_count, subjects=[group_text(group)]) for group in item.groups],
            )
            for item in course.criteria if item.status in shown
        ],
    )


def load_course(db: Db, slug: str) -> Course:
    course = db.scalar(
        select(Course).options(*COURSE_LOAD, selectinload(Course.careers), selectinload(Course.exams).joinedload(EntranceExam.region))
        .where(Course.slug == slug, Course.status.in_(visible()))
    )
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "We couldn't find that course.")
    return course


@router.get("/fields", response_model=list[FieldSummary])
def fields(db: Db) -> list[FieldSummary]:
    found = db.scalars(
        select(Field).options(selectinload(Field.courses), joinedload(Field.source))
        .where(Field.status.in_(visible())).order_by(Field.sort_order)
    ).all()
    result = []
    for field in found:
        item = FieldSummary.model_validate(field)
        item.course_count = sum(1 for course in field.courses if course.status in visible())
        result.append(item)
    return result


@router.get("/fields/{slug}", response_model=FieldDetail)
def field_detail(
    slug: str, db: Db, region: RegionParam = None, stream: StreamParam = None, subjects: SubjectsParam = "",
) -> FieldDetail:
    field = db.scalar(
        select(Field).options(joinedload(Field.source)).where(Field.slug == slug, Field.status.in_(visible()))
    )
    if field is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "We couldn't find that field.")
    courses = db.scalars(
        select(Course).options(*COURSE_LOAD).where(Course.field_id == field.id, Course.status.in_(visible())).order_by(Course.name)
    ).all()
    subject_ids = student_subjects(db, stream, subjects)
    return FieldDetail(
        status=field.status, academic_year=field.academic_year, last_updated=field.last_updated, source=field.source,
        slug=field.slug, name=field.name, tagline=field.tagline, course_count=len(courses),
        what_is_it=field.what_is_it, what_you_learn=field.what_you_learn, who_can_choose=field.who_can_choose,
        required_skills=field.required_skills, further_education=field.further_education,
        courses=[CourseSummary(**summary_of(course, subject_ids, region)) for course in courses],
    )


@router.get("/courses", response_model=CourseList)
def courses(
    db: Db,
    lang: Lang = "en",
    q: Annotated[str, Query(max_length=100)] = "",
    field: Annotated[str, Query(max_length=60)] = "",
    exam: Annotated[str, Query(max_length=60)] = "",
    open_to_me: bool = False,
    region: RegionParam = None,
    stream: StreamParam = None,
    subjects: SubjectsParam = "",
) -> CourseList:
    query = select(Course).options(*COURSE_LOAD).where(Course.status.in_(visible())).order_by(Course.name)
    if q.strip():
        pattern = "%" + q.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        query = query.where(or_(
            Course.name.ilike(pattern, escape="\\"),
            Course.summary.ilike(pattern, escape="\\"),
            Course.what_you_study.ilike(pattern, escape="\\"),
        ))
    if field:
        query = query.join(Course.field).where(Field.slug == field)
    if exam:
        query = query.where(Course.exams.any(EntranceExam.slug == exam))

    subject_ids = student_subjects(db, stream, subjects)
    found = db.scalars(query).all()
    words = text_map(db, "course", [course.id for course in found], lang)
    items = [
        CourseSummary(**{**summary_of(course, subject_ids, region), "summary": words.get((course.id, "summary"), course.summary)})
        for course in found
    ]
    if open_to_me:
        items = [item for item in items if item.eligibility.status != "not_eligible"]
    return CourseList(total=len(items), courses=items)


@router.get("/courses/compare", response_model=list[CourseDetail])
def compare(
    db: Db,
    slugs: Annotated[str, Query(max_length=200)],
    lang: Lang = "en",
    region: RegionParam = None,
    stream: StreamParam = None,
    subjects: SubjectsParam = "",
) -> list[CourseDetail]:
    chosen = list(dict.fromkeys(slug for slug in slugs.split(",") if slug))
    if not 2 <= len(chosen) <= 3:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Choose 2 or 3 courses to compare.")
    subject_ids = student_subjects(db, stream, subjects)
    return [detail_of(db, load_course(db, slug), subject_ids, region, lang) for slug in chosen]


@router.get("/courses/{slug}", response_model=CourseDetail)
def course_detail(
    slug: str, db: Db, lang: Lang = "en", region: RegionParam = None, stream: StreamParam = None, subjects: SubjectsParam = "",
) -> CourseDetail:
    return detail_of(db, load_course(db, slug), student_subjects(db, stream, subjects), region, lang)


@router.get("/exams", response_model=list[ExamOut])
def exams(db: Db):
    return db.scalars(
        select(EntranceExam).options(joinedload(EntranceExam.source), joinedload(EntranceExam.region))
        .where(EntranceExam.status.in_(visible())).order_by(EntranceExam.name)
    ).all()

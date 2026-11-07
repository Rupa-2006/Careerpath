"""Roadmaps, progress, the quiz, exam dates, reports, updates and job sources."""
from datetime import UTC, date, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request, status
from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import joinedload, selectinload

from app.api.auth import client_ip
from app.api.catalog import COURSE_LOAD, student_subjects, visible
from app.api.deps import CurrentUser, Db, MaybeUser
from app.core.security import is_rate_limited, key_for, record_event
from app.eligibility import check
from app.models import (
    Course,
    ImportantDate,
    OpportunitySource,
    QuizOption,
    QuizQuestion,
    QuizResult,
    Report,
    Roadmap,
    RoadmapStep,
    TechnologyUpdate,
    UserStepProgress,
)
from app.schemas import (
    DateOut,
    DatesOut,
    OpportunitySourceOut,
    ProgressRow,
    QuizAnswersIn,
    QuizCourseOut,
    QuizOptionOut,
    QuizQuestionOut,
    QuizResultOut,
    ReportIn,
    RoadmapDetail,
    RoadmapSummary,
    StepOut,
    UpdateOut,
    UpdatesOut,
)
from app.translate import Lang, text_map

router = APIRouter(tags=["journey"])

HEADLINE_MAX_AGE_DAYS = 45
DATE_CHECKED_FOR_DAYS = 30   # exam dates change often, so a date warns when it has not been re-checked
REPORTS_PER_HOUR = 5
REPORT_WINDOW = timedelta(hours=1)


def web_links(text: str) -> list[str]:
    """One link per line. Anything that isn't a web address is dropped."""
    links = [line.strip() for line in text.splitlines()]
    return [link for link in links if link.startswith(("https://", "http://"))]


def done_ids(db: Db, user) -> set[int]:
    if user is None:
        return set()
    return set(db.scalars(select(UserStepProgress.step_id).where(UserStepProgress.user_id == user.id)))


# ---------- Roadmaps ----------

def roadmap_base(roadmap: Roadmap, words: dict) -> dict:
    shown = visible()
    return {
        "status": roadmap.status, "academic_year": roadmap.academic_year, "last_updated": roadmap.last_updated,
        "source": roadmap.source, "slug": roadmap.slug,
        "name": words.get((roadmap.id, "name"), roadmap.name),
        "description": words.get((roadmap.id, "description"), roadmap.description),
        "step_count": len(roadmap.steps),
        "years": max((step.year for step in roadmap.steps), default=0),
        "courses": [course.name for course in roadmap.courses if course.status in shown],
    }


LOAD_ROADMAP = (joinedload(Roadmap.source), selectinload(Roadmap.steps), selectinload(Roadmap.courses))


@router.get("/roadmaps", response_model=list[RoadmapSummary])
def roadmaps(db: Db, lang: Lang = "en") -> list[RoadmapSummary]:
    found = db.scalars(
        select(Roadmap).options(*LOAD_ROADMAP).where(Roadmap.status.in_(visible())).order_by(Roadmap.sort_order)
    ).all()
    words = text_map(db, "roadmap", [item.id for item in found], lang)
    return [RoadmapSummary(**roadmap_base(item, words)) for item in found]


@router.get("/roadmaps/{slug}", response_model=RoadmapDetail)
def roadmap_detail(slug: str, db: Db, user: MaybeUser, lang: Lang = "en") -> RoadmapDetail:
    roadmap = db.scalar(
        select(Roadmap).options(*LOAD_ROADMAP).where(Roadmap.slug == slug, Roadmap.status.in_(visible()))
    )
    if roadmap is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "We couldn't find that roadmap.")
    words = text_map(db, "roadmap", [roadmap.id], lang)
    step_words = text_map(db, "step", [step.id for step in roadmap.steps], lang)
    finished = done_ids(db, user)
    steps = [
        StepOut(
            id=step.id, year=step.year, semester=step.semester,
            title=step_words.get((step.id, "title"), step.title),
            why=step_words.get((step.id, "why"), step.why),
            build_task=step_words.get((step.id, "build_task"), step.build_task),
            resources=web_links(step.resources), done=step.id in finished,
        )
        for step in roadmap.steps
    ]
    return RoadmapDetail(
        **roadmap_base(roadmap, words),
        uses_semesters=roadmap.uses_semesters,
        course_slugs=[course.slug for course in roadmap.courses if course.status in visible()],
        steps=steps,
        done_count=sum(1 for step in steps if step.done),
        next_step_id=next((step.id for step in steps if not step.done), None),
    )


@router.put("/me/progress/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
def mark_done(step_id: int, user: CurrentUser, db: Db) -> None:
    if db.get(RoadmapStep, step_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Step not found.")
    exists = db.scalar(select(UserStepProgress.id).where(UserStepProgress.user_id == user.id, UserStepProgress.step_id == step_id))
    if exists is None:
        db.add(UserStepProgress(user_id=user.id, step_id=step_id))
        db.commit()


@router.delete("/me/progress/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
def mark_not_done(step_id: int, user: CurrentUser, db: Db) -> None:
    db.execute(delete(UserStepProgress).where(UserStepProgress.user_id == user.id, UserStepProgress.step_id == step_id))
    db.commit()


@router.get("/me/progress", response_model=list[ProgressRow])
def my_progress(user: CurrentUser, db: Db, lang: Lang = "en") -> list[ProgressRow]:
    finished = done_ids(db, user)
    found = db.scalars(select(Roadmap).options(selectinload(Roadmap.steps)).order_by(Roadmap.sort_order)).all()
    started = [item for item in found if any(step.id in finished for step in item.steps)]
    words = text_map(db, "roadmap", [item.id for item in started], lang)
    step_words = text_map(db, "step", [step.id for item in started for step in item.steps], lang)
    rows = []
    for item in started:
        upcoming = next((step for step in item.steps if step.id not in finished), None)
        rows.append(ProgressRow(
            slug=item.slug, name=words.get((item.id, "name"), item.name),
            done=sum(1 for step in item.steps if step.id in finished), total=len(item.steps),
            next_step=step_words.get((upcoming.id, "title"), upcoming.title) if upcoming else None,
            next_step_id=upcoming.id if upcoming else None,
        ))
    return rows


# ---------- Quiz ----------

def load_questions(db: Db):
    return db.scalars(
        select(QuizQuestion).options(selectinload(QuizQuestion.options).selectinload(QuizOption.courses))
        .order_by(QuizQuestion.position)
    ).all()


@router.get("/quiz", response_model=list[QuizQuestionOut])
def quiz(db: Db, lang: Lang = "en") -> list[QuizQuestionOut]:
    questions = load_questions(db)
    question_words = text_map(db, "quiz_question", [item.id for item in questions], lang)
    option_words = text_map(db, "quiz_option", [option.id for item in questions for option in item.options], lang)
    return [
        QuizQuestionOut(
            id=item.id, text=question_words.get((item.id, "text"), item.text),
            options=[QuizOptionOut(id=option.id, text=option_words.get((option.id, "text"), option.text)) for option in item.options],
        )
        for item in questions
    ]


def rank_courses(chosen: list[tuple[int, QuizOption]], allowed: set[int] | None) -> list[dict]:
    """
    Rule-based scoring: `chosen` is (weight, option). Interests weigh more than practical
    limits, so nobody is pointed at a course just because it is short and cheap.
    """
    scores: dict[int, dict] = {}
    for weight, option in chosen:
        for course in option.courses:
            if allowed is not None and course.id not in allowed:
                continue
            entry = scores.setdefault(course.id, {"course": course, "score": 0, "options": []})
            entry["score"] += weight
            entry["options"].append(option)
    return sorted(scores.values(), key=lambda item: (-item["score"], item["course"].name))


def build_result(db: Db, snapshot: dict, lang: str) -> QuizResultOut:
    shown = visible()
    slugs = [item["slug"] for item in snapshot["results"]] + snapshot["also"]
    courses = {
        course.slug: course
        for course in db.scalars(select(Course).where(Course.slug.in_(slugs), Course.status.in_(shown)))
    }
    words = text_map(db, "course", [course.id for course in courses.values()], lang)
    results = []
    for item in snapshot["results"]:
        course = courses.get(item["slug"])
        if course is None:
            continue   # the course was withdrawn after this result was saved
        linked = db.scalars(
            select(Roadmap).where(Roadmap.courses.any(Course.id == course.id), Roadmap.status.in_(shown)).order_by(Roadmap.sort_order)
        ).all()
        roadmap_words = text_map(db, "roadmap", [road.id for road in linked], lang)
        results.append(QuizCourseOut(
            slug=course.slug, name=course.name, summary=words.get((course.id, "summary"), course.summary),
            points=len(item["reasons"]),
            reasons=[reason.get(lang) or reason["en"] for reason in item["reasons"]],
            roadmaps=[{"slug": road.slug, "name": roadmap_words.get((road.id, "name"), road.name)} for road in linked],
        ))
    scores = [item["score"] for item in snapshot["results"]]
    return QuizResultOut(
        answered=snapshot["answered"], results=results,
        also=[{"slug": slug, "name": courses[slug].name} for slug in snapshot["also"] if slug in courses],
        top_tie=len(scores) > 1 and scores[0] == scores[1],
    )


@router.post("/quiz/score", response_model=QuizResultOut)
def score_quiz(data: QuizAnswersIn, db: Db, user: MaybeUser, lang: Lang = "en") -> QuizResultOut:
    questions = load_questions(db)
    chosen = []
    for question in questions:
        # Security: an option only counts if it really belongs to this question
        option = next((item for item in question.options if item.id == data.answers.get(question.id)), None)
        if option is not None:
            chosen.append((question.weight, option))
    if not chosen:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Answer at least one question.")

    # A course the student can't join, or that hasn't been reviewed, never appears
    shown = visible()
    subjects = ",".join(str(item) for item in data.subject_ids)
    subject_ids = student_subjects(db, data.stream_id, subjects)
    catalogue = db.scalars(select(Course).options(*COURSE_LOAD).where(Course.status.in_(shown))).all()
    allowed = {
        course.id for course in catalogue
        if check(course, subject_ids, data.region_id, shown).status != "not_eligible"
    }

    ranked = rank_courses(chosen, allowed)
    top = ranked[:3]
    snapshot = {
        "answered": len(chosen),
        "results": [
            {
                "slug": item["course"].slug, "score": item["score"],
                "reasons": [{"en": option.text, "te": text_map(db, "quiz_option", [option.id], "te").get((option.id, "text"))} for option in item["options"]],
            }
            for item in top
        ],
        # A tie must not hide a course: anything level with 3rd place is still shown
        "also": [item["course"].slug for item in ranked[3:] if len(top) == 3 and item["score"] == top[2]["score"]],
    }
    if user is not None:
        db.add(QuizResult(user_id=user.id, answered=snapshot["answered"], results=snapshot["results"], also=snapshot["also"]))
        db.commit()
    return build_result(db, snapshot, lang)


@router.get("/me/quiz-result", response_model=QuizResultOut | None)
def my_quiz_result(user: CurrentUser, db: Db, lang: Lang = "en") -> QuizResultOut | None:
    saved = db.scalar(
        select(QuizResult).where(QuizResult.user_id == user.id).order_by(QuizResult.created_at.desc(), QuizResult.id.desc()).limit(1)
    )
    if saved is None:
        return None
    return build_result(db, {"answered": saved.answered, "results": saved.results, "also": saved.also}, lang)


# ---------- Exam dates ----------

def date_out(item: ImportantDate, words: dict) -> DateOut:
    today = date.today()
    return DateOut(
        status=item.status, academic_year=item.academic_year, last_updated=item.last_updated, source=item.source,
        id=item.id, title=words.get((item.id, "title"), item.title), certainty=item.certainty,
        starts_on=item.starts_on, ends_on=item.ends_on, note=words.get((item.id, "note"), item.note),
        checked_on=item.checked_on, days_left=(item.starts_on - today).days if item.starts_on else None,
        recheck_due=(today - item.checked_on).days > DATE_CHECKED_FOR_DAYS,
    )


@router.get("/dates", response_model=DatesOut)
def dates(db: Db, lang: Lang = "en", stream: int | None = None, course: str = "") -> DatesOut:
    today = date.today()
    query = select(ImportantDate).options(joinedload(ImportantDate.source)).where(ImportantDate.status.in_(visible()))
    if course:
        query = query.where(ImportantDate.courses.any(Course.slug == course))
    found = db.scalars(query.order_by(ImportantDate.starts_on.asc().nulls_last(), ImportantDate.title)).all()
    if stream is not None:
        subject_ids = student_subjects(db, stream, "")
        if subject_ids is not None:
            linked = db.scalars(select(Course).options(*COURSE_LOAD).where(Course.status.in_(visible()))).all()
            open_ids = {item.id for item in linked if check(item, subject_ids, None, visible()).status != "not_eligible"}
            with_courses = db.scalars(select(ImportantDate).options(selectinload(ImportantDate.courses))).all()
            keep = {item.id for item in with_courses if any(course_row.id in open_ids for course_row in item.courses)}
            found = [item for item in found if item.id in keep]
    words = text_map(db, "date", [item.id for item in found], lang)
    upcoming = [item for item in found if item.starts_on and (item.ends_on or item.starts_on) >= today]
    waiting = [item for item in found if item.starts_on is None]
    return DatesOut(upcoming=[date_out(item, words) for item in upcoming], waiting=[date_out(item, words) for item in waiting])


# ---------- Reports ----------

@router.post("/reports", status_code=status.HTTP_204_NO_CONTENT)
def report(data: ReportIn, request: Request, db: Db) -> None:
    """Anyone can say a page is wrong. No account or personal details needed."""
    if data.website:
        return   # only robots fill in the hidden field, and they get no hint
    key = key_for("report", client_ip(request))
    if is_rate_limited(db, key, REPORTS_PER_HOUR, REPORT_WINDOW):
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many reports. Please try again later.")
    db.add(Report(page=data.page, message=data.message.strip()))
    record_event(db, key)


# ---------- Updates and job sources ----------

def update_out(item: TechnologyUpdate, words: dict) -> UpdateOut:
    return UpdateOut(
        title=item.title, link=item.link, source_name=item.source_name,
        why_it_matters=words.get((item.id, "why_it_matters"), item.why_it_matters), published_at=item.published_at,
    )


@router.get("/updates", response_model=UpdatesOut)
def updates(db: Db, lang: Lang = "en") -> UpdatesOut:
    fresh_since = datetime.now(UTC) - timedelta(days=HEADLINE_MAX_AGE_DAYS)
    tools = db.scalars(select(TechnologyUpdate).where(TechnologyUpdate.is_tool).order_by(TechnologyUpdate.title)).all()
    latest = db.scalars(
        select(TechnologyUpdate)
        .where(~TechnologyUpdate.is_tool, or_(
            TechnologyUpdate.published_at >= fresh_since,
            TechnologyUpdate.published_at.is_(None) & (TechnologyUpdate.created_at >= fresh_since),
        ))
        .order_by(TechnologyUpdate.published_at.desc().nulls_last()).limit(30)
    ).all()
    words = text_map(db, "update", [item.id for item in tools], lang)
    return UpdatesOut(
        tools=[update_out(item, words) for item in tools],
        latest=[update_out(item, {}) for item in latest],
        last_collected=db.scalar(select(func.max(TechnologyUpdate.created_at)).where(~TechnologyUpdate.is_tool)),
    )


@router.get("/updates/career", response_model=list[UpdateOut])
def career_updates(db: Db, roadmap: Annotated[str, Query(max_length=60)]) -> list[UpdateOut]:
    fresh_since = datetime.now(UTC) - timedelta(days=HEADLINE_MAX_AGE_DAYS)
    found = db.scalars(
        select(TechnologyUpdate)
        .where(TechnologyUpdate.careers.contains([roadmap]), or_(
            TechnologyUpdate.published_at >= fresh_since,
            TechnologyUpdate.published_at.is_(None) & (TechnologyUpdate.created_at >= fresh_since),
        ))
        .order_by(TechnologyUpdate.published_at.desc().nulls_last()).limit(6)
    ).all()
    return [update_out(item, {}) for item in found]


@router.get("/opportunities/sources", response_model=list[OpportunitySourceOut])
def opportunity_sources(db: Db, lang: Lang = "en") -> list[OpportunitySourceOut]:
    found = db.scalars(select(OpportunitySource).order_by(OpportunitySource.sort_order)).all()
    words = text_map(db, "opportunity_source", [item.id for item in found], lang)
    return [
        OpportunitySourceOut(name=item.name, url=item.url, description=words.get((item.id, "description"), item.description))
        for item in found
    ]

import hashlib
import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import joinedload

from app.api.deps import AdminUser, Db
from app.models import (
    CareerOpportunity,
    Course,
    CourseListing,
    EligibilityCriterion,
    EntranceExam,
    Field,
    ImportantDate,
    Region,
    Report,
    Roadmap,
    Precheck,
    Scholarship,
    Skill,
    TechChange,
    Source,
    SourceWatch,
    Stream,
    UpdateHistory,
    User,
    UserSession,
    VerificationRecord,
)
from app.schemas import (
    AdminSummary,
    AdminUserIn,
    AdminUserList,
    AdminUserOut,
    GroupPublishIn,
    SourceWatchOut,
    GroupPublishOut,
    ReportOut,
    ReviewIn,
    ReviewItem,
)

router = APIRouter(prefix="/admin", tags=["admin"])

REVIEWABLE = {
    "field": Field, "course": Course, "exam": EntranceExam, "criterion": EligibilityCriterion,
    "roadmap": Roadmap, "date": ImportantDate, "skill": Skill, "scholarship": Scholarship, "listing": CourseListing, "technology": TechChange, "opportunity": CareerOpportunity,
}
GROUP_PUBLISHABLE = ("pending_verification", "verified")


def count(db: Db, model, *conditions) -> int:
    return db.scalar(select(func.count()).select_from(model).where(*conditions))


@router.get("/summary", response_model=AdminSummary)
def summary(_: AdminUser, db: Db) -> AdminSummary:
    return AdminSummary(
        students=count(db, User, User.role == "student"),
        admins=count(db, User, User.role == "admin"),
        regions=count(db, Region),
        streams=count(db, Stream),
        sources=count(db, Source),
        pending_verification=sum(
            count(db, model, model.status == "pending_verification") for model in REVIEWABLE.values()
        ),
    )


@router.get("/users", response_model=AdminUserList)
def users(
    _: AdminUser, db: Db,
    q: Annotated[str, Query(max_length=100)] = "",
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 25,
) -> AdminUserList:
    conditions = []
    if q.strip():
        pattern = "%" + q.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        conditions.append(User.email.ilike(pattern, escape="\\") | User.name.ilike(pattern, escape="\\") | User.username.ilike(pattern, escape="\\"))
    found = db.scalars(
        select(User).where(*conditions).order_by(User.created_at.desc()).offset((page - 1) * size).limit(size)
    ).all()
    return AdminUserList(total=count(db, User, *conditions), users=found)


@router.patch("/users/{user_id}", response_model=AdminUserOut)
def update_user(user_id: uuid.UUID, data: AdminUserIn, admin: AdminUser, db: Db) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    if user.id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You can't change your own account here.")

    changes = data.model_dump(exclude_none=True)
    for field, value in changes.items():
        setattr(user, field, value)
    if changes.get("is_active") is False:
        db.execute(delete(UserSession).where(UserSession.user_id == user.id))
    db.add(UpdateHistory(
        entity_type="user", entity_id=str(user.id), action="admin_update", changes=changes, actor_id=admin.id,
    ))
    db.commit()
    return user


def fingerprint(item: ReviewItem) -> str:
    return hashlib.sha256(f"{item.title}\n{item.detail}".encode()).hexdigest()


def review_item(entity: str, record) -> ReviewItem:
    if entity == "criterion":
        title, detail = f"{record.course.name}: {record.label}", record.summary
    elif entity == "field":
        title, detail = record.name, record.what_is_it
    elif entity == "roadmap":
        title, detail = record.name, record.description
    elif entity == "skill":
        title, detail = record.name, f"{record.why} Project: {record.project}"
    elif entity == "opportunity":
        title, detail = f"{record.roadmap.name}: {record.title}", record.detail
    elif entity == "technology":
        title, detail = record.title, f"{record.level}. {record.what_changed} {record.why_it_matters} Learn next: {record.learn_next}"
    elif entity == "listing":
        title, detail = record.name, f"{record.group_name}. {record.state}. Route: {record.route}. {record.duration or 'Length not listed'}."
    elif entity == "scholarship":
        title, detail = record.name, f"Who can apply: {record.who_can_apply} What you get: {record.what_you_get}"
    elif entity == "date":
        when = record.starts_on.isoformat() if record.starts_on else "Not announced"
        title, detail = record.title, f"{when} ({record.certainty}). {record.note}".strip()
    else:
        title, detail = record.name, record.summary
    return ReviewItem(
        entity=entity, id=record.id, title=title, detail=detail, status=record.status, source=record.source,
    )


@router.get("/watches", response_model=list[SourceWatchOut])
def source_watches(_: AdminUser, db: Db) -> list[SourceWatch]:
    return list(db.scalars(select(SourceWatch).order_by(SourceWatch.needs_review.desc(), SourceWatch.name)))


@router.post("/watches/{watch_id}/reviewed", response_model=SourceWatchOut)
def watch_reviewed(watch_id: int, _: AdminUser, db: Db) -> SourceWatch:
    watch = db.get(SourceWatch, watch_id)
    if watch is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Page not found.")
    watch.needs_review = False
    db.commit()
    return watch


@router.get("/review", response_model=list[ReviewItem])
def review_queue(
    _: AdminUser, db: Db,
    review_status: Annotated[str, Query(alias="status", max_length=25)] = "pending_verification",
) -> list[ReviewItem]:
    items = []
    marks = {(mark.entity_type, mark.entity_id): mark.fingerprint for mark in db.scalars(select(Precheck))}
    for entity, model in REVIEWABLE.items():
        query = select(model).options(joinedload(model.source)).where(model.status == review_status).order_by(model.id)
        if entity == "criterion":
            query = query.options(joinedload(EligibilityCriterion.course))
        if entity == "opportunity":
            query = query.options(joinedload(CareerOpportunity.roadmap))
        items += [review_item(entity, record) for record in db.scalars(query).all()]
    for item in items:
        item.prechecked = marks.get((item.entity, item.id)) == fingerprint(item)
    return items


def change_status(db: Db, entity: str, record, new_status: str, admin, note: str | None) -> None:
    """Every change is logged the same way, so a group publish leaves the same trail as a single one."""
    previous = record.status
    record.status = new_status
    db.add(VerificationRecord(
        entity_type=entity, entity_id=str(record.id), status=new_status,
        source_id=record.source_id, reviewer_id=admin.id, note=note,
    ))
    db.add(UpdateHistory(
        entity_type=entity, entity_id=str(record.id), action="status_change",
        changes={"status": [previous, new_status]}, actor_id=admin.id,
    ))


@router.post("/review-group/{entity}", response_model=GroupPublishOut)
def publish_group(entity: str, data: GroupPublishIn, admin: AdminUser, db: Db) -> GroupPublishOut:
    """Publishes only the records the admin was shown, so anything added since then still waits for review."""
    model = REVIEWABLE.get(entity)
    if model is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Record type not found.")
    if not data.checked:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Confirm you have checked these against their sources.")

    records = db.scalars(select(model).where(model.id.in_(data.ids), model.status.in_(GROUP_PUBLISHABLE))).all()
    ready = [record for record in records if record.source_id is not None]
    for record in ready:
        change_status(db, entity, record, "published", admin, "Published as a group")
    db.commit()
    return GroupPublishOut(published=len(ready), skipped=len(set(data.ids)) - len(ready))


@router.post("/review/{entity}/{record_id}", response_model=ReviewItem)
def review_record(entity: str, record_id: int, data: ReviewIn, admin: AdminUser, db: Db) -> ReviewItem:
    model = REVIEWABLE.get(entity)
    record = db.get(model, record_id) if model else None
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Record not found.")
    if data.status == "published" and record.source_id is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Add an official source before publishing.")

    change_status(db, entity, record, data.status, admin, data.note)
    db.commit()
    return review_item(entity, record)


@router.get("/reports", response_model=list[ReportOut])
def reports(_: AdminUser, db: Db):
    return db.scalars(select(Report).order_by(Report.resolved, Report.created_at.desc()).limit(100)).all()


@router.post("/reports/{report_id}/resolve", response_model=ReportOut)
def resolve_report(report_id: int, _: AdminUser, db: Db) -> Report:
    report = db.get(Report, report_id)
    if report is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Report not found.")
    report.resolved = True
    db.commit()
    return report

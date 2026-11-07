from datetime import date
from math import ceil
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, selectinload

from app.api.deps import AdminUser, Db
from app.college_import import ImportRefused, publish_batch, reject_batch
from app.models import (
    Branch,
    College,
    CollegeCourse,
    CollegeFact,
    Course,
    ImportBatch,
    Source,
    UpdateHistory,
)
from app.schemas import (
    BatchOut,
    CollegeDetail,
    CollegeFilters,
    CollegeList,
    FactIn,
    FactOut,
    OfferingIn,
    OfferingOut,
    SourcedIn,
    WebsiteIn,
)

router = APIRouter(tags=["colleges"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])

# Students only ever see published records here. Colleges have no development preview,
# because an unreviewed row could be mistaken for a real admission fact.
SHOWN = ("published",)


def offering_out(item: CollegeCourse) -> OfferingOut:
    return OfferingOut(
        id=item.id, status=item.status, academic_year=item.academic_year, last_updated=item.last_updated,
        source=item.source, course_slug=item.course.slug, course_name=item.course.name,
        branch=item.branch.name if item.branch else None,
    )


def detail_of(college: College) -> CollegeDetail:
    return CollegeDetail(
        id=college.id, aishe_code=college.aishe_code, name=college.name, region=college.region,
        status=college.status, academic_year=college.academic_year, last_updated=college.last_updated,
        source=college.source, district=college.district, college_type=college.college_type,
        management=college.management, university_name=college.university_name,
        year_established=college.year_established, location=college.location,
        university_type=college.university_type, website=college.website,
        offerings=[offering_out(item) for item in college.offerings if item.status in SHOWN],
        facts=[FactOut.model_validate(item) for item in college.facts if item.status in SHOWN],
    )


def load_college(db: Db, college_id: int) -> College:
    college = db.scalar(
        select(College)
        .options(
            joinedload(College.region), joinedload(College.source),
            selectinload(College.offerings).options(
                joinedload(CollegeCourse.course), joinedload(CollegeCourse.branch), joinedload(CollegeCourse.source)
            ),
            selectinload(College.facts).joinedload(CollegeFact.source),
        )
        .where(College.id == college_id, College.status.in_(SHOWN))
    )
    if college is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "We couldn't find that college.")
    return college


@router.get("/colleges", response_model=CollegeList)
def colleges(
    db: Db,
    q: Annotated[str, Query(max_length=100)] = "",
    region: int | None = None,
    district: Annotated[str, Query(max_length=100)] = "",
    college_type: Annotated[str, Query(max_length=100)] = "",
    management: Annotated[str, Query(max_length=100)] = "",
    course: Annotated[str, Query(max_length=60)] = "",
    page: Annotated[int, Query(ge=1, le=10000)] = 1,
    size: Annotated[int, Query(ge=1, le=50)] = 20,
) -> CollegeList:
    conditions = [College.status.in_(SHOWN)]
    if q.strip():
        pattern = "%" + q.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        conditions.append(College.name.ilike(pattern, escape="\\"))
    if region is not None:
        conditions.append(College.region_id == region)
    if district:
        conditions.append(College.district == district)
    if college_type:
        conditions.append(College.college_type == college_type)
    if management:
        conditions.append(College.management == management)
    if course:
        conditions.append(College.offerings.any(
            (CollegeCourse.status.in_(SHOWN)) & CollegeCourse.course.has(Course.slug == course)
        ))

    total = db.scalar(select(func.count()).select_from(College).where(*conditions))
    found = db.scalars(
        select(College).options(joinedload(College.region), joinedload(College.source))
        .where(*conditions).order_by(College.name, College.id).offset((page - 1) * size).limit(size)
    ).all()
    return CollegeList(total=total, page=page, pages=ceil(total / size), colleges=found)


@router.get("/colleges/filters", response_model=CollegeFilters)
def college_filters(db: Db, region: int | None = None) -> CollegeFilters:
    def values(column, *conditions):
        return db.scalars(
            select(column).where(College.status.in_(SHOWN), column.is_not(None), *conditions).distinct().order_by(column)
        ).all()

    return CollegeFilters(
        districts=values(College.district, College.region_id == region) if region is not None else [],
        college_types=values(College.college_type),
        managements=values(College.management),
    )


@router.get("/colleges/compare", response_model=list[CollegeDetail])
def compare(db: Db, ids: Annotated[str, Query(max_length=50, pattern=r"^[0-9,]+$")]) -> list[CollegeDetail]:
    chosen = list(dict.fromkeys(int(item) for item in ids.split(",") if item))
    if not 2 <= len(chosen) <= 3:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Choose 2 or 3 colleges to compare.")
    return [detail_of(load_college(db, college_id)) for college_id in chosen]


@router.get("/colleges/{college_id}", response_model=CollegeDetail)
def college_detail(college_id: int, db: Db) -> CollegeDetail:
    return detail_of(load_college(db, college_id))


# ---------- Admin ----------

def source_for(db: Db, data: SourcedIn) -> Source:
    url = str(data.source_url)
    source = db.scalar(select(Source).where(Source.url == url))
    if source is None:
        source = Source(name=data.source_name, url=url, is_official=True)
        db.add(source)
        db.flush()
    return source


def record(db: Db, entity: str, entity_id: int, action: str, changes: dict, admin) -> None:
    db.add(UpdateHistory(entity_type=entity, entity_id=str(entity_id), action=action, changes=changes, actor_id=admin.id))


@admin_router.get("/imports", response_model=list[BatchOut])
def imports(_: AdminUser, db: Db):
    return db.scalars(
        select(ImportBatch).options(joinedload(ImportBatch.source)).order_by(ImportBatch.created_at.desc()).limit(20)
    ).all()


def pending_batch(db: Db, batch_id: int) -> ImportBatch:
    batch = db.scalar(select(ImportBatch).options(joinedload(ImportBatch.source)).where(ImportBatch.id == batch_id))
    if batch is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Import not found.")
    return batch


@admin_router.post("/imports/{batch_id}/publish", response_model=BatchOut)
def publish_import(batch_id: int, admin: AdminUser, db: Db, allow_large_removal: bool = False) -> ImportBatch:
    batch = pending_batch(db, batch_id)
    try:
        publish_batch(db, batch, admin.id, allow_large_removal)
    except ImportRefused as problem:
        raise HTTPException(status.HTTP_409_CONFLICT, str(problem)) from None
    return batch


@admin_router.post("/imports/{batch_id}/reject", response_model=BatchOut)
def reject_import(batch_id: int, admin: AdminUser, db: Db) -> ImportBatch:
    batch = pending_batch(db, batch_id)
    try:
        reject_batch(db, batch, admin.id)
    except ImportRefused as problem:
        raise HTTPException(status.HTTP_409_CONFLICT, str(problem)) from None
    return batch


@admin_router.post("/colleges/{college_id}/offerings", response_model=OfferingOut, status_code=status.HTTP_201_CREATED)
def add_offering(college_id: int, data: OfferingIn, admin: AdminUser, db: Db) -> OfferingOut:
    college = load_college(db, college_id)
    course = db.scalar(select(Course).where(Course.slug == data.course_slug))
    if course is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Unknown course.")
    branch = None
    if data.branch and data.branch.strip():
        name = data.branch.strip()
        branch = db.scalar(select(Branch).where(Branch.course_id == course.id, Branch.name == name))
        if branch is None:
            branch = Branch(course_id=course.id, name=name)
            db.add(branch)
    item = CollegeCourse(
        college=college, course=course, branch=branch, source=source_for(db, data),
        academic_year=data.academic_year, last_updated=date.today(), status="published",
    )
    db.add(item)
    db.flush()
    record(db, "college", college.id, "offering_added", {"course": course.slug, "branch": data.branch}, admin)
    db.commit()
    return offering_out(item)


@admin_router.post("/colleges/{college_id}/facts", response_model=FactOut, status_code=status.HTTP_201_CREATED)
def add_fact(college_id: int, data: FactIn, admin: AdminUser, db: Db) -> CollegeFact:
    college = load_college(db, college_id)
    item = CollegeFact(
        college=college, kind=data.kind, value=data.value.strip(), source=source_for(db, data),
        academic_year=data.academic_year, last_updated=date.today(), status="published",
    )
    db.add(item)
    db.flush()
    record(db, "college", college.id, "fact_added", {"kind": data.kind}, admin)
    db.commit()
    return item


@admin_router.patch("/colleges/{college_id}/website", response_model=CollegeDetail)
def set_website(college_id: int, data: WebsiteIn, admin: AdminUser, db: Db) -> CollegeDetail:
    college = load_college(db, college_id)
    college.website = str(data.website)
    record(db, "college", college.id, "website_set", {"website": college.website}, admin)
    db.commit()
    return detail_of(college)


@admin_router.delete("/colleges/offerings/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_offering(item_id: int, admin: AdminUser, db: Db) -> None:
    item = db.get(CollegeCourse, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found.")
    record(db, "college", item.college_id, "offering_removed", {"course_id": item.course_id}, admin)
    db.delete(item)
    db.commit()


@admin_router.delete("/colleges/facts/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fact(item_id: int, admin: AdminUser, db: Db) -> None:
    item = db.get(CollegeFact, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found.")
    record(db, "college", item.college_id, "fact_removed", {"kind": item.kind}, admin)
    db.delete(item)
    db.commit()


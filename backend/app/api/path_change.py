"""
Changing the career chosen at sign-up.
A student may change it once by themselves. After that, each change is a request an admin approves or rejects.
Progress is never deleted: steps from the old path stay saved and come back if the student returns to it.
"""
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api.deps import AdminUser, CurrentUser, Db
from app.models import PathChangeRequest, Roadmap, UpdateHistory, User
from app.schemas import PathChangeDecisionIn, PathChangeIn, PathChangeOut, PathChangeRequestOut, PathChangeStatus

FREE_CHANGES = 1

router = APIRouter(tags=["path change"])


def roadmap_name(db: Db, slug: str) -> str:
    return db.scalar(select(Roadmap.name).where(Roadmap.slug == slug)) or slug


def apply_path(db: Db, user: User, path: str, actor_id: uuid.UUID, how: str) -> None:
    saved = dict(user.saved_progress or {"steps": {}, "skills": []})
    old = saved.get("path", "")
    saved["path"], saved["path_from"] = path, ""
    user.saved_progress = saved
    user.saved_progress_at = datetime.now(UTC)
    db.add(UpdateHistory(
        entity_type="user_path", entity_id=str(user.id), action=how,
        changes={"path": [old, path]}, actor_id=actor_id,
    ))


def request_out(db: Db, item: PathChangeRequest) -> PathChangeRequestOut:
    return PathChangeRequestOut(
        id=item.id, from_path=item.from_path, from_name=roadmap_name(db, item.from_path),
        to_path=item.to_path, to_name=roadmap_name(db, item.to_path), reason=item.reason, status=item.status,
        created_at=item.created_at, decided_at=item.decided_at,
        student_email=item.user.email if item.user else None, student_name=item.user.name if item.user else None,
    )


@router.get("/me/path-change", response_model=PathChangeStatus)
def my_path_change(user: CurrentUser, db: Db) -> PathChangeStatus:
    latest = db.scalar(
        select(PathChangeRequest).options(joinedload(PathChangeRequest.user))
        .where(PathChangeRequest.user_id == user.id).order_by(PathChangeRequest.created_at.desc()).limit(1)
    )
    return PathChangeStatus(
        path=user.path, free_left=max(0, FREE_CHANGES - user.path_changes),
        latest=request_out(db, latest) if latest else None,
    )


@router.post("/me/path-change", response_model=PathChangeOut)
def change_my_path(data: PathChangeIn, user: CurrentUser, db: Db) -> PathChangeOut:
    if data.path == user.path:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "That is already your path.")
    if db.scalar(select(Roadmap.id).where(Roadmap.slug == data.path)) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Please choose a career from the list.")

    if user.path_changes < FREE_CHANGES:
        apply_path(db, user, data.path, user.id, "changed_by_student")
        user.path_changes += 1
        db.commit()
        return PathChangeOut(result="changed", message=f"Your path is now {roadmap_name(db, data.path)}.")

    waiting = db.scalar(select(PathChangeRequest.id).where(
        PathChangeRequest.user_id == user.id, PathChangeRequest.status == "pending"))
    if waiting:
        raise HTTPException(status.HTTP_409_CONFLICT, "You already have a request waiting. Please wait for an answer.")
    if not data.reason:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Please tell us why you want to change your path.")
    db.add(PathChangeRequest(user_id=user.id, from_path=user.path, to_path=data.path, reason=data.reason))
    db.commit()
    return PathChangeOut(result="requested", message="Your request has been sent. An admin will check it.")


@router.get("/admin/path-requests", response_model=list[PathChangeRequestOut])
def path_requests(_: AdminUser, db: Db) -> list[PathChangeRequestOut]:
    """Waiting requests first, then the 20 most recent answers."""
    load = select(PathChangeRequest).options(joinedload(PathChangeRequest.user))
    waiting = db.scalars(load.where(PathChangeRequest.status == "pending").order_by(PathChangeRequest.created_at)).all()
    done = db.scalars(load.where(PathChangeRequest.status != "pending").order_by(PathChangeRequest.decided_at.desc()).limit(20)).all()
    return [request_out(db, item) for item in [*waiting, *done]]


@router.post("/admin/path-requests/{request_id}", response_model=PathChangeRequestOut)
def decide_path_request(request_id: int, data: PathChangeDecisionIn, admin: AdminUser, db: Db) -> PathChangeRequestOut:
    item = db.scalar(select(PathChangeRequest).options(joinedload(PathChangeRequest.user)).where(PathChangeRequest.id == request_id))
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Request not found.")
    if item.status != "pending":
        raise HTTPException(status.HTTP_409_CONFLICT, "This request has already been answered.")
    item.status = "approved" if data.approve else "rejected"
    item.decided_at, item.decided_by = datetime.now(UTC), admin.id
    if data.approve and item.user:
        apply_path(db, item.user, item.to_path, admin.id, "changed_by_admin")
        item.user.path_changes += 1
    db.commit()
    return request_out(db, item)

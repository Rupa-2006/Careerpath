from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Response, status
from sqlalchemy import delete, select

from app.api.deps import CurrentUser, Db
from app.core.security import SESSION_COOKIE, hash_password, hash_token, password_problem, verify_password
from app.models import Region, Roadmap, Stream, UserSession
from app.schemas import DeleteAccountIn, PasswordChangeIn, ProfileIn, SavedProgress, SavedProgressOut, UserOut

router = APIRouter(prefix="/me", tags=["profile"])


@router.patch("", response_model=UserOut)
def update_profile(data: ProfileIn, user: CurrentUser, db: Db):
    changes = data.model_dump(exclude_unset=True)
    if changes.get("region_id") is not None and db.get(Region, changes["region_id"]) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Unknown state or Union Territory.")
    if changes.get("stream_id") is not None and db.get(Stream, changes["stream_id"]) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Unknown stream.")
    if "name" in changes:
        changes["name"] = (changes["name"] or "").strip() or None
    for field, value in changes.items():
        setattr(user, field, value)
    db.commit()
    return user


@router.post("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: PasswordChangeIn, user: CurrentUser, db: Db,
    token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
) -> None:
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Your current password is wrong.")
    problem = password_problem(data.new_password, user.email)
    if problem:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, problem)
    user.password_hash = hash_password(data.new_password)
    # Log out every other device, in case the old password was stolen
    db.execute(delete(UserSession).where(UserSession.user_id == user.id, UserSession.token_hash != hash_token(token)))
    db.commit()


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(data: DeleteAccountIn, response: Response, user: CurrentUser, db: Db) -> None:
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "That password is wrong.")
    db.delete(user)
    db.commit()
    response.delete_cookie(SESSION_COOKIE, path="/")


@router.get("/saved-progress", response_model=SavedProgressOut)
def get_saved_progress(user: CurrentUser) -> SavedProgressOut:
    """My Path progress kept with the account, so it follows the student to any device."""
    return SavedProgressOut(**(user.saved_progress or {}), saved_at=user.saved_progress_at)


@router.put("/saved-progress", response_model=SavedProgressOut)
def put_saved_progress(data: SavedProgress, user: CurrentUser, db: Db) -> SavedProgressOut:
    """The browser sends the whole, already merged state. Unknown fields and oversized data are refused."""
    if data.path and db.scalar(select(Roadmap.id).where(Roadmap.slug == data.path)) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Unknown career.")
    user.saved_progress = data.model_dump(exclude_none=True)
    user.saved_progress_at = datetime.now(UTC)
    db.commit()
    return SavedProgressOut(**user.saved_progress, saved_at=user.saved_progress_at)

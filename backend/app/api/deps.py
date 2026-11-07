from datetime import UTC, datetime
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import SESSION_COOKIE, hash_token
from app.models import User, UserSession

Db = Annotated[Session, Depends(get_db)]


def current_user(db: Db, token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None) -> User:
    if token:
        session = db.scalar(
            select(UserSession).options(joinedload(UserSession.user))
            .where(UserSession.token_hash == hash_token(token), UserSession.expires_at > datetime.now(UTC))
        )
        if session and session.user.is_active:
            return session.user
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Please log in.")


CurrentUser = Annotated[User, Depends(current_user)]


def optional_user(db: Db, token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None) -> User | None:
    try:
        return current_user(db, token)
    except HTTPException:
        return None


MaybeUser = Annotated[User | None, Depends(optional_user)]


def admin_user(user: CurrentUser) -> User:
    if user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admins only.")
    return user


AdminUser = Annotated[User, Depends(admin_user)]

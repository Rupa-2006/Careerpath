from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Request, Response, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, Db
from app.core.config import get_settings
from app.core.security import (
    SESSION_COOKIE,
    clear_events,
    hash_password,
    hash_token,
    is_rate_limited,
    key_for,
    new_session_token,
    password_problem,
    record_event,
    verify_password,
)
from app.models import User, UserSession
from app.schemas import LoginIn, RegisterIn, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

LOGIN_LIMIT = 5
LOGIN_WINDOW = timedelta(minutes=15)
REGISTER_LIMIT = 10
REGISTER_WINDOW = timedelta(hours=1)


def client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def start_session(db: Db, response: Response, user: User) -> None:
    settings = get_settings()
    token = new_session_token()
    expires = datetime.now(UTC) + timedelta(days=settings.session_days)
    db.add(UserSession(user_id=user.id, token_hash=hash_token(token), expires_at=expires))
    db.execute(delete(UserSession).where(UserSession.user_id == user.id, UserSession.expires_at < datetime.now(UTC)))
    db.commit()
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=settings.session_days * 86400,
        httponly=True,
        samesite="lax",
        secure=settings.is_production,
        path="/",
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterIn, request: Request, response: Response, db: Db) -> User:
    key = key_for("register", client_ip(request))
    if is_rate_limited(db, key, REGISTER_LIMIT, REGISTER_WINDOW):
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many sign-ups. Please try again later.")

    email = data.email.lower()
    problem = password_problem(data.password, email)
    if problem:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, problem)

    user = User(email=email, password_hash=hash_password(data.password), name=data.name)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "This email already has an account. Please log in.") from None
    record_event(db, key)
    start_session(db, response, user)
    return user


@router.post("/login", response_model=UserOut)
def login(data: LoginIn, request: Request, response: Response, db: Db) -> User:
    email = data.email.lower()
    key = key_for("login", email, client_ip(request))
    if is_rate_limited(db, key, LOGIN_LIMIT, LOGIN_WINDOW):
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many wrong tries. Please wait 15 minutes.")

    user = db.scalar(select(User).where(User.email == email))
    password_ok = verify_password(data.password, user.password_hash if user else None)
    if not password_ok or not user.is_active:
        record_event(db, key)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Your email or password is wrong.")

    clear_events(db, key)
    start_session(db, response, user)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, db: Db, token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None) -> None:
    if token:
        db.execute(delete(UserSession).where(UserSession.token_hash == hash_token(token)))
        db.commit()
    response.delete_cookie(SESSION_COOKIE, path="/")


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser) -> User:
    return user

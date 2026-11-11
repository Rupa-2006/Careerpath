from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Request, Response, status
import hashlib
import hmac
import secrets

from sqlalchemy import delete, or_, select
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
from app.mailer import send_email
from app.models import PasswordReset, Roadmap, User, UserSession
from app.schemas import ForgotIn, LoginIn, RegisterIn, ResetPasswordIn, UserOut

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
    if not problem and data.username in data.password.lower():
        problem = "Don't use your username in your password."
    if problem:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, problem)
    if db.scalar(select(User.id).where(User.username == data.username)) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "This username is taken. Please try another.")

    if db.scalar(select(Roadmap.id).where(Roadmap.slug == data.path)) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Please choose your career path.")

    user = User(
        email=email, username=data.username, password_hash=hash_password(data.password), name=data.name,
        saved_progress={"path": data.path, "path_from": "", "steps": {}, "skills": []}, saved_progress_at=datetime.now(UTC),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "This email or username already has an account. Please log in.") from None
    record_event(db, key)
    start_session(db, response, user)
    return user


@router.post("/login", response_model=UserOut)
def login(data: LoginIn, request: Request, response: Response, db: Db) -> User:
    who = data.who
    if not who:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Please enter your username.")
    key = key_for("login", who, client_ip(request))
    if is_rate_limited(db, key, LOGIN_LIMIT, LOGIN_WINDOW):
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many wrong tries. Please wait 15 minutes.")

    user = db.scalar(select(User).where(or_(User.username == who, User.email == who)))
    password_ok = verify_password(data.password, user.password_hash if user else None)
    if not password_ok or not user.is_active:
        record_event(db, key)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Your username or password is wrong.")

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


# ---------- Forgot password or username ----------
# The answer is always the same, so nobody can use these pages to find out who has an account.

RESET_MINUTES = 30
RESET_TRIES = 5
FORGOT_LIMIT = 5
FORGOT_WINDOW = timedelta(hours=1)
SENT = "If that email has an account, we have sent it a message. Please check your inbox."


def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def slow_down(db: Db, request: Request, kind: str, email: str) -> None:
    key = key_for(kind, email, client_ip(request))
    if is_rate_limited(db, key, FORGOT_LIMIT, FORGOT_WINDOW):
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many tries. Please wait an hour.")
    record_event(db, key)


@router.post("/forgot-password")
def forgot_password(data: ForgotIn, request: Request, db: Db) -> dict:
    email = data.email.lower()
    slow_down(db, request, "forgot-password", email)
    user = db.scalar(select(User).where(User.email == email, User.is_active.is_(True)))
    if user:
        code = f"{secrets.randbelow(1_000_000):06d}"
        db.execute(delete(PasswordReset).where(PasswordReset.user_id == user.id))   # only the newest code works
        db.add(PasswordReset(user_id=user.id, code_hash=hash_code(code), expires_at=datetime.now(UTC) + timedelta(minutes=RESET_MINUTES)))
        db.commit()
        send_email(email, "Your PathMithra reset code", (
            f"Hello {user.username},\n\nYour code to reset your PathMithra password is: {code}\n\n"
            f"It works once and expires in {RESET_MINUTES} minutes. If you didn't ask for this, you can ignore this email."
        ))
    return {"message": SENT}


@router.post("/reset-password")
def reset_password(data: ResetPasswordIn, request: Request, db: Db) -> dict:
    email = data.email.lower()
    wrong = HTTPException(status.HTTP_400_BAD_REQUEST, "That code is wrong or has expired. Please ask for a new one.")
    user = db.scalar(select(User).where(User.email == email, User.is_active.is_(True)))
    reset = db.scalar(select(PasswordReset).where(
        PasswordReset.user_id == user.id, PasswordReset.used_at.is_(None), PasswordReset.expires_at > datetime.now(UTC),
    )) if user else None
    if reset is None or reset.attempts >= RESET_TRIES:
        raise wrong
    if not hmac.compare_digest(reset.code_hash, hash_code(data.code)):
        reset.attempts += 1
        db.commit()
        raise wrong

    problem = password_problem(data.new_password, email)
    if not problem and user.username in data.new_password.lower():
        problem = "Don't use your username in your password."
    if problem:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, problem)
    user.password_hash = hash_password(data.new_password)
    reset.used_at = datetime.now(UTC)
    db.execute(delete(UserSession).where(UserSession.user_id == user.id))   # log out everywhere
    db.commit()
    return {"message": "Your password has been changed. Please log in."}


@router.post("/forgot-username")
def forgot_username(data: ForgotIn, request: Request, db: Db) -> dict:
    email = data.email.lower()
    slow_down(db, request, "forgot-username", email)
    user = db.scalar(select(User).where(User.email == email, User.is_active.is_(True)))
    if user:
        send_email(email, "Your PathMithra username", (
            f"Hello,\n\nYour PathMithra username is: {user.username}\n\nYou can log in with it and your password."
        ))
    return {"message": SENT}

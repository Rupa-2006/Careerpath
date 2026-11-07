import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import RateLimitEvent

SESSION_COOKIE = "careerpath_session"
MIN_PASSWORD_LENGTH = 10
MAX_PASSWORD_LENGTH = 128
COMMON_PASSWORDS = {
    "1234567890", "12345678910", "0123456789", "password123", "password1234", "qwertyuiop",
    "iloveyou123", "admin12345", "welcome123", "careerpath", "careerpath1", "careerpath123",
}

_hasher = PasswordHasher()
# Checked when an email is unknown, so response time doesn't reveal which emails have accounts
_DUMMY_HASH = _hasher.hash(secrets.token_urlsafe(16))


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    try:
        matched = _hasher.verify(password_hash or _DUMMY_HASH, password)
    except (VerificationError, InvalidHashError):
        return False
    return matched and password_hash is not None


def password_problem(password: str, email: str) -> str | None:
    """Returns a message a student can act on, or None if the password is acceptable."""
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Use at least {MIN_PASSWORD_LENGTH} characters."
    if len(password) > MAX_PASSWORD_LENGTH:
        return f"Use no more than {MAX_PASSWORD_LENGTH} characters."
    if password.isdigit():
        return "Don't use only numbers."
    if password.lower() in COMMON_PASSWORDS:
        return "This password is too common."
    if email.split("@")[0].lower() in password.lower():
        return "Don't use your email name in your password."
    return None


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def key_for(*parts: str) -> str:
    """Rate-limit keys are hashed, so emails and IP addresses aren't kept in that table."""
    return hashlib.sha256("|".join(parts).lower().encode()).hexdigest()


def is_rate_limited(db: Session, key: str, limit: int, window: timedelta) -> bool:
    since = datetime.now(UTC) - window
    count = db.scalar(
        select(func.count()).select_from(RateLimitEvent)
        .where(RateLimitEvent.key == key, RateLimitEvent.created_at >= since)
    )
    return count >= limit


def record_event(db: Session, key: str) -> None:
    db.execute(delete(RateLimitEvent).where(RateLimitEvent.created_at < datetime.now(UTC) - timedelta(days=1)))
    db.add(RateLimitEvent(key=key))
    db.commit()


def clear_events(db: Session, key: str) -> None:
    db.execute(delete(RateLimitEvent).where(RateLimitEvent.key == key))
    db.commit()

"""Password hashing, demo-account seeding, and opaque session creation."""

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuthSession, User


PASSWORD_ITERATIONS = 600_000
SESSION_DURATION = timedelta(hours=8)
DEMO_USERS = (
    ("requestor@demo.local", "requestor-demo", "requestor"),
    ("reviewer@demo.local", "reviewer-demo", "reviewer"),
)


def hash_password(password: str) -> str:
    """Create a salted PBKDF2-HMAC password hash without an external dependency."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PASSWORD_ITERATIONS)
    return "$".join(
        (
            "pbkdf2_sha256",
            str(PASSWORD_ITERATIONS),
            base64.b64encode(salt).decode(),
            base64.b64encode(digest).decode(),
        )
    )


def password_matches(password: str, stored_hash: str) -> bool:
    """Verify a candidate password against the stored salted hash."""
    algorithm, iterations, salt_value, digest_value = stored_hash.split("$")
    if algorithm != "pbkdf2_sha256":
        return False
    expected_digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), base64.b64decode(salt_value), int(iterations)
    )
    return hmac.compare_digest(expected_digest, base64.b64decode(digest_value))


def seed_demo_users(session: Session) -> None:
    """Create local demo accounts only when they are not already present."""
    added_user = False
    for email, password, role in DEMO_USERS:
        existing_user = session.scalar(select(User).where(User.email == email))
        if existing_user is None:
            session.add(User(email=email, password_hash=hash_password(password), role=role))
            added_user = True
    if added_user:
        session.commit()


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    """Return the user only when the supplied password is valid."""
    user = session.scalar(select(User).where(User.email == email.lower()))
    if user is None or not password_matches(password, user.password_hash):
        return None
    return user


def register_user(session: Session, email: str, password: str, role: str) -> User | None:
    """Create a local account, returning ``None`` when the email is already used."""
    normalized_email = email.lower()
    existing_user = session.scalar(select(User).where(User.email == normalized_email))
    if existing_user is not None:
        return None

    user = User(email=normalized_email, password_hash=hash_password(password), role=role)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_session(session: Session, user: User) -> str:
    """Persist a hash of a new bearer token and return the raw token once."""
    token = secrets.token_urlsafe(32)
    session.add(
        AuthSession(
            user=user,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + SESSION_DURATION,
        )
    )
    session.commit()
    return token

"""Shared SQLAlchemy database configuration."""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./request_triage.db")

# SQLite permits one connection to be used across FastAPI's request-handling
# threads only when this guard is disabled.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base class inherited by all SQLAlchemy models."""


def get_db() -> Generator[Session, None, None]:
    """Yield one database session and always close it after the request."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

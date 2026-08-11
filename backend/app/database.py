"""Shared SQLAlchemy database configuration."""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./request_triage.db")

# Render supplies a PostgreSQL URL. This tells SQLAlchemy to use psycopg,
# the PostgreSQL driver installed in requirements.txt.
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )

engine_options = {}

# This option is required for SQLite with FastAPI, but not for PostgreSQL.
if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_options)
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
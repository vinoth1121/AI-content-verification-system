"""Database session factory + declarative Base.

Uses SQLAlchemy 2.0 style. The Base class is shared by all models.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# `check_same_thread=False` only matters for SQLite; ignored by Postgres.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    future=True,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models."""


def init_db() -> None:
    """Create all tables. Called on app startup in dev; use Alembic in prod."""
    # Import models so they are registered with Base.metadata before create_all.
    from app.models import user, scan  # noqa: F401

    Base.metadata.create_all(bind=engine)


def reinit_engine(new_url: str):
    """Recreate the global engine/session — used by tests that need to override DATABASE_URL."""
    global engine, SessionLocal
    engine = create_engine(
        new_url,
        pool_pre_ping=True,
        future=True,
        connect_args={"check_same_thread": False} if new_url.startswith("sqlite") else {},
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return engine

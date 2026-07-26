"""Pytest configuration & fixtures."""
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Make `backend/` and `ai-engine/` importable
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "ai-engine"))

# Use a stable test secret + ensure env vars don't leak in from the sandbox
os.environ.setdefault("JWT_SECRET", "test-secret-must-be-at-least-32-characters-long")
os.environ["DATABASE_URL"] = "sqlite:///./acvs.db"
os.environ.setdefault("CORS_ORIGINS", '["http://localhost:3000"]')

from app.db.session import Base  # noqa: E402
from app.core.deps import get_db  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture(scope="function")
def db_session():
    """In-memory SQLite DB for isolation."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient wired to use the in-memory DB."""
    app = create_app()

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c

"""Health & info endpoints (unauthenticated)."""
from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["meta"])
settings = get_settings()


@router.get("/health")
def health():
    return {"status": "ok", "env": settings.APP_ENV, "version": "0.1.0"}


@router.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }

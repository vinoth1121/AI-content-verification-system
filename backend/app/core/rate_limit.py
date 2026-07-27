"""Rate limiting configuration using slowapi."""
from __future__ import annotations

import os

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import get_settings

settings = get_settings()


def _storage_uri() -> str:
    if settings.REDIS_URL and "localhost" not in settings.REDIS_URL:
        return settings.REDIS_URL
    return "memory://"


def _is_enabled() -> bool:
    env = os.environ.get("APP_ENV", "development")
    return env != "test"


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=_storage_uri(),
    default_limits=[settings.RATE_LIMIT_GLOBAL],
    headers_enabled=True,
    enabled=_is_enabled(),
)


def register_rate_limiter(app) -> None:
    from fastapi import Request
    from fastapi.responses import JSONResponse

    app.state.limiter = limiter
    app.add_exception_handler(
        RateLimitExceeded,
        lambda request, exc: JSONResponse(
            status_code=429,
            content={"detail": f"Rate limit exceeded: {exc.detail}"},
            headers=getattr(exc, "headers", {}),
        ),
    )
    app.add_middleware(SlowAPIMiddleware)

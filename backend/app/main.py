"""FastAPI application factory."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import admin, auth, meta, scan
from app.core.config import get_settings
from app.core.metrics import metrics_response
from app.core.middleware import MetricsMiddleware
from app.core.rate_limit import register_rate_limiter
from app.db.session import init_db

settings = get_settings()
logging.basicConfig(level=settings.APP_LOG_LEVEL.upper())
logger = logging.getLogger("acvs")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s in %s mode", settings.APP_NAME, settings.APP_ENV)
    if not settings.is_prod:
        init_db()
        logger.info("Dev DB initialized")
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.2.0",
        description="Privacy-first cross-platform AI Content Verification System",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(MetricsMiddleware)
    register_rate_limiter(app)

    api_prefix = "/api/v1"
    app.include_router(meta.router)
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(scan.router, prefix=api_prefix)
    app.include_router(admin.router, prefix=api_prefix)

    @app.get("/metrics", tags=["meta"], include_in_schema=False)
    def prometheus_metrics():
        return metrics_response()

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    return app


app = create_app()

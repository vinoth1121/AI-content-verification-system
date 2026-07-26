"""Scan service: orchestrates the AI engine + persists results.

This is the single entry point for detection. It:
1. Persists a pending Scan row (for audit / history).
2. Calls the appropriate detector from `ai-engine`.
3. Updates the row with results and timing.
4. Returns a structured payload to the router.

The engine is imported lazily so the backend can boot even if heavy ML
deps are missing (e.g. when running unit tests against a stub).
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.scan import Scan, ScanModality, ScanStatus
from app.schemas.scan import ScanResult

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Engine loader (lazy import)
# --------------------------------------------------------------------------- #
def _load_engine():
    """Import the AI engine package lazily so the backend is decoupled."""
    try:
        from ai_engine.engine import detect_text, detect_image, detect_audio, detect_video, detect_fake_news  # type: ignore
        return {
            "detect_text": detect_text,
            "detect_image": detect_image,
            "detect_audio": detect_audio,
            "detect_video": detect_video,
            "detect_fake_news": detect_fake_news,
        }
    except Exception as exc:  # pragma: no cover - import error path
        logger.error("Failed to load ai_engine: %s", exc)
        raise RuntimeError(f"AI engine unavailable: {exc}") from exc


# --------------------------------------------------------------------------- #
# Public service API
# --------------------------------------------------------------------------- #
def run_text_scan(db: Session, user_id: int, text: str) -> Scan:
    scan = Scan(
        user_id=user_id,
        modality=ScanModality.text,
        status=ScanStatus.pending,
        input_meta={"length": len(text)},
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    return _execute(db, scan, lambda: _load_engine()["detect_text"](text))


def run_fake_news_scan(db: Session, user_id: int, text: str, title: str | None) -> Scan:
    scan = Scan(
        user_id=user_id,
        modality=ScanModality.fake_news,
        status=ScanStatus.pending,
        input_meta={"length": len(text), "title": bool(title)},
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return _execute(db, scan, lambda: _load_engine()["detect_fake_news"](text, title=title))


def run_image_scan(db: Session, user_id: int, image_bytes: bytes, mime: str) -> Scan:
    import hashlib
    scan = Scan(
        user_id=user_id,
        modality=ScanModality.image,
        status=ScanStatus.pending,
        input_meta={"size_bytes": len(image_bytes), "mime": mime, "sha256": hashlib.sha256(image_bytes).hexdigest()},
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return _execute(db, scan, lambda: _load_engine()["detect_image"](image_bytes))


def run_audio_scan(db: Session, user_id: int, audio_bytes: bytes, mime: str) -> Scan:
    scan = Scan(
        user_id=user_id,
        modality=ScanModality.audio,
        status=ScanStatus.pending,
        input_meta={"size_bytes": len(audio_bytes), "mime": mime},
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return _execute(db, scan, lambda: _load_engine()["detect_audio"](audio_bytes))


def run_video_scan(db: Session, user_id: int, video_bytes: bytes, mime: str) -> Scan:
    scan = Scan(
        user_id=user_id,
        modality=ScanModality.video,
        status=ScanStatus.pending,
        input_meta={"size_bytes": len(video_bytes), "mime": mime},
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return _execute(db, scan, lambda: _load_engine()["detect_video"](video_bytes))


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _execute(db: Session, scan: Scan, callable_: Any) -> Scan:
    """Run a detector callable and persist results."""
    start = time.perf_counter()
    try:
        raw: dict = callable_()
        result = ScanResult(**raw)
        scan.label = result.label
        scan.confidence = result.confidence
        scan.explanation = result.explanation
        scan.result = raw
        scan.status = ScanStatus.completed
    except Exception as exc:
        logger.exception("Scan %s failed: %s", scan.id, exc)
        scan.status = ScanStatus.failed
        scan.result = {"error": str(exc)}
        scan.explanation = "Detection failed; please retry."
    finally:
        scan.duration_ms = int((time.perf_counter() - start) * 1000)
        scan.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(scan)
    return scan


def list_user_scans(
    db: Session,
    user_id: int,
    *,
    modality: ScanModality | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Scan], int]:
    q = select(Scan).where(Scan.user_id == user_id).order_by(Scan.created_at.desc())
    if modality:
        q = q.where(Scan.modality == modality)
    total = db.scalar(select(func.count()).select_from(q.subquery()))
    items = list(db.scalars(q.offset((page - 1) * page_size).limit(page_size)))
    return items, int(total or 0)


def get_scan(db: Session, user_id: int, scan_id: int) -> Scan | None:
    return db.scalar(select(Scan).where(Scan.id == scan_id, Scan.user_id == user_id))

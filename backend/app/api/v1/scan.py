"""Scan router: text / image / audio / video / fake-news detection + history."""
import hashlib
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import CurrentUser, DbSession
from app.models.scan import ScanModality
from app.schemas.scan import ScanListOut, ScanOut, ScanTextRequest
from app.services import scan_service

router = APIRouter(prefix="/scan", tags=["scan"])
settings = get_settings()
logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Text
# --------------------------------------------------------------------------- #
@router.post("/text", response_model=ScanOut, status_code=status.HTTP_201_CREATED)
def scan_text(payload: ScanTextRequest, db: DbSession, user: CurrentUser):
    scan = scan_service.run_text_scan(db, user.id, payload.text)
    return _to_out(scan)


@router.post("/fake-news", response_model=ScanOut, status_code=status.HTTP_201_CREATED)
def scan_fake_news(payload: ScanTextRequest, db: DbSession, user: CurrentUser):
    scan = scan_service.run_fake_news_scan(db, user.id, payload.text, payload.title)
    return _to_out(scan)


# --------------------------------------------------------------------------- #
# File uploads
# --------------------------------------------------------------------------- #
@router.post("/image", response_model=ScanOut, status_code=status.HTTP_201_CREATED)
async def scan_image(
    db: DbSession,
    user: CurrentUser,
    file: UploadFile = File(..., description="PNG / JPEG / WEBP up to 10 MB"),
):
    raw = await _read_upload(file, settings.MAX_IMAGE_MB)
    scan = scan_service.run_image_scan(db, user.id, raw, file.content_type or "image/png")
    return _to_out(scan)


@router.post("/audio", response_model=ScanOut, status_code=status.HTTP_201_CREATED)
async def scan_audio(
    db: DbSession,
    user: CurrentUser,
    file: UploadFile = File(..., description="WAV / MP3 / FLAC up to 50 MB"),
):
    raw = await _read_upload(file, settings.MAX_AUDIO_MB)
    scan = scan_service.run_audio_scan(db, user.id, raw, file.content_type or "audio/wav")
    return _to_out(scan)


@router.post("/video", response_model=ScanOut, status_code=status.HTTP_201_CREATED)
async def scan_video(
    db: DbSession,
    user: CurrentUser,
    file: UploadFile = File(..., description="MP4 / WEBM up to 100 MB"),
):
    raw = await _read_upload(file, settings.MAX_VIDEO_MB)
    scan = scan_service.run_video_scan(db, user.id, raw, file.content_type or "video/mp4")
    return _to_out(scan)


# --------------------------------------------------------------------------- #
# History
# --------------------------------------------------------------------------- #
@router.get("/history", response_model=ScanListOut)
def history(
    db: DbSession,
    user: CurrentUser,
    modality: ScanModality | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = scan_service.list_user_scans(db, user.id, modality=modality, page=page, page_size=page_size)
    return ScanListOut(items=[_to_out(s) for s in items], total=total, page=page, page_size=page_size)


@router.get("/history/{scan_id}", response_model=ScanOut)
def history_detail(scan_id: int, db: DbSession, user: CurrentUser):
    scan = scan_service.get_scan(db, user.id, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return _to_out(scan)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
async def _read_upload(file: UploadFile, max_mb: int) -> bytes:
    """Read an UploadFile with size enforcement."""
    raw = await file.read()
    if len(raw) > max_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {max_mb} MB limit",
        )
    return raw


def _to_out(scan) -> ScanOut:
    return ScanOut(
        id=scan.id,
        modality=scan.modality.value if hasattr(scan.modality, "value") else scan.modality,
        status=scan.status.value if hasattr(scan.status, "value") else scan.status,
        confidence=scan.confidence,
        label=scan.label,
        explanation=scan.explanation,
        result=scan.result,
        created_at=scan.created_at.isoformat() if scan.created_at else None,
        completed_at=scan.completed_at.isoformat() if scan.completed_at else None,
        duration_ms=scan.duration_ms,
    )

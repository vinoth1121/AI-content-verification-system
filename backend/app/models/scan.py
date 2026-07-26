"""Scan ORM model — every detection request is persisted for history & audit."""
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ScanModality(str, PyEnum):
    text = "text"
    image = "image"
    audio = "audio"
    video = "video"
    fake_news = "fake_news"


class ScanStatus(str, PyEnum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    modality: Mapped[ScanModality] = mapped_column(Enum(ScanModality), nullable=False, index=True)
    status: Mapped[ScanStatus] = mapped_column(Enum(ScanStatus), default=ScanStatus.pending, nullable=False)

    # Inputs / outputs (JSON columns keep schema flexible as the AI engine evolves)
    input_meta: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # e.g. {length, mime, sha256}
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)              # full engine response
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    label: Mapped[str | None] = mapped_column(String(64), nullable=True)          # human / ai-generated / deepfake
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)          # short text for UI badge

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user = relationship("User", backref="scans")

    def __repr__(self) -> str:
        return f"<Scan id={self.id} user_id={self.user_id} modality={self.modality} label={self.label}>"

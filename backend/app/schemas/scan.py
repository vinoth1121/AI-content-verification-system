"""Pydantic schemas for scan requests and responses."""
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


Modality = Literal["text", "image", "audio", "video", "fake_news"]


class ScanTextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=50_000)
    title: str | None = Field(default=None, max_length=500)  # for fake-news mode


class ScanResult(BaseModel):
    """The shape returned by the AI engine and persisted in `Scan.result`."""

    label: str = Field(description="human | ai_generated | deepfake | suspicious | authentic")
    confidence: float = Field(ge=0.0, le=1.0)
    modality: Modality
    explanation: str
    features: dict[str, Any] = Field(default_factory=dict)
    heatmap_path: str | None = None        # for images/video
    flagged_segments: list[dict] | None = None  # for audio/video


class ScanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    modality: Modality
    status: str
    confidence: float | None
    label: str | None
    explanation: str | None
    result: dict | None
    created_at: str
    completed_at: str | None
    duration_ms: int | None


class ScanListOut(BaseModel):
    items: list[ScanOut]
    total: int
    page: int
    page_size: int

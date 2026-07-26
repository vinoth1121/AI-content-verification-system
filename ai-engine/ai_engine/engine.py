"""Public engine entry points — thin wrappers over the detector modules.

We use lazy imports here so that:
- The text + fake-news + image detectors work even if `librosa` (audio) is
  not installed.
- The backend's import of `ai_engine.engine` is fast and never crashes the
  API on startup.
"""
from __future__ import annotations

from typing import Any, Callable

from .detectors.fake_news import detect_fake_news
from .detectors.image import detect_image
from .detectors.text import detect_text

__all__ = [
    "detect_text",
    "detect_fake_news",
    "detect_image",
    "detect_audio",
    "detect_video",
]


def detect_audio(audio_bytes: bytes) -> dict:
    """Lazy wrapper around `detectors.audio.detect_audio`."""
    from .detectors.audio import detect_audio as _impl
    return _impl(audio_bytes)


def detect_video(video_bytes: bytes, max_frames: int = 8) -> dict:
    """Lazy wrapper around `detectors.video.detect_video`."""
    from .detectors.video import detect_video as _impl
    return _impl(video_bytes, max_frames=max_frames)

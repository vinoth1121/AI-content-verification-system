"""AI Content Verification System — Detection Engine.

Public API (lazy where heavy deps are required):
    detect_text(text) -> dict
    detect_fake_news(text, title=None) -> dict
    detect_image(image_bytes) -> dict
    detect_audio(audio_bytes) -> dict          # lazy (librosa)
    detect_video(video_bytes) -> dict          # lazy (cv2)

Each function returns a dict with the following shape:
    {
        "label": str,            # human | ai_generated | deepfake | suspicious | authentic
        "confidence": float,     # 0.0 - 1.0
        "modality": str,
        "explanation": str,
        "features": dict,
        "heatmap_path": str | None,
        "flagged_segments": list[dict] | None,
    }
"""
from .engine import (
    detect_audio,
    detect_fake_news,
    detect_image,
    detect_text,
    detect_video,
)

__all__ = [
    "detect_text",
    "detect_fake_news",
    "detect_image",
    "detect_audio",
    "detect_video",
]
__version__ = "0.1.0"

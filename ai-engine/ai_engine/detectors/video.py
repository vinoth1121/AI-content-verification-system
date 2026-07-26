"""Video deepfake detector.

Strategy:
1. Open the video via OpenCV (temp-file fallback for non-seekable codecs).
2. Sample up to N frames uniformly across the timeline.
3. Run the image detector on each frame.
4. Aggregate: if more than 40% of sampled frames are flagged as
   "deepfake" or "suspicious", flag the whole video.
5. Temporal consistency: compute the std of per-frame confidence — large
   swings indicate splicing / lip-sync manipulation.
"""
from __future__ import annotations

import io
import math
import os
import tempfile

import cv2
import numpy as np

from ai_engine.detectors.image import detect_image
from ai_engine.explainability.explain import humanize_explain


def _sample_frames(video_bytes: bytes, max_frames: int = 8) -> list[bytes]:
    """Decode and uniformly sample frames as JPEG bytes."""
    fd, path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)
    try:
        with open(path, "wb") as f:
            f.write(video_bytes)
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise ValueError("Could not open video")
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total <= 0:
            total = max_frames
        step = max(1, total // max_frames)
        frames = []
        for i in range(0, total, step):
            if len(frames) >= max_frames:
                break
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ok, frame = cap.read()
            if not ok:
                continue
            ok, buf = cv2.imencode(".jpg", frame)
            if ok:
                frames.append(buf.tobytes())
        cap.release()
        return frames
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def detect_video(video_bytes: bytes, max_frames: int = 8) -> dict:
    frames = _sample_frames(video_bytes, max_frames=max_frames)
    if not frames:
        raise ValueError("Could not extract frames from video")

    per_frame = [detect_image(f) for f in frames]
    confs = [r["confidence"] for r in per_frame]
    flagged = sum(1 for r in per_frame if r["label"] in {"deepfake", "suspicious"})

    mean_conf = float(np.mean(confs))
    std_conf = float(np.std(confs))

    # Temporal inconsistency boost
    z = 2.0 * (flagged / len(per_frame)) + 1.5 * std_conf + 0.5 * mean_conf - 1.0
    confidence = 1.0 / (1.0 + math.exp(-z))

    if confidence >= 0.66:
        label = "deepfake"
    elif confidence >= 0.4:
        label = "suspicious"
    else:
        label = "authentic"

    positive = [
        f"flagged_frames={flagged}/{len(per_frame)}",
        f"mean_frame_confidence={mean_conf:.3f}",
        f"temporal_std={std_conf:.3f}",
    ]
    negative = []

    return {
        "label": label,
        "confidence": round(confidence, 4),
        "modality": "video",
        "explanation": humanize_explain(positive, negative),
        "features": {
            "frames_sampled": len(per_frame),
            "flagged_frames": flagged,
            "mean_frame_confidence": round(mean_conf, 4),
            "std_frame_confidence": round(std_conf, 4),
        },
        "heatmap_path": None,
        "flagged_segments": [
            {"frame_index": i, "confidence": c, "label": r["label"]}
            for i, (c, r) in enumerate(zip(confs, per_frame))
            if r["label"] != "authentic"
        ],
    }

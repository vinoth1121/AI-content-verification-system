"""Image deepfake detector using frequency-domain + noise-residual analysis.

Pipeline:
1. Decode bytes → RGB array via OpenCV.
2. Compute the 2D DCT of the luminance channel; AI-generated / GAN images
   typically leave characteristic high-frequency residue.
3. Compute noise residual (Laplacian) — synthetic images often have
   anomalously low or anomalously high local noise.
4. Channel-wise saturation histogram — diffusion-model images tend to
   over-saturate.
5. Combine into a single score via weighted sum.

Returns the standard dict shape. When `save_heatmap=True`, also writes
a PNG showing the residual magnitude (for the UI to display).
"""
from __future__ import annotations

import math
import os
import tempfile
from typing import Any

import cv2
import numpy as np

from ai_engine.explainability.explain import humanize_explanation


def _decode(image_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image (unsupported format or corrupt)")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def _dct_high_freq_energy(gray: np.ndarray) -> float:
    """Fraction of DCT energy in the top-right (high-freq) quadrant."""
    f = cv2.dct(np.float32(gray) / 255.0)
    h, w = f.shape
    hf = f[: h // 2, w // 2 :]  # high frequencies
    return float(np.abs(hf).sum() / (np.abs(f).sum() + 1e-9))


def _noise_residual(gray: np.ndarray) -> float:
    """Mean magnitude of Laplacian — proxy for local noise."""
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    return float(lap.var())


def _saturation_stats(rgb: np.ndarray) -> tuple[float, float]:
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    s = hsv[..., 1].astype(np.float32) / 255.0
    return float(s.mean()), float(s.std())


def _edge_density(gray: np.ndarray) -> float:
    edges = cv2.Canny(gray, 100, 200)
    return float(edges.sum() / (edges.size * 255))


def detect_image(image_bytes: bytes, *, save_heatmap: bool = False) -> dict[str, Any]:
    rgb = _decode(image_bytes)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    hf = _dct_high_freq_energy(gray)
    noise = _noise_residual(gray)
    s_mean, s_std = _saturation_stats(rgb)
    edge = _edge_density(gray)

    # Normalise & score
    # Synthetic images: higher HF energy, lower noise variance, higher saturation std
    z = (
        3.5 * hf                       # high-freq residue
        - 0.0001 * noise               # GAN images often have very low Laplacian variance
        + 2.0 * s_std                  # oversaturated
        - 5.0 * edge                   # synthetic images tend to have unnaturally clean edges
        - 0.5
    )
    confidence = 1.0 / (1.0 + math.exp(-z))

    if confidence >= 0.66:
        label = "deepfake"
    elif confidence >= 0.4:
        label = "suspicious"
    else:
        label = "authentic"

    heatmap_path = None
    if save_heatmap:
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        norm = cv2.normalize(np.abs(lap), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        heat = cv2.applyColorMap(norm, cv2.COLORMAP_JET)
        fd, path = tempfile.mkstemp(suffix=".png", prefix="heatmap_")
        os.close(fd)
        cv2.imwrite(path, heat)
        heatmap_path = path

    positive = [
        f"high_freq_energy={hf:.4f}",
        f"saturation_std={s_std:.4f}",
    ]
    negative = [
        f"noise_variance={noise:.1f}",
        f"edge_density={edge:.4f}",
    ]

    return {
        "label": label,
        "confidence": round(confidence, 4),
        "modality": "image",
        "explanation": humanize_explanation(positive, negative),
        "features": {
            "high_freq_energy": round(hf, 4),
            "noise_variance": round(noise, 2),
            "saturation_mean": round(s_mean, 4),
            "saturation_std": round(s_std, 4),
            "edge_density": round(edge, 4),
            "width": rgb.shape[1],
            "height": rgb.shape[0],
        },
        "heatmap_path": heatmap_path,
        "flagged_segments": None,
    }

"""Tests for the image detector."""
import cv2
import numpy as np
import pytest

from ai_engine.engine import detect_image


def _png_bytes(rgb: np.ndarray) -> bytes:
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    ok, buf = cv2.imencode(".png", bgr)
    assert ok
    return buf.tobytes()


def test_detect_image_synthetic_gradient():
    # A smooth gradient is the simplest "synthetic-looking" image.
    h, w = 256, 256
    grad = np.linspace(0, 255, w, dtype=np.uint8).reshape(1, w).repeat(h, axis=0)
    rgb = np.stack([grad, grad, grad], axis=-1)
    r = detect_image(_png_bytes(rgb))
    assert r["modality"] == "image"
    assert 0.0 <= r["confidence"] <= 1.0
    assert "high_freq_energy" in r["features"]


def test_detect_image_noisy_natural_like():
    # Add lots of random noise — should look "natural" to the detector.
    rng = np.random.default_rng(42)
    rgb = rng.integers(0, 256, size=(128, 128, 3), dtype=np.uint8)
    r = detect_image(_png_bytes(rgb))
    assert r["label"] in {"authentic", "suspicious", "deepfake"}


def test_detect_image_invalid_bytes_raises():
    with pytest.raises(ValueError):
        detect_image(b"not-an-image")

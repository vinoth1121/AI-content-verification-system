"""Audio deepfake detector using spectral analysis.

Pipeline:
1. Decode bytes via librosa (supports WAV/MP3/FLAC) → mono float32.
2. Compute MFCCs and the mel spectrogram.
3. Extract:
   - MFCC variance (synthetic voices tend to be smoother)
   - Spectral flux mean (AI voices often have unnaturally flat flux)
   - Pitch contour smoothness (proxy via fundamental frequency std)
   - Zero-crossing rate variance (synthetic voices tend to have low ZCR variance)
4. Score with a logistic-style combination.
"""
from __future__ import annotations

import io
import math

import librosa
import numpy as np

from ai_engine.explainability.explain import humanize_explanation


def _decode(audio_bytes: bytes, sr: int = 16000) -> tuple[np.ndarray, int]:
    y, _ = librosa.load(io.BytesIO(audio_bytes), sr=sr, mono=True)
    if y.size == 0:
        raise ValueError("Empty audio after decoding")
    return y, sr


def detect_audio(audio_bytes: bytes) -> dict:
    y, sr = _decode(audio_bytes)

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    mfcc_var = float(mfcc.var(axis=1).mean())

    # Spectral flux
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    flux_mean = float(onset_env.mean())
    flux_std = float(onset_env.std())

    # Pitch
    f0, _, _ = librosa.pyin(y, sr=sr, fmin=80, fmax=400, frame_length=2048)
    f0_clean = f0[~np.isnan(f0)] if f0 is not None else np.array([])
    pitch_std = float(f0_clean.std()) if f0_clean.size else 0.0

    # Zero-crossing rate
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    zcr_var = float(zcr.var())

    # Score
    z = (
        -0.5 * mfcc_var                # smooth MFCC → AI
        - 0.05 * flux_std              # flat flux → AI
        - 0.2 * pitch_std              # very stable pitch → AI
        - 200.0 * zcr_var              # very low ZCR variance → AI
        + 0.5
    )
    confidence = 1.0 / (1.0 + math.exp(-z))

    if confidence >= 0.66:
        label = "deepfake"
    elif confidence >= 0.4:
        label = "suspicious"
    else:
        label = "authentic"

    positive = [
        f"low_mfcc_variance={mfcc_var:.3f}",
        f"low_zcr_variance={zcr_var:.6f}",
    ]
    negative = [
        f"pitch_std={pitch_std:.2f}",
        f"flux_std={flux_std:.4f}",
    ]

    return {
        "label": label,
        "confidence": round(confidence, 4),
        "modality": "audio",
        "explanation": humanize_explanation(positive, negative),
        "features": {
            "mfcc_variance": round(mfcc_var, 4),
            "spectral_flux_mean": round(flux_mean, 4),
            "spectral_flux_std": round(flux_std, 4),
            "pitch_std": round(pitch_std, 4),
            "zcr_variance": round(zcr_var, 6),
            "duration_sec": round(len(y) / sr, 2),
            "sample_rate": sr,
        },
        "heatmap_path": None,
        "flagged_segments": [],
    }

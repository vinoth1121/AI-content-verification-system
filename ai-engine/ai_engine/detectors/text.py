"""AI-text detector based on statistical stylometry.

Weights are learned by logistic regression on a labelled corpus — see
`train_text.py`. Falls back to hand-tuned baseline if weights file missing.
"""
from __future__ import annotations

import json
import logging
import math
from pathlib import Path

from ai_engine.explainability.explain import humanize_explanation
from ai_engine.utils.stats import extract_all

logger = logging.getLogger(__name__)


def _sigmoid(x: float) -> float:
    if x > 35:
        return 1.0
    if x < -35:
        return 0.0
    return 1.0 / (1.0 + math.exp(-x))


def _normalise(features: dict[str, float]) -> dict[str, float]:
    return {
        "burstiness": min(max(features["burstiness"] / 1.2, 0.0), 1.0),
        "lexical_diversity": min(max(features["lexical_diversity"], 0.0), 1.0),
        "char_entropy": min(max((features["char_entropy"] - 3.5) / 1.5, 0.0), 1.0),
        "function_word_ratio": min(max((features["function_word_ratio"] - 0.25) / 0.30, 0.0), 1.0),
        "punctuation_ratio": min(max(features["punctuation_ratio"] / 0.15, 0.0), 1.0),
        "repetitive_trigram_density": min(max(features["repetitive_trigram_density"] / 0.4, 0.0), 1.0),
        "mean_sentence_length": min(max((features["mean_sentence_length"] - 5) / 20, 0.0), 1.0),
    }


_FALLBACK_WEIGHTS = {
    "burstiness": -1.6, "lexical_diversity": -1.4, "char_entropy": 0.6,
    "function_word_ratio": 0.4, "punctuation_ratio": -0.3,
    "repetitive_trigram_density": 1.8, "mean_sentence_length": 0.6,
}
_FALLBACK_BIAS = -0.3


def _load_weights() -> tuple[dict[str, float], float]:
    weights_path = Path(__file__).resolve().parent / "text_weights.json"
    if not weights_path.exists():
        logger.info("text_weights.json not found — using hand-tuned baseline weights")
        return _FALLBACK_WEIGHTS, _FALLBACK_BIAS
    try:
        data = json.loads(weights_path.read_text())
        weights = data["weights"]
        bias = data["bias"]
        for k in _FALLBACK_WEIGHTS:
            if k not in weights:
                weights[k] = _FALLBACK_WEIGHTS[k]
        return weights, bias
    except Exception as exc:
        logger.warning("Failed to load text_weights.json (%s) — using baseline", exc)
        return _FALLBACK_WEIGHTS, _FALLBACK_BIAS


_WEIGHTS, _BIAS = _load_weights()


def detect_text(text: str) -> dict:
    raw = extract_all(text)
    features = _normalise(raw)

    z = _BIAS + sum(features.get(k, 0.0) * w for k, w in _WEIGHTS.items())
    confidence = _sigmoid(z)

    if confidence >= 0.66:
        label = "ai_generated"
    elif confidence >= 0.4:
        label = "suspicious"
    else:
        label = "human"

    contributions = sorted(
        ((k, features[k] * _WEIGHTS.get(k, 0.0)) for k in features),
        key=lambda kv: abs(kv[1]), reverse=True,
    )[:4]
    positive = [f"{k}={features[k]:.2f}" for k, c in contributions if c > 0]
    negative = [f"{k}={features[k]:.2f}" for k, c in contributions if c < 0]

    return {
        "label": label,
        "confidence": round(confidence, 4),
        "modality": "text",
        "explanation": humanize_explanation(positive, negative),
        "features": {k: round(v, 4) for k, v in raw.items()},
        "heatmap_path": None,
        "flagged_segments": None,
    }

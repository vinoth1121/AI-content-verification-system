"""AI-text detector based on statistical stylometry.

Features are normalised to plausible ranges before scoring. The scorer is a
logistic-regression-style linear combination whose weights are hand-tuned
from public stylometry research (burstiness, lexical diversity, repetitive
n-gram density are the strongest signals).

This is deliberately a CPU-only baseline. The architecture allows swapping
in a transformer-based detector (e.g. RoBERTa fine-tuned on HC3) by
replacing the body of `detect_text` — the calling code (backend) is unaffected.
"""
from __future__ import annotations

import math

from ai_engine.explainability.explain import humanize_explanation
from ai_engine.utils.stats import extract_all


def _sigmoid(x: float) -> float:
    if x > 35:
        return 1.0
    if x < -35:
        return 0.0
    return 1.0 / (1.0 + math.exp(-x))


def _normalise(features: dict[str, float]) -> dict[str, float]:
    """Map raw features into a 0–1 range so weights can be compared."""
    return {
        # Burstiness typically 0–1.5 for English; higher = more human.
        "burstiness": min(max(features["burstiness"] / 1.2, 0.0), 1.0),
        # Lexical diversity 0–1 already.
        "lexical_diversity": min(max(features["lexical_diversity"], 0.0), 1.0),
        # Character entropy typically 3.5–5.0 for English; AI text leans higher.
        "char_entropy": min(max((features["char_entropy"] - 3.5) / 1.5, 0.0), 1.0),
        # Function-word ratio typically 0.25–0.55; AI tends slightly higher.
        "function_word_ratio": min(max((features["function_word_ratio"] - 0.25) / 0.30, 0.0), 1.0),
        # Punctuation ratio 0–0.15 typically.
        "punctuation_ratio": min(max(features["punctuation_ratio"] / 0.15, 0.0), 1.0),
        # Repetitive trigram density 0–0.4 typically; high = AI.
        "repetitive_trigram_density": min(max(features["repetitive_trigram_density"] / 0.4, 0.0), 1.0),
        # Mean sentence length 5–25 words typically; very long → AI.
        "mean_sentence_length": min(max((features["mean_sentence_length"] - 5) / 20, 0.0), 1.0),
    }


# Weights on normalised features. Positive = AI signal, negative = human signal.
_WEIGHTS = {
    "burstiness": -1.6,                # humans burst more
    "lexical_diversity": -1.4,         # humans use more diverse vocabulary
    "char_entropy": 0.6,               # AI tends to have slightly higher entropy
    "function_word_ratio": 0.4,        # AI slightly overuses function words
    "punctuation_ratio": -0.3,         # humans punctuate a bit more variably
    "repetitive_trigram_density": 1.8, # repetition is the strongest AI signal
    "mean_sentence_length": 0.6,       # AI tends slightly longer
}

_BIAS = -0.3  # mild prior toward human (most text on the internet is human)


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

    # Surface the top contributing features (signed by weight) for the explanation
    contributions = sorted(
        ((k, features[k] * _WEIGHTS.get(k, 0.0)) for k in features),
        key=lambda kv: abs(kv[1]),
        reverse=True,
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

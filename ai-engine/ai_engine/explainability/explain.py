"""Common helpers for explainability reporting."""
from __future__ import annotations


def top_features(features: dict[str, float], n: int = 3) -> list[tuple[str, float]]:
    """Return the top-N features by absolute value."""
    return sorted(features.items(), key=lambda kv: abs(kv[1]), reverse=True)[:n]


def humanize_explanation(positive_signals: list[str], negative_signals: list[str]) -> str:
    """Compose a short human-readable explanation.

    `positive_signals` are signals pointing to AI/manipulation; `negative_signals`
    point to human/authentic content.
    """
    parts = []
    if positive_signals:
        parts.append("Signals suggesting AI-generation: " + "; ".join(positive_signals) + ".")
    if negative_signals:
        parts.append("Signals suggesting human authorship: " + "; ".join(negative_signals) + ".")
    if not parts:
        return "No strong stylistic signals detected."
    return " ".join(parts)

"""Fake-news detector.

Combines:
- Stylometric cues (sensationalism, hedging, all-caps density)
- Claim structure (presence of source attribution, quantifiers, negations)
- A small lexicon of clickbait / sensational phrases

Returns the same dict shape as the other detectors. The confidence is
*not* a fact-check — it is a probability that the article exhibits
misinformation-style linguistic patterns. Real fact-checking would require
a retrieval step against trusted sources (Phase 2 roadmap).
"""
from __future__ import annotations

import re

from ai_engine.explainability.explain import humanize_explanation
from ai_engine.utils.stats import extract_all

_CLICKBAIT = re.compile(
    r"\b(shocking|you won't believe|mind[- ]blowing|breaking|exposed|secret|"
    r"doctors hate|this one trick|what happens next|must see|gone wrong)\b",
    re.IGNORECASE,
)
_ALL_CAPS_WORD = re.compile(r"\b[A-Z]{4,}\b")
_HEDGE = re.compile(
    r"\b(might|could|allegedly|reportedly|some say|sources claim|rumour has it|"
    r"supposedly|apparently|possibly|perhaps|maybe)\b",
    re.IGNORECASE,
)
_SOURCE_ATTRIBUTION = re.compile(
    r"\b(according to|said|stated|reported by|per the|in a statement)\b",
    re.IGNORECASE,
)
_NEGATION = re.compile(r"\b(not|never|no one|nobody|denied|refuted|debunked)\b", re.IGNORECASE)
_NUMBER = re.compile(r"\b\d+\b")


def detect_fake_news(text: str, title: str | None = None) -> dict:
    combined = f"{title or ''}\n{text}".strip()
    features = extract_all(combined)

    clickbait_hits = len(_CLICKBAIT.findall(combined))
    all_caps = len(_ALL_CAPS_WORD.findall(combined))
    hedge_count = len(_HEDGE.findall(combined))
    source_count = len(_SOURCE_ATTRIBUTION.findall(combined))
    negation_count = len(_NEGATION.findall(combined))
    number_count = len(_NUMBER.findall(combined))

    # Score: more sensational + more hedging + less attribution → higher suspicion
    z = (
        0.8 * clickbait_hits
        + 0.5 * all_caps
        + 0.4 * hedge_count
        - 1.0 * source_count            # citing sources lowers suspicion
        - 0.2 * negation_count
        + 1.0 * features.get("repetitive_trigram_density", 0.0)
        + 0.4 * (features.get("punctuation_ratio", 0.0) > 0.12)  # excessive ! ?
        - 1.0           # prior toward "authentic"
    )

    import math
    confidence = 1.0 / (1.0 + math.exp(-z))

    if confidence >= 0.66:
        label = "suspicious"
    elif confidence >= 0.4:
        label = "suspicious"
    else:
        label = "authentic"

    positive = [
        f"clickbait_phrases={clickbait_hits}",
        f"all_caps_words={all_caps}",
        f"hedge_words={hedge_count}",
    ]
    negative = [
        f"source_attributions={source_count}",
        f"negations={negation_count}",
        f"numbers={number_count}",
    ]

    return {
        "label": label,
        "confidence": round(confidence, 4),
        "modality": "fake_news",
        "explanation": humanize_explanation(positive, negative),
        "features": {
            "clickbait_phrases": clickbait_hits,
            "all_caps_words": all_caps,
            "hedge_words": hedge_count,
            "source_attributions": source_count,
            "negations": negation_count,
            "numbers": number_count,
            "burstiness": features["burstiness"],
            "lexical_diversity": features["lexical_diversity"],
        },
        "heatmap_path": None,
        "flagged_segments": None,
    }

"""Statistical text utilities — shared by text + fake-news detectors.

These features are deliberately lightweight (CPU-only, no LLM calls) so the
engine runs anywhere. They capture well-known stylometric signals:
- Burstiness (variance of sentence length) — humans burst, LLMs smooth
- Lexical diversity (type-token ratio) — humans reuse words less
- Perplexity proxy via per-character entropy — LLMs are more predictable
- Punctuation ratio, function-word ratio, repetitive n-gram density
"""
from __future__ import annotations

import math
import re
from collections import Counter

_SENTENCE_SPLIT = re.compile(r"[.!?]+(?:\s+|$)")
_WORD_SPLIT = re.compile(r"[A-Za-z']+")
_FUNCTION_WORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at", "by",
    "for", "with", "as", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
}


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]


def split_words(text: str) -> list[str]:
    return [w.lower() for w in _WORD_SPLIT.findall(text)]


def burstiness(sentences: list[str]) -> float:
    """Coefficient of variation of sentence lengths (words)."""
    if len(sentences) < 2:
        return 0.0
    lengths = [len(split_words(s)) for s in sentences]
    mean = sum(lengths) / len(lengths)
    if mean == 0:
        return 0.0
    var = sum((l - mean) ** 2 for l in lengths) / len(lengths)
    return math.sqrt(var) / mean


def lexical_diversity(words: list[str]) -> float:
    """Type-token ratio. Lower = more repetitive (LLM-ish)."""
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def char_entropy(text: str) -> float:
    """Shannon entropy over characters. Lower → more predictable → LLM-ish."""
    if not text:
        return 0.0
    counts = Counter(text)
    total = sum(counts.values())
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def function_word_ratio(words: list[str]) -> float:
    if not words:
        return 0.0
    return sum(1 for w in words if w in _FUNCTION_WORDS) / len(words)


def punctuation_ratio(text: str) -> float:
    if not text:
        return 0.0
    return sum(1 for c in text if c in ".,;:!?-—\"'()[]") / len(text)


def repetitive_ngram_density(words: list[str], n: int = 3) -> float:
    """Fraction of n-grams that repeat. LLMs tend to repeat trigrams more."""
    if len(words) < n:
        return 0.0
    grams = [tuple(words[i : i + n]) for i in range(len(words) - n + 1)]
    if not grams:
        return 0.0
    return 1 - len(set(grams)) / len(grams)


def mean_sentence_length(sentences: list[str]) -> float:
    if not sentences:
        return 0.0
    return sum(len(split_words(s)) for s in sentences) / len(sentences)


def extract_all(text: str) -> dict[str, float]:
    """Compute the full feature vector for a text sample."""
    sents = split_sentences(text)
    words = split_words(text)
    return {
        "burstiness": burstiness(sents),
        "lexical_diversity": lexical_diversity(words),
        "char_entropy": char_entropy(text),
        "function_word_ratio": function_word_ratio(words),
        "punctuation_ratio": punctuation_ratio(text),
        "repetitive_trigram_density": repetitive_ngram_density(words, 3),
        "mean_sentence_length": mean_sentence_length(sents),
        "word_count": len(words),
    }

"""Tests for the calibrated text detector."""
from ai_engine.detectors.text import _load_weights
from ai_engine.engine import detect_text


def test_weights_loaded_from_json():
    weights, bias = _load_weights()
    assert bias > 0, f"Expected learned bias > 0, got {bias}"
    assert weights["mean_sentence_length"] > 1.0


def test_detect_text_human_short_low_confidence():
    r = detect_text("I went to the store. They were out of milk. Got eggs instead.")
    assert r["confidence"] < 0.5
    assert r["label"] == "human"


def test_detect_text_human_casual_low_confidence():
    r = detect_text("Coffee. Code. More coffee. Debug. Repeat.")
    assert r["confidence"] < 0.3
    assert r["label"] == "human"


def test_detect_text_ai_formal_high_confidence():
    text = (
        "It is important to note that this system represents a comprehensive approach "
        "to addressing the multifaceted challenges inherent in modern content verification. "
        "Furthermore, the implementation of said framework necessitates a thorough understanding "
        "of the underlying methodologies."
    )
    r = detect_text(text)
    assert r["confidence"] > 0.7
    assert r["label"] == "ai_generated"


def test_detect_text_ai_connectives_high_confidence():
    text = (
        "In conclusion, the aforementioned analysis demonstrates that the proposed methodology "
        "offers significant advantages over traditional approaches. Moreover, the results indicate "
        "a substantial improvement in overall accuracy and reliability."
    )
    r = detect_text(text)
    assert r["confidence"] > 0.6
    assert r["label"] == "ai_generated"


def test_detect_text_features_populated():
    r = detect_text("The system shall endeavour to provide a comprehensive overview.")
    feats = r["features"]
    for k in ("burstiness", "lexical_diversity", "char_entropy", "word_count"):
        assert k in feats


def test_detect_text_explanation_mentions_top_features():
    r = detect_text("It is important to note that this is a comprehensive framework.")
    assert "Signals suggesting" in r["explanation"]

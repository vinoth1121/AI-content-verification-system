"""Tests for the text + fake-news detectors."""
from ai_engine.engine import detect_fake_news, detect_text


def test_detect_text_human_short():
    r = detect_text("I went to the store. Bought milk. Walked home.")
    assert r["modality"] == "text"
    assert 0.0 <= r["confidence"] <= 1.0
    assert "features" in r
    assert r["label"] in {"human", "ai_generated", "suspicious"}


def test_detect_text_features_populated():
    r = detect_text("The system shall endeavour to provide a comprehensive overview.")
    feats = r["features"]
    for k in ("burstiness", "lexical_diversity", "char_entropy", "word_count"):
        assert k in feats


def test_detect_fake_news_clickbait_increases_confidence():
    plain = detect_fake_news("The council met on Tuesday to discuss the budget proposal.")
    bait = detect_fake_news("SHOCKING: Doctors HATE this one trick for losing weight!")
    assert bait["confidence"] > plain["confidence"]
    assert bait["label"] == "suspicious"

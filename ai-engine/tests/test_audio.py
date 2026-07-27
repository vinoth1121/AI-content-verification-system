"""Tests for the audio deepfake detector."""
import io

import numpy as np
import soundfile as sf
import pytest

from ai_engine.engine import detect_audio


def _wav_bytes(samples: np.ndarray, sr: int = 16000) -> bytes:
    buf = io.BytesIO()
    sf.write(buf, samples, sr, format="WAV", subtype="PCM_16")
    return buf.getvalue()


def _pure_tone(freq: float = 440.0, duration: float = 2.0, sr: int = 16000) -> np.ndarray:
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * freq * t)


def _white_noise(duration: float = 2.0, sr: int = 16000, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return 0.1 * rng.standard_normal(int(sr * duration))


def _frequency_sweep(duration: float = 2.0, sr: int = 16000) -> np.ndarray:
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    freq = 200 + (2000 - 200) * t / duration
    phase = 2 * np.pi * np.cumsum(freq) / sr
    return 0.5 * np.sin(phase)


def test_detect_audio_pure_tone_returns_result():
    audio = _wav_bytes(_pure_tone())
    r = detect_audio(audio)
    assert r["modality"] == "audio"
    assert 0.0 <= r["confidence"] <= 1.0
    assert r["label"] in {"authentic", "suspicious", "deepfake"}
    assert "mfcc_variance" in r["features"]
    assert "duration_sec" in r["features"]


def test_detect_audio_white_noise_natural_like():
    noise = detect_audio(_wav_bytes(_white_noise()))
    for k in ("mfcc_variance", "spectral_flux_mean", "pitch_std", "zcr_variance"):
        assert k in noise["features"]
        assert noise["features"][k] >= 0


def test_detect_audio_pure_tone_low_pitch_variation():
    tone = detect_audio(_wav_bytes(_pure_tone()))
    assert tone["features"]["pitch_std"] < 5.0


def test_detect_audio_chirp_has_pitch_variation():
    audio = _wav_bytes(_frequency_sweep())
    r = detect_audio(audio)
    assert r["features"]["pitch_std"] > 0


def test_detect_audio_empty_bytes_raises():
    with pytest.raises(Exception):
        detect_audio(b"")


def test_detect_audio_invalid_bytes_raises():
    with pytest.raises(Exception):
        detect_audio(b"not-audio-data-just-text-bytes")

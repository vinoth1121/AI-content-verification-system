# AI Engine

Standalone Python package providing the detection primitives consumed by the
backend. Designed to be importable as a regular Python package so it can run
in-process with the API or as a sidecar service.

## Layout

```
ai-engine/
├── ai_engine/
│   ├── __init__.py
│   ├── engine.py            # Public API: detect_text / detect_image / ...
│   ├── detectors/
│   │   ├── text.py
│   │   ├── fake_news.py
│   │   ├── image.py
│   │   ├── audio.py
│   │   └── video.py
│   ├── explainability/
│   │   └── explain.py
│   └── utils/
│       └── stats.py
├── tests/
├── requirements.txt
└── README.md
```

## Design Principles

1. **CPU-friendly by default.** No GPU required for the baseline detectors —
   they use statistical / signal-processing features that run in milliseconds.
2. **Pluggable models.** Each detector exposes a `detect(...)` function; swap
   the implementation with a HuggingFace / ONNX variant without touching callers.
3. **Explainable.** Every detector returns a `features` dict so the UI can
   surface "why" alongside the confidence score.
4. **Deterministic.** Same input → same output, every time.

## Install

```bash
pip install -r requirements.txt
```

## Usage

```python
from ai_engine.engine import detect_text
result = detect_text("This is a sentence that may or may not be AI-generated.")
# {'label': 'ai_generated', 'confidence': 0.72, 'explanation': '...', 'features': {...}}
```

"""Train a logistic regression on stylometric features."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from ai_engine.detectors._corpus import load_corpus
from ai_engine.detectors.text import _normalise
from ai_engine.utils.stats import extract_all

FEATURE_ORDER = [
    "burstiness", "lexical_diversity", "char_entropy",
    "function_word_ratio", "punctuation_ratio",
    "repetitive_trigram_density", "mean_sentence_length",
]


def featurise(text: str) -> np.ndarray:
    raw = extract_all(text)
    norm = _normalise(raw)
    return np.array([norm[k] for k in FEATURE_ORDER], dtype=np.float64)


def main() -> None:
    corpus = load_corpus()
    print(f"Loaded corpus: {len(corpus)} samples")

    X = np.array([featurise(t) for t, _ in corpus])
    y = np.array([label for _, label in corpus], dtype=np.int32)

    print(f"Class balance: human={int((y==0).sum())}, ai={int((y==1).sum())}")
    print(f"Feature matrix: {X.shape}")

    model = LogisticRegression(
        C=1.0, solver="lbfgs", max_iter=1000, class_weight="balanced",
    )

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    y_pred_cv = cross_val_predict(model, X, y, cv=skf, method="predict")
    y_proba_cv = cross_val_predict(model, X, y, cv=skf, method="predict_proba")[:, 1]

    acc = accuracy_score(y, y_pred_cv)
    auc = roc_auc_score(y, y_proba_cv)
    print(f"\n=== Cross-validated metrics (5-fold) ===")
    print(f"Accuracy: {acc:.4f}")
    print(f"ROC AUC:  {auc:.4f}")
    print(classification_report(y, y_pred_cv, target_names=["human", "ai_generated"]))

    model.fit(X, y)
    weights = dict(zip(FEATURE_ORDER, model.coef_[0].tolist()))
    bias = float(model.intercept_[0])

    print(f"\n=== Learned weights ===")
    for k, v in sorted(weights.items(), key=lambda kv: abs(kv[1]), reverse=True):
        print(f"  {k:30s}  {v:+.4f}")
    print(f"  {'bias':30s}  {bias:+.4f}")

    out_dir = Path(__file__).resolve().parent
    weights_path = out_dir / "text_weights.json"
    weights_path.write_text(json.dumps({"weights": weights, "bias": bias}, indent=2))
    print(f"\nWrote weights → {weights_path}")

    metrics_path = out_dir / "text_metrics.json"
    metrics_path.write_text(json.dumps({
        "accuracy": float(acc), "roc_auc": float(auc),
        "n_samples": len(corpus), "feature_order": FEATURE_ORDER,
    }, indent=2))
    print(f"Wrote metrics → {metrics_path}")


if __name__ == "__main__":
    main()

"""Pytest configuration — adds the ai-engine root to sys.path so tests can
import the `ai_engine` package without requiring an editable install.

This mirrors the pattern used by `backend/tests/conftest.py`.
"""
import sys
from pathlib import Path

# Add the ai-engine root (parent of tests/) to sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

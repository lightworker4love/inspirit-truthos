from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "apps/truth-api"))

from app.dimension_classifier import classify_dimensions


def test_dimension_classifier_attaches_low_confidence_metadata():
    result = classify_dimensions("太短")

    assert list(result) == ["motive", "cognition", "emotion"]
    assert result.confidence == 0.0
    assert result.low_confidence is True
    assert result.low_confidence_reason == "input_too_short"


def test_dimension_classifier_preserves_rankings_with_confidence_metadata():
    result = classify_dimensions("我在關係裡總是想控制對方，也很怕失去對方")

    assert result[0] == "relationship"
    assert result.confidence > 0.35
    assert result.low_confidence is False
    assert result.low_confidence_reason is None

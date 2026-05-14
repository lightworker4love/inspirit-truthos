from __future__ import annotations

from packages.truth_schema.validators import validate_non_dual_axiom


def test_validator_flags_subjective_axiom():
    errors = validate_non_dual_axiom(
        {
            "axiom": "Truth works only if you believe it.",
            "worldly_example": "Gravity pulls bodies.",
            "spiritual_example": "Avoided patterns repeat.",
            "objectivity_statement": "This principle operates even if the person does not know it.",
        }
    )

    assert any("if you believe" in error for error in errors)


def test_validator_requires_non_dual_examples():
    errors = validate_non_dual_axiom({"axiom": "Truth remains true."})

    assert "Missing worldly_example: axiom must demonstrate in material domain" in errors
    assert "Missing spiritual_example: axiom must demonstrate in spiritual domain" in errors
    assert "Missing objectivity_statement: must assert existence independent of belief" in errors


def test_seed_loader_enhances_legacy_principle_before_validation():
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "apps/truth-api"))

    from app.seed_loader import _enhance_core_principle

    principle = _enhance_core_principle(
        {
            "id": "cp_cau_001",
            "dimension_code": "causality",
            "code": "CAU_001",
            "title": "因果盲點",
            "axiom": "忽略選擇時，因與果之間的責任會被切斷。",
        }
    )

    assert validate_non_dual_axiom(principle) == []
    assert principle["truth_property_primary"] == "consistency"

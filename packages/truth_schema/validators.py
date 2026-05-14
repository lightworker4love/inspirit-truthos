from __future__ import annotations

from typing import Any


def validate_non_dual_axiom(principle: dict[str, Any]) -> list[str]:
    errors = []

    if not principle.get("worldly_example"):
        errors.append("Missing worldly_example: axiom must demonstrate in material domain")

    if not principle.get("spiritual_example"):
        errors.append("Missing spiritual_example: axiom must demonstrate in spiritual domain")

    if not principle.get("objectivity_statement"):
        errors.append("Missing objectivity_statement: must assert existence independent of belief")

    axiom = principle.get("axiom", "")
    subjective_markers = ["if you believe", "when you think", "if you feel", "depending on"]
    for marker in subjective_markers:
        if marker.lower() in axiom.lower():
            errors.append(f"Axiom contains subjective marker '{marker}' - Truth is objective")

    return errors


def validate_principle_batch(
    principles: list[dict[str, Any]],
    fail_threshold: float = 0.2,
) -> list[dict[str, Any]]:
    warnings = []
    for principle in principles:
        errors = validate_non_dual_axiom(principle)
        if errors:
            warnings.append(
                {
                    "id": principle.get("id") or principle.get("code"),
                    "axiom": principle.get("axiom"),
                    "errors": errors,
                }
            )

    if principles and (len(warnings) / len(principles)) > fail_threshold:
        raise ValueError(
            "Non-dual axiom validation failed: "
            f"{len(warnings)}/{len(principles)} principles exceeded {fail_threshold:.0%} threshold"
        )

    return warnings

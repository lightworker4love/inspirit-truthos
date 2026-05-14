from __future__ import annotations

from typing import Any


DEFAULT_OBJECTIVITY_STATEMENT = (
    "This principle operates regardless of whether the person knows, "
    "believes, or imagines it."
)


def build_truth_map(
    user_message: str,
    top_puzzle: dict[str, Any] | None,
    matched_principle: dict[str, Any] | None,
    soul_map_patterns: list,
    action: str,
) -> dict[str, Any]:
    puzzle = top_puzzle or {}
    principle = matched_principle or {}
    return {
        "fact_layer": puzzle.get("fact_layer") or extract_fact_layer(user_message),
        "reality_layer": (
            puzzle.get("reality_layer")
            or summarize_soul_map_patterns(soul_map_patterns)
            or "Soul Map not yet built for this user"
        ),
        "truth_claim": {
            "axiom": principle.get("axiom") or puzzle.get("truth_reframe") or "",
            "objectivity_statement": principle.get("objectivity_statement")
            or DEFAULT_OBJECTIVITY_STATEMENT,
            "worldly_example": principle.get("worldly_example"),
            "spiritual_example": principle.get("spiritual_example"),
        },
        "wisdom_anchor": action,
    }


def extract_fact_layer(message: str) -> str:
    stripped = " ".join(message.strip().split())
    return stripped[:240]


def summarize_soul_map_patterns(patterns: list) -> str:
    if not patterns:
        return ""
    first = patterns[0]
    if isinstance(first, str):
        return first
    if isinstance(first, dict):
        for key in ("pattern", "summary", "name", "description"):
            value = first.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return str(first)

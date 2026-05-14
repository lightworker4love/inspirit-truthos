from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/truth-api"))

from app.truth_map import build_truth_map


def test_truth_map_contains_four_layers():
    truth_map = build_truth_map(
        user_message="我最近感覺很疲憊，什麼都提不起勁",
        top_puzzle={"fact_layer": "感覺疲憊", "reality_layer": "能量長期被壓抑"},
        matched_principle={
            "axiom": "情緒停在壓抑時，感受就難以指向真正需要。",
            "objectivity_statement": "This principle operates even if the person does not know it.",
            "worldly_example": "Fatigue appears when recovery is ignored.",
            "spiritual_example": "Suppressed needs continue asking to be seen.",
        },
        soul_map_patterns=[],
        action="今天先承認一個真實需要。",
    )

    assert truth_map["fact_layer"] == "感覺疲憊"
    assert truth_map["reality_layer"] == "能量長期被壓抑"
    assert truth_map["truth_claim"]["axiom"].startswith("情緒停在壓抑")
    assert truth_map["truth_claim"]["objectivity_statement"]
    assert truth_map["wisdom_anchor"] == "今天先承認一個真實需要。"

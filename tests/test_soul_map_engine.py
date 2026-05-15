from __future__ import annotations

import math
import sqlite3
import sys
from pathlib import Path
from unittest.mock import MagicMock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/truth-api"))

from app.soul_map_engine import EVOLUTION_STAGES, SoulMapEngine


def make_engine():
    db = MagicMock()
    db.fetchone.return_value = None
    db.fetchall.return_value = []
    engine = SoulMapEngine(db_client=db)
    return engine, db


def test_create_empty_soul_map():
    engine, _ = make_engine()
    soul_map = engine._create_empty("user-001", "2026-01-01T00:00:00Z")
    assert soul_map["evolution_stage"] == "awakening"
    assert soul_map["recurring_patterns"] == []
    assert soul_map["pattern_weights"] == {}


def test_pattern_weight_increases_with_frequency():
    engine, _ = make_engine()
    soul_map = engine._create_empty("user-001", "2026-01-01T00:00:00Z")
    soul_map, _ = engine._update_pattern_weight(soul_map, "control_pattern", "2026-01-01")
    soul_map, _ = engine._update_pattern_weight(soul_map, "control_pattern", "2026-01-02")
    soul_map, _ = engine._update_pattern_weight(soul_map, "control_pattern", "2026-01-03")
    weight = soul_map["pattern_weights"]["control_pattern"]
    assert weight["frequency"] == 3
    assert weight["weight"] == round(1 - math.exp(-3 / 5), 4)


def test_pattern_weight_asymptotically_approaches_1():
    engine, _ = make_engine()
    soul_map = engine._create_empty("user-001", "2026-01-01T00:00:00Z")
    for index in range(50):
        soul_map, _ = engine._update_pattern_weight(
            soul_map, "old_pattern", f"2026-01-{index + 1:02d}"
        )
    weight = soul_map["pattern_weights"]["old_pattern"]["weight"]
    assert weight < 1.0
    assert weight > 0.99


def test_evolution_stage_advances_with_truth_shifts():
    engine, _ = make_engine()
    soul_map = engine._create_empty("user-001", "2026-01-01T00:00:00Z")
    assert engine._evaluate_evolution_stage(soul_map) == "awakening"
    soul_map["recurring_patterns"] = [{"id": "p1", "description": "test"}]
    soul_map["last_truth_shift_at"] = "2026-01-02"
    soul_map["pattern_weights"] = {"p1": {"frequency": 3, "weight": 0.45}}
    soul_map["integrated_dimensions"] = ["causality"]
    soul_map["evolution_history"] = [{"x": index} for index in range(3)]
    stage = engine._evaluate_evolution_stage(soul_map)
    assert stage in EVOLUTION_STAGES
    assert EVOLUTION_STAGES.index(stage) >= 2


def test_blind_spot_severity_calculation():
    engine, _ = make_engine()
    assert engine._calculate_severity(1, ["relationship"]) == "low"
    assert engine._calculate_severity(2, ["relationship"]) == "medium"
    assert engine._calculate_severity(4, ["relationship", "career"]) == "high"
    assert engine._calculate_severity(7, ["relationship"]) == "critical"
    assert engine._calculate_severity(2, ["relationship", "career", "self-worth"]) == "critical"


def test_hard_case_not_triggered_on_empty_map():
    engine, db = make_engine()
    db.fetchone.return_value = None
    result = engine.detect_hard_case("user-new")
    assert result["is_hard_case"] is False


def test_hard_case_triggered_on_stuck_pattern():
    engine, db = make_engine()
    soul_map = engine._create_empty("user-stuck", "2026-01-01")
    for index in range(6):
        soul_map, _ = engine._update_pattern_weight(
            soul_map, "rejection_pattern", f"2026-01-{index + 1:02d}"
        )
    engine.get_soul_map = MagicMock(return_value=soul_map)
    db.fetchall.return_value = []
    result = engine.detect_hard_case("user-stuck")
    assert result["is_hard_case"] is True
    assert any("5+" in reason for reason in result["reasons"])


def test_get_primary_pattern_returns_highest_weight():
    engine, _ = make_engine()
    soul_map = engine._create_empty("user-001", "2026-01-01")
    soul_map["recurring_patterns"] = [
        {"id": "p1", "description": "Control pattern"},
        {"id": "p2", "description": "Abandonment pattern"},
    ]
    soul_map["pattern_weights"] = {
        "p1": {"frequency": 2, "weight": 0.33},
        "p2": {"frequency": 5, "weight": 0.63},
    }
    engine.get_soul_map = MagicMock(return_value=soul_map)
    result = engine.get_primary_pattern("user-001")
    assert "Abandonment" in result


def test_update_from_query_result_persists_new_soul_map(tmp_path):
    db_path = tmp_path / "truthos.db"
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        connection.executescript(
            """
            CREATE TABLE soulmaps (
              id TEXT PRIMARY KEY,
              userid TEXT NOT NULL UNIQUE,
              recurringpatternsjson TEXT,
              limitingbeliefsjson TEXT,
              emotionalsignaturesjson TEXT,
              activelessonsjson TEXT,
              evolutionstage TEXT,
              lasttruthshiftat TEXT,
              createdat TEXT NOT NULL,
              updatedat TEXT NOT NULL,
              patternweightsjson TEXT,
              integrateddimensionsjson TEXT,
              transcendedpatternsjson TEXT,
              evolutionhistoryjson TEXT,
              soulmapsummary TEXT
            );
            CREATE TABLE blindspotarchives (
              id TEXT PRIMARY KEY,
              userid TEXT NOT NULL,
              title TEXT NOT NULL,
              triggerpattern TEXT NOT NULL,
              knowntheory TEXT,
              practicalfailuremode TEXT,
              suggestedanchorsjson TEXT,
              relatedpuzzlesjson TEXT,
              frequency INTEGER DEFAULT 1,
              lastseenat TEXT,
              createdat TEXT NOT NULL,
              severity TEXT DEFAULT 'medium',
              domainsjson TEXT,
              resolutionstatus TEXT DEFAULT 'active',
              resolutionat TEXT
            );
            """
        )
        engine = SoulMapEngine(connection)
        changes = engine.update_from_query_result(
            user_id="user-write",
            detected_patterns=["relationship:REL_001"],
            matched_dimension="relationship",
            matched_principle_id="REL_001",
            belief_shift_detected=False,
            discovery_triggered=False,
            session_id="sess-1",
        )
        row = connection.execute(
            "SELECT recurringpatternsjson, patternweightsjson FROM soulmaps WHERE userid = ?",
            ("user-write",),
        ).fetchone()

    assert changes["new_patterns"] == ["relationship:REL_001"]
    assert row is not None
    assert "relationship:REL_001" in row["recurringpatternsjson"]
    assert "relationship:REL_001" in row["patternweightsjson"]

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/truth-api"))

from app.main import truth_query
from app.models import TruthQueryRequest


def test_truth_query_fallback_keeps_legacy_and_truth_map_fields(monkeypatch):
    def broken_connect_db():
        raise sqlite3.DatabaseError("db unavailable")

    monkeypatch.setattr("app.main.connect_db", broken_connect_db)
    payload = TruthQueryRequest(
        userid="test-user",
        sessionid="test-session",
        message="我最近感覺很疲憊",
    )

    response = truth_query(payload)

    for field in ("dimensions", "principles", "puzzles", "response"):
        assert field in response
    assert response["truth_map"]["fact_layer"]
    assert response["truth_map"]["truth_claim"]["objectivity_statement"]

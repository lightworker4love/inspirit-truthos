from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = ROOT / "scripts" / "bridge_daily_reflection_to_api.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("bridge_daily_reflection_to_api_phase3", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _prepare_run_dir(tmp_path: Path, run_date: str) -> Path:
    daily_dir = tmp_path / "data" / "daily_reflections" / run_date
    daily_dir.mkdir(parents=True, exist_ok=True)
    reflection_payload = {
        "run_date": run_date,
        "time_window": {
            "start": "2026-03-12T09:00:00+08:00",
            "end": "2026-03-13T09:00:00+08:00",
            "timezone": "Asia/Taipei",
            "window_hours": 24,
        },
        "summary": "phase3 reflection",
        "discernment_layers": {
            "facts": ["f1"],
            "interpretations": ["i1"],
            "inferences": [{"statement": "maybe", "confidence": 0.5, "working_hypothesis": True}],
            "guidance": ["g1"],
        },
        "signals": {
            "emotions": ["calm"],
            "relationship_patterns": ["pattern"],
            "work_patterns": [],
            "decision_patterns": [],
        },
        "truth_mapping": {
            "dimensions": [{"code": "relationship", "score": 0.9}],
            "principles": [{"code": "REL_001", "title": "Boundary", "confidence": 0.8}],
            "puzzles": [{"id": "PZ1", "title": "Puzzle", "pattern_type": "relationship", "confidence": 0.7}],
        },
        "writeback_candidates": {
            "soul_map": {
                "recurring_patterns": ["pattern"],
                "limiting_beliefs": [],
                "emotional_signatures": [],
                "active_lessons": [],
                "evolution_stage": "stage",
                "should_write": True,
            },
            "blind_spot_archive": [],
            "belief_logs": [],
            "case_summary": {
                "title": "Case",
                "summary": "Summary",
                "related_dimensions": ["relationship"],
                "should_write": False,
            },
        },
        "dashboard_metrics": {
            "clarity_score": 70,
            "emotional_intensity_score": 50,
            "alignment_score": 71,
            "boundary_score": 69,
            "truth_discernment_score": 80,
            "memory_confidence_score": 60,
        },
        "uncertainty_notes": [],
        "source_context_status": {
            "life_principles_attached": False,
            "external_context_complete": False,
            "missing_inputs": ["attachment"],
        },
        "recommended_actions": [],
        "recommended_questions": [],
        "truth_observations": [],
    }
    (daily_dir / "reflection.json").write_text(json.dumps(reflection_payload, ensure_ascii=False), encoding="utf-8")
    (daily_dir / "report.md").write_text("# report\nbody", encoding="utf-8")
    dashboard_dir = tmp_path / "data" / "dashboard"
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    (dashboard_dir / "reflection_snapshots.jsonl").write_text(
        json.dumps(
            {
                "run_date": run_date,
                "time_window_hours": 24,
                "daily_timeline": {
                    "summary": "timeline",
                    "primary_dimensions": ["relationship"],
                    "primary_principles": ["REL_001"],
                    "primary_fluctuations": ["calm"],
                },
                "dimension_scores": [{"dimension_code": "relationship", "score": 0.9}],
                "recurring_patterns": [],
                "belief_shifts": [],
                "blind_spots": [],
                "alignment_metrics": {
                    "clarity_score": 70,
                    "boundary_score": 69,
                    "discernment_score": 80,
                    "alignment_score": 71,
                    "emotional_intensity_score": 50,
                    "memory_confidence_score": 60,
                },
                "source_run_path": str(daily_dir / "reflection.json"),
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return daily_dir


def test_writeback_success_triggers_materialize(tmp_path, monkeypatch):
    module = _load_module()
    run_date = "2026-03-13"
    daily_dir = _prepare_run_dir(tmp_path, run_date)
    monkeypatch.setattr(module, "ROOT", tmp_path)

    def _post(url, payload, timeout=20.0):
        if url.endswith("/api/reflection/writeback"):
            return {"accepted_streams": ["reflection_runs"]}
        if url.endswith("/api/reflection/materialize"):
            return {"materialized_views": ["dashboard_overview_view", "dimension_trends_view"]}
        raise AssertionError(url)

    monkeypatch.setattr(module, "_post_json", _post)

    result = module.run_bridge(module.BridgeConfig(run_date=run_date))

    assert result["writeback_status"] == "success"
    assert result["materialize_status"] == "success"
    receipt = json.loads((daily_dir / "materialize_receipt.json").read_text(encoding="utf-8"))
    assert receipt["response"]["materialized_views"] == ["dashboard_overview_view", "dimension_trends_view"]


def test_writeback_failure_skips_materialize(tmp_path, monkeypatch):
    module = _load_module()
    run_date = "2026-03-13"
    daily_dir = _prepare_run_dir(tmp_path, run_date)
    monkeypatch.setattr(module, "ROOT", tmp_path)

    def _post(url, payload, timeout=20.0):
        raise module.error.URLError("writeback down")

    monkeypatch.setattr(module, "_post_json", _post)

    with pytest.raises(module.BridgeError):
        module.run_bridge(module.BridgeConfig(run_date=run_date))

    assert (daily_dir / "writeback_error.json").exists()
    assert not (daily_dir / "materialize_receipt.json").exists()
    assert not (daily_dir / "materialize_error.json").exists()


def test_materialize_failure_keeps_writeback_success(tmp_path, monkeypatch):
    module = _load_module()
    run_date = "2026-03-13"
    daily_dir = _prepare_run_dir(tmp_path, run_date)
    monkeypatch.setattr(module, "ROOT", tmp_path)

    def _post(url, payload, timeout=20.0):
        if url.endswith("/api/reflection/writeback"):
            return {"accepted_streams": ["reflection_runs"]}
        if url.endswith("/api/reflection/materialize"):
            raise module.error.URLError("materialize down")
        raise AssertionError(url)

    monkeypatch.setattr(module, "_post_json", _post)

    result = module.run_bridge(module.BridgeConfig(run_date=run_date))

    assert result["writeback_status"] == "success"
    assert result["materialize_status"] == "error"
    assert (daily_dir / "writeback_receipt.json").exists()
    assert (daily_dir / "materialize_error.json").exists()


def test_skip_materialize(tmp_path, monkeypatch):
    module = _load_module()
    run_date = "2026-03-13"
    daily_dir = _prepare_run_dir(tmp_path, run_date)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "_post_json", lambda url, payload, timeout=20.0: {"accepted_streams": ["reflection_runs"]})

    result = module.run_bridge(module.BridgeConfig(run_date=run_date, materialize=False))

    assert result["writeback_status"] == "success"
    assert result["materialize_status"] == "skipped"
    assert not (daily_dir / "materialize_receipt.json").exists()


def test_strict_materialize_non_zero_exit(tmp_path, monkeypatch):
    module = _load_module()
    run_date = "2026-03-13"
    _prepare_run_dir(tmp_path, run_date)
    monkeypatch.setattr(module, "ROOT", tmp_path)

    def _post(url, payload, timeout=20.0):
        if url.endswith("/api/reflection/writeback"):
            return {"accepted_streams": ["reflection_runs"]}
        raise module.error.URLError("materialize down")

    monkeypatch.setattr(module, "_post_json", _post)

    exit_code = module.main(["--date", run_date, "--strict-materialize"])

    assert exit_code == 1

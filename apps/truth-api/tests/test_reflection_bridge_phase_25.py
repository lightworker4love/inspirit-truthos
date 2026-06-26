from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = ROOT / "scripts" / "bridge_daily_reflection_to_api.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("bridge_daily_reflection_to_api", SCRIPT_PATH)
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
        "summary": "bridge test reflection",
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
    import_dir = tmp_path / "data" / "import_drafts"
    import_dir.mkdir(parents=True, exist_ok=True)
    (import_dir / "core_principle_candidates.jsonl").write_text(
        json.dumps(
            {
                "id": "draft1",
                "dimension": "relationship",
                "title": "Boundary",
                "axiom": "a",
                "explanation": "b",
                "shadow_form": "c",
                "truth_form": "d",
                "coach_questions": [],
                "source_refs": ["r1"],
                "status": "draft",
                "generated_from_run_date": run_date,
                "cross_day_support_count": 3,
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (import_dir / "truth_puzzle_candidates.jsonl").write_text(
        json.dumps(
            {
                "id": "draftp1",
                "dimension": "relationship",
                "principle_code": "draft1",
                "title": "Puzzle",
                "statement": "s",
                "pattern_type": "relationship",
                "misbelief": "m",
                "truth_reframe": "t",
                "coach_prompt": "c",
                "trigger_signals": [],
                "use_cases": [],
                "tags": [],
                "source_doc": "doc",
                "source_excerpt": "excerpt",
                "status": "draft",
                "generated_from_run_date": run_date,
                "cross_day_support_count": 3,
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return daily_dir


def test_bridge_success_writeback(tmp_path, monkeypatch):
    module = _load_module()
    run_date = "2026-03-13"
    daily_dir = _prepare_run_dir(tmp_path, run_date)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "_post_json", lambda url, payload, timeout=20.0: {"accepted_streams": ["reflection_runs"]})

    result = module.run_bridge(module.BridgeConfig(run_date=run_date, api_base="http://api.test"))

    assert result["status"] == "success"
    receipt = json.loads((daily_dir / "writeback_receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "success"
    assert receipt["response"]["accepted_streams"] == ["reflection_runs"]


def test_bridge_duplicate_skip(tmp_path, monkeypatch):
    module = _load_module()
    run_date = "2026-03-13"
    daily_dir = _prepare_run_dir(tmp_path, run_date)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "_post_json", lambda url, payload, timeout=20.0: {"materialized_views": ["dashboard_overview_view"]})
    (daily_dir / "writeback_receipt.json").write_text(
        json.dumps(
            {
                "status": "success",
                "run_date": run_date,
                "user_id": "tongwei",
                "payload_fingerprint": "abc123",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = module.run_bridge(module.BridgeConfig(run_date=run_date))

    assert result["writeback_status"] == "skipped"
    assert result["materialize_status"] == "success"
    assert result["skipped_reason"].startswith("existing successful")


def test_bridge_api_unavailable_writes_error(tmp_path, monkeypatch):
    module = _load_module()
    run_date = "2026-03-13"
    daily_dir = _prepare_run_dir(tmp_path, run_date)
    monkeypatch.setattr(module, "ROOT", tmp_path)

    def _boom(url, payload, timeout=20.0):
        raise module.error.URLError("connection refused")

    monkeypatch.setattr(module, "_post_json", _boom)

    with pytest.raises(module.BridgeError):
        module.run_bridge(module.BridgeConfig(run_date=run_date))

    error_payload = json.loads((daily_dir / "writeback_error.json").read_text(encoding="utf-8"))
    assert error_payload["status"] == "error"
    assert error_payload["retry"]["recommended"] is True


def test_bridge_dry_run_no_files_written(tmp_path, monkeypatch):
    module = _load_module()
    run_date = "2026-03-13"
    daily_dir = _prepare_run_dir(tmp_path, run_date)
    monkeypatch.setattr(module, "ROOT", tmp_path)

    result = module.run_bridge(module.BridgeConfig(run_date=run_date, dry_run=True))

    assert result["status"] == "dry-run"
    assert not (daily_dir / "writeback_receipt.json").exists()
    assert not (daily_dir / "writeback_error.json").exists()


def test_bridge_missing_reflection_json_fails_safely(tmp_path, monkeypatch):
    module = _load_module()
    run_date = "2026-03-13"
    monkeypatch.setattr(module, "ROOT", tmp_path)

    with pytest.raises(module.BridgeError):
        module.run_bridge(module.BridgeConfig(run_date=run_date))

    error_payload = json.loads(
        (tmp_path / "data" / "daily_reflections" / run_date / "writeback_error.json").read_text(encoding="utf-8")
    )
    assert error_payload["status"] == "error"
    assert "Missing reflection artifact" in error_payload["error_message"]

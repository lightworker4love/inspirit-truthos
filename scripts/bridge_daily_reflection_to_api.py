#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_API_BASE = os.getenv("TRUTHOS_REFLECTION_API_BASE", "http://127.0.0.1:18000").rstrip("/")
DEFAULT_USER_ID = os.getenv("TRUTHOS_REFLECTION_WRITEBACK_USER_ID", "tongwei")
DEFAULT_TENANT_ID = os.getenv("TRUTHOS_REFLECTION_WRITEBACK_TENANT_ID", "inspirit-local")


class BridgeError(RuntimeError):
    pass


@dataclass
class BridgeConfig:
    run_date: str
    api_base: str = DEFAULT_API_BASE
    user_id: str = DEFAULT_USER_ID
    tenant_id: str = DEFAULT_TENANT_ID
    force: bool = False
    dry_run: bool = False
    materialize: bool = True
    strict_materialize: bool = False


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _post_json(url: str, payload: dict[str, Any], timeout: float = 20.0) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _payload_fingerprint(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _daily_dir(run_date: str) -> Path:
    return ROOT / "data" / "daily_reflections" / run_date


def _find_dashboard_snapshot(run_date: str, reflection_run: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    notes: list[str] = []
    snapshot_path = ROOT / "data" / "dashboard" / "reflection_snapshots.jsonl"
    matches = [item for item in _read_jsonl(snapshot_path) if item.get("run_date") == run_date]
    if matches:
        return matches[-1], notes

    truth_mapping = reflection_run.get("truth_mapping", {})
    metrics = reflection_run.get("dashboard_metrics", {})
    derived = {
        "run_date": run_date,
        "time_window_hours": reflection_run.get("time_window", {}).get("window_hours", 24),
        "daily_timeline": {
            "summary": reflection_run.get("summary", ""),
            "primary_dimensions": [item.get("code") for item in truth_mapping.get("dimensions", [])],
            "primary_principles": [item.get("code") for item in truth_mapping.get("principles", [])],
            "primary_fluctuations": reflection_run.get("signals", {}).get("emotions", []),
        },
        "dimension_scores": [
            {"dimension_code": item.get("code"), "score": item.get("score", 0.0)}
            for item in truth_mapping.get("dimensions", [])
        ],
        "recurring_patterns": [],
        "belief_shifts": [],
        "blind_spots": [],
        "alignment_metrics": {
            "clarity_score": metrics.get("clarity_score", 0),
            "boundary_score": metrics.get("boundary_score", 0),
            "discernment_score": metrics.get("truth_discernment_score", 0),
            "alignment_score": metrics.get("alignment_score", 0),
            "emotional_intensity_score": metrics.get("emotional_intensity_score", 0),
            "memory_confidence_score": metrics.get("memory_confidence_score", 0),
        },
        "source_run_path": str(_daily_dir(run_date) / "reflection.json"),
    }
    notes.append("dashboard_snapshot derived from reflection.json because no same-day reflection_snapshots.jsonl record was found.")
    return derived, notes


def _find_import_drafts(run_date: str) -> tuple[dict[str, Any], list[str]]:
    notes: list[str] = []
    principles_path = ROOT / "data" / "import_drafts" / "core_principle_candidates.jsonl"
    puzzles_path = ROOT / "data" / "import_drafts" / "truth_puzzle_candidates.jsonl"
    principle_matches = [
        item for item in _read_jsonl(principles_path) if item.get("generated_from_run_date") == run_date
    ]
    puzzle_matches = [
        item for item in _read_jsonl(puzzles_path) if item.get("generated_from_run_date") == run_date
    ]
    if not principle_matches:
        notes.append("No same-day core principle draft events found; using empty draft list.")
    if not puzzle_matches:
        notes.append("No same-day truth puzzle draft events found; using empty draft list.")
    return {
        "core_principle_candidates": principle_matches,
        "truth_puzzle_candidates": puzzle_matches,
    }, notes


def _build_operator_summary(
    *,
    run_date: str,
    reflection_run: dict[str, Any],
    files_written: list[str],
    notes: list[str],
) -> dict[str, Any]:
    truth_mapping = reflection_run.get("truth_mapping", {})
    candidates = reflection_run.get("writeback_candidates", {})
    writeback_streams: list[str] = []
    if candidates.get("soul_map", {}).get("should_write"):
        writeback_streams.append("soul_map")
    if any(item.get("should_write") for item in candidates.get("blind_spot_archive", [])):
        writeback_streams.append("blind_spot")
    if any(item.get("should_write") for item in candidates.get("belief_logs", [])):
        writeback_streams.append("belief_log")
    if candidates.get("case_summary", {}).get("should_write"):
        writeback_streams.append("case_summary")

    report_path = _daily_dir(run_date) / "report.md"
    report_excerpt = ""
    if report_path.exists():
        for line in report_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                report_excerpt = stripped[:200]
                break
    summary_notes = list(notes)
    if report_excerpt:
        summary_notes.append(f"report_excerpt: {report_excerpt}")

    return {
        "window_hours": reflection_run.get("time_window", {}).get("window_hours", 24),
        "primary_dimensions": [item.get("code") for item in truth_mapping.get("dimensions", [])],
        "files_written": files_written,
        "writeback_streams": writeback_streams,
        "notes": summary_notes,
        "metadata": {
            "trigger": "bridge_daily_reflection_to_api",
            "run_date": run_date,
            "canonical_promotion_policy": "human-review-gated",
        },
    }


def build_writeback_payload(config: BridgeConfig) -> tuple[dict[str, Any], dict[str, Path], list[str]]:
    notes: list[str] = []
    daily_dir = _daily_dir(config.run_date)
    reflection_path = daily_dir / "reflection.json"
    report_path = daily_dir / "report.md"
    receipt_path = daily_dir / "writeback_receipt.json"
    error_path = daily_dir / "writeback_error.json"

    if not reflection_path.exists():
        raise BridgeError(f"Missing reflection artifact: {reflection_path}")

    reflection_run = _read_json(reflection_path)
    dashboard_snapshot, dashboard_notes = _find_dashboard_snapshot(config.run_date, reflection_run)
    import_drafts, draft_notes = _find_import_drafts(config.run_date)
    notes.extend(dashboard_notes)
    notes.extend(draft_notes)
    files_written = [str(reflection_path)]
    if report_path.exists():
        files_written.append(str(report_path))

    payload = {
        "run_date": config.run_date,
        "user_id": config.user_id,
        "tenant_id": config.tenant_id,
        "source_file": str(reflection_path),
        "source_run_id": f"{config.user_id}:{config.run_date}",
        "reflection_run": reflection_run,
        "dashboard_snapshot": dashboard_snapshot,
        "writeback_candidates": reflection_run.get("writeback_candidates", {}),
        "import_drafts": import_drafts,
        "source_context_status": reflection_run.get("source_context_status", {}),
        "operator_summary": _build_operator_summary(
            run_date=config.run_date,
            reflection_run=reflection_run,
            files_written=files_written,
            notes=notes,
        ),
    }
    return payload, {
        "daily_dir": daily_dir,
        "reflection": reflection_path,
        "report": report_path,
        "receipt": receipt_path,
        "error": error_path,
    }, notes


def should_skip_due_to_receipt(receipt_path: Path, *, user_id: str, run_date: str, force: bool) -> tuple[bool, dict[str, Any] | None]:
    if force or not receipt_path.exists():
        return False, None
    receipt = _read_json(receipt_path)
    if receipt.get("status") == "success" and receipt.get("user_id") == user_id and receipt.get("run_date") == run_date:
        return True, receipt
    return False, receipt


def run_bridge(config: BridgeConfig) -> dict[str, Any]:
    daily_dir = _daily_dir(config.run_date)
    receipt_path = daily_dir / "writeback_receipt.json"
    error_path = daily_dir / "writeback_error.json"
    materialize_receipt_path = daily_dir / "materialize_receipt.json"
    materialize_error_path = daily_dir / "materialize_error.json"
    try:
        payload, paths, notes = build_writeback_payload(config)
    except BridgeError as exc:
        error_payload = {
            "status": "error",
            "attempted_at": datetime.utcnow().isoformat() + "Z",
            "run_date": config.run_date,
            "user_id": config.user_id,
            "tenant_id": config.tenant_id,
            "api_base": config.api_base,
            "endpoint": f"{config.api_base}/api/reflection/writeback",
            "payload_fingerprint": None,
            "source_file": str(daily_dir / "reflection.json"),
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "notes": [],
            "retry": {
                "recommended": True,
                "next_retry_command": (
                    f"python {ROOT / 'scripts' / 'bridge_daily_reflection_to_api.py'} "
                    f"--date {config.run_date} --api-base {config.api_base} "
                    f"--user-id {config.user_id} --tenant-id {config.tenant_id} --force"
                ),
            },
        }
        _write_json(error_path, error_payload)
        raise

    summary: dict[str, Any] = {
        "status": "pending",
        "run_date": config.run_date,
        "user_id": config.user_id,
        "tenant_id": config.tenant_id,
        "writeback_status": "pending",
        "materialize_status": "pending" if config.materialize else "skipped",
        "updated_views": [],
        "skipped_reason": None,
    }

    skip, existing_receipt = should_skip_due_to_receipt(
        paths["receipt"], user_id=config.user_id, run_date=config.run_date, force=config.force
    )
    if skip:
        summary.update(
            {
                "status": "skipped",
                "writeback_status": "skipped",
                "skipped_reason": "existing successful writeback receipt found",
                "receipt_path": str(paths["receipt"]),
                "existing_receipt": existing_receipt,
            }
        )
        if not config.materialize:
            summary["materialize_status"] = "skipped"
            summary["skipped_reason"] = summary["skipped_reason"] or "materialize disabled"
            return summary
        materialize_result = _trigger_materialize(
            config=config,
            payload_fingerprint=existing_receipt.get("payload_fingerprint") if isinstance(existing_receipt, dict) else None,
            materialize_receipt_path=materialize_receipt_path,
            materialize_error_path=materialize_error_path,
        )
        summary.update(materialize_result)
        summary["status"] = "success" if summary["materialize_status"] == "success" else "partial"
        return summary

    fingerprint = _payload_fingerprint(payload)
    if config.dry_run:
        summary.update(
            {
                "status": "dry-run",
                "writeback_status": "dry-run",
                "materialize_status": "skipped" if not config.materialize else "dry-run",
                "api_base": config.api_base,
                "payload_fingerprint": fingerprint,
                "notes": notes,
                "payload_preview": payload,
            }
        )
        return summary

    url = f"{config.api_base}/api/reflection/writeback"
    try:
        response = _post_json(url, payload)
        receipt = {
            "status": "success",
            "posted_at": datetime.utcnow().isoformat() + "Z",
            "run_date": config.run_date,
            "user_id": config.user_id,
            "tenant_id": config.tenant_id,
            "api_base": config.api_base,
            "endpoint": url,
            "payload_fingerprint": fingerprint,
            "source_file": payload["source_file"],
            "response": response,
            "notes": notes,
            "retry": {
                "recommended": False,
                "next_retry_command": None,
            },
        }
        _write_json(paths["receipt"], receipt)
        if paths["error"].exists():
            paths["error"].unlink()
        summary.update(
            {
                "status": "success",
                "writeback_status": "success",
                "materialize_status": "skipped" if not config.materialize else "pending",
                "api_base": config.api_base,
                "payload_fingerprint": fingerprint,
                "writeback_receipt_path": str(paths["receipt"]),
                "writeback_response": response,
                "notes": notes,
            }
        )
        if not config.materialize:
            summary["skipped_reason"] = "materialize disabled"
            return summary
        materialize_result = _trigger_materialize(
            config=config,
            payload_fingerprint=fingerprint,
            materialize_receipt_path=materialize_receipt_path,
            materialize_error_path=materialize_error_path,
        )
        summary.update(materialize_result)
        if summary["materialize_status"] == "error" and config.strict_materialize:
            summary["status"] = "error"
            raise BridgeError("Materialize failed in strict-materialize mode.")
        if summary["materialize_status"] == "error":
            summary["status"] = "partial"
        return summary
    except (BridgeError, error.URLError, error.HTTPError, TimeoutError, ValueError) as exc:
        error_payload = {
            "status": "error",
            "attempted_at": datetime.utcnow().isoformat() + "Z",
            "run_date": config.run_date,
            "user_id": config.user_id,
            "tenant_id": config.tenant_id,
            "api_base": config.api_base,
            "endpoint": url,
            "payload_fingerprint": fingerprint,
            "source_file": payload["source_file"],
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "notes": notes,
            "retry": {
                "recommended": True,
                "next_retry_command": (
                    f"python {ROOT / 'scripts' / 'bridge_daily_reflection_to_api.py'} "
                    f"--date {config.run_date} --api-base {config.api_base} "
                    f"--user-id {config.user_id} --tenant-id {config.tenant_id} --force"
                ),
            },
        }
        _write_json(paths["error"], error_payload)
        raise BridgeError(str(exc)) from exc


def parse_args(argv: list[str] | None = None) -> BridgeConfig:
    parser = argparse.ArgumentParser(description="Bridge daily reflection artifacts into TruthOS /api/reflection/writeback.")
    parser.add_argument("--date", required=True, dest="run_date")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--user-id", default=DEFAULT_USER_ID)
    parser.add_argument("--tenant-id", default=DEFAULT_TENANT_ID)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--materialize", action="store_true", default=True)
    parser.add_argument("--skip-materialize", action="store_true")
    parser.add_argument("--strict-materialize", action="store_true")
    args = parser.parse_args(argv)
    return BridgeConfig(
        run_date=args.run_date,
        api_base=args.api_base.rstrip("/"),
        user_id=args.user_id,
        tenant_id=args.tenant_id,
        force=args.force,
        dry_run=args.dry_run,
        materialize=not args.skip_materialize,
        strict_materialize=args.strict_materialize,
    )


def main(argv: list[str] | None = None) -> int:
    config = parse_args(argv)
    try:
        result = run_bridge(config)
    except BridgeError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _trigger_materialize(
    *,
    config: BridgeConfig,
    payload_fingerprint: str | None,
    materialize_receipt_path: Path,
    materialize_error_path: Path,
) -> dict[str, Any]:
    request_payload = {
        "user_id": config.user_id,
        "tenant_id": config.tenant_id,
        "run_date": config.run_date,
        "mode": "incremental",
        "rebuild_all": False,
    }
    endpoint = f"{config.api_base}/api/reflection/materialize"
    try:
        response = _post_json(endpoint, request_payload)
        receipt = {
            "status": "success",
            "posted_at": datetime.utcnow().isoformat() + "Z",
            "run_date": config.run_date,
            "user_id": config.user_id,
            "tenant_id": config.tenant_id,
            "api_base": config.api_base,
            "endpoint": endpoint,
            "mode": "incremental",
            "payload_fingerprint": payload_fingerprint,
            "response": response,
        }
        _write_json(materialize_receipt_path, receipt)
        if materialize_error_path.exists():
            materialize_error_path.unlink()
        return {
            "materialize_status": "success",
            "updated_views": response.get("materialized_views", []),
            "materialize_receipt_path": str(materialize_receipt_path),
        }
    except (error.URLError, error.HTTPError, TimeoutError, ValueError) as exc:
        error_payload = {
            "status": "error",
            "attempted_at": datetime.utcnow().isoformat() + "Z",
            "run_date": config.run_date,
            "user_id": config.user_id,
            "tenant_id": config.tenant_id,
            "api_base": config.api_base,
            "endpoint": endpoint,
            "mode": "incremental",
            "payload_fingerprint": payload_fingerprint,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "retry": {
                "recommended": True,
                "next_retry_command": (
                    f"python {ROOT / 'scripts' / 'materialize_reflection_dashboard.py'} "
                    f"--user-id {config.user_id} --tenant-id {config.tenant_id} "
                    f"--run-date {config.run_date} --mode incremental"
                ),
            },
        }
        _write_json(materialize_error_path, error_payload)
        return {
            "materialize_status": "error",
            "updated_views": [],
            "materialize_error_path": str(materialize_error_path),
            "skipped_reason": None,
        }


if __name__ == "__main__":
    raise SystemExit(main())

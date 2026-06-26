from __future__ import annotations

import json
import sqlite3
from typing import Any


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


class ReflectionRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def get_existing_run(self, *, user_id: str, run_date: str) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT *
            FROM reflection_runs
            WHERE user_id = ? AND run_date = ?
            """,
            (user_id, run_date),
        ).fetchone()

    def upsert_reflection_run(self, payload: dict[str, Any]) -> None:
        self.connection.execute(
            """
            INSERT INTO reflection_runs (
              id, run_date, user_id, tenant_id, source_file, source_run_id, status, confidence,
              generated_from_run_date, payload_fingerprint, source_context_status_json,
              operator_summary_json, reflection_run_json, dashboard_snapshot_json,
              writeback_candidates_json, import_drafts_json, created_at, updated_at
            ) VALUES (
              :id, :run_date, :user_id, :tenant_id, :source_file, :source_run_id, :status, :confidence,
              :generated_from_run_date, :payload_fingerprint, :source_context_status_json,
              :operator_summary_json, :reflection_run_json, :dashboard_snapshot_json,
              :writeback_candidates_json, :import_drafts_json, :created_at, :updated_at
            )
            ON CONFLICT(user_id, run_date) DO UPDATE SET
              tenant_id = excluded.tenant_id,
              source_file = excluded.source_file,
              source_run_id = excluded.source_run_id,
              status = excluded.status,
              confidence = excluded.confidence,
              generated_from_run_date = excluded.generated_from_run_date,
              payload_fingerprint = excluded.payload_fingerprint,
              source_context_status_json = excluded.source_context_status_json,
              operator_summary_json = excluded.operator_summary_json,
              reflection_run_json = excluded.reflection_run_json,
              dashboard_snapshot_json = excluded.dashboard_snapshot_json,
              writeback_candidates_json = excluded.writeback_candidates_json,
              import_drafts_json = excluded.import_drafts_json,
              updated_at = excluded.updated_at
            """,
            payload,
        )

    def replace_discernment_layers(self, *, user_id: str, run_date: str, rows: list[dict[str, Any]]) -> None:
        self.connection.execute(
            "DELETE FROM reflection_discernment_layers WHERE user_id = ? AND run_date = ?",
            (user_id, run_date),
        )
        self.connection.executemany(
            """
            INSERT INTO reflection_discernment_layers (
              id, run_date, user_id, tenant_id, source_file, source_run_id, status, confidence,
              layer_type, content, working_hypothesis, created_at, updated_at
            ) VALUES (
              :id, :run_date, :user_id, :tenant_id, :source_file, :source_run_id, :status, :confidence,
              :layer_type, :content, :working_hypothesis, :created_at, :updated_at
            )
            """,
            rows,
        )

    def replace_truth_mappings(self, *, user_id: str, run_date: str, rows: list[dict[str, Any]]) -> None:
        self.connection.execute(
            "DELETE FROM reflection_truth_mappings WHERE user_id = ? AND run_date = ?",
            (user_id, run_date),
        )
        self.connection.executemany(
            """
            INSERT INTO reflection_truth_mappings (
              id, run_date, user_id, tenant_id, source_file, source_run_id, status, confidence,
              mapping_type, code, title, pattern_type, score, generated_from_run_date, metadata_json,
              created_at, updated_at
            ) VALUES (
              :id, :run_date, :user_id, :tenant_id, :source_file, :source_run_id, :status, :confidence,
              :mapping_type, :code, :title, :pattern_type, :score, :generated_from_run_date,
              :metadata_json, :created_at, :updated_at
            )
            """,
            rows,
        )

    def upsert_dashboard_snapshot(self, row: dict[str, Any]) -> None:
        self.connection.execute(
            """
            INSERT INTO dashboard_snapshots (
              id, run_date, user_id, tenant_id, source_file, source_run_id, status, confidence,
              summary, snapshot_json, created_at, updated_at
            ) VALUES (
              :id, :run_date, :user_id, :tenant_id, :source_file, :source_run_id, :status, :confidence,
              :summary, :snapshot_json, :created_at, :updated_at
            )
            ON CONFLICT(user_id, run_date) DO UPDATE SET
              tenant_id = excluded.tenant_id,
              source_file = excluded.source_file,
              source_run_id = excluded.source_run_id,
              status = excluded.status,
              confidence = excluded.confidence,
              summary = excluded.summary,
              snapshot_json = excluded.snapshot_json,
              updated_at = excluded.updated_at
            """,
            row,
        )

    def upsert_dashboard_metrics(self, row: dict[str, Any]) -> None:
        self.connection.execute(
            """
            INSERT INTO dashboard_daily_metrics (
              id, run_date, user_id, tenant_id, source_file, source_run_id, status, confidence,
              clarity_score, emotional_intensity_score, alignment_score, boundary_score,
              truth_discernment_score, memory_confidence_score, created_at, updated_at
            ) VALUES (
              :id, :run_date, :user_id, :tenant_id, :source_file, :source_run_id, :status, :confidence,
              :clarity_score, :emotional_intensity_score, :alignment_score, :boundary_score,
              :truth_discernment_score, :memory_confidence_score, :created_at, :updated_at
            )
            ON CONFLICT(user_id, run_date) DO UPDATE SET
              tenant_id = excluded.tenant_id,
              source_file = excluded.source_file,
              source_run_id = excluded.source_run_id,
              status = excluded.status,
              confidence = excluded.confidence,
              clarity_score = excluded.clarity_score,
              emotional_intensity_score = excluded.emotional_intensity_score,
              alignment_score = excluded.alignment_score,
              boundary_score = excluded.boundary_score,
              truth_discernment_score = excluded.truth_discernment_score,
              memory_confidence_score = excluded.memory_confidence_score,
              updated_at = excluded.updated_at
            """,
            row,
        )

    def insert_ignore_many(self, table: str, rows: list[dict[str, Any]]) -> int:
        if not rows:
            return 0
        columns = sorted(rows[0].keys())
        names = ", ".join(columns)
        placeholders = ", ".join(f":{column}" for column in columns)
        before = self.connection.total_changes
        self.connection.executemany(
            f"INSERT OR IGNORE INTO {table} ({names}) VALUES ({placeholders})",
            rows,
        )
        return self.connection.total_changes - before

    def insert_audit_logs(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        self.connection.executemany(
            """
            INSERT INTO writeback_audit_log (
              id, run_date, user_id, tenant_id, source_file, source_run_id, stream_name,
              action, outcome, reason, status, confidence, duplicate_key, created_at, updated_at
            ) VALUES (
              :id, :run_date, :user_id, :tenant_id, :source_file, :source_run_id, :stream_name,
              :action, :outcome, :reason, :status, :confidence, :duplicate_key, :created_at, :updated_at
            )
            """,
            rows,
        )

    def get_run_bundle(self, *, user_id: str, run_date: str) -> dict[str, Any] | None:
        run_row = self.get_existing_run(user_id=user_id, run_date=run_date)
        if run_row is None:
            return None
        discernment_rows = self.connection.execute(
            """
            SELECT layer_type, content, confidence, working_hypothesis, status, created_at
            FROM reflection_discernment_layers
            WHERE user_id = ? AND run_date = ?
            ORDER BY layer_type ASC, created_at ASC
            """,
            (user_id, run_date),
        ).fetchall()
        truth_mapping_rows = self.connection.execute(
            """
            SELECT mapping_type, code, title, pattern_type, score, confidence, metadata_json
            FROM reflection_truth_mappings
            WHERE user_id = ? AND run_date = ?
            ORDER BY mapping_type ASC, code ASC
            """,
            (user_id, run_date),
        ).fetchall()
        dashboard_metrics_row = self.connection.execute(
            """
            SELECT clarity_score, emotional_intensity_score, alignment_score, boundary_score,
                   truth_discernment_score, memory_confidence_score
            FROM dashboard_daily_metrics
            WHERE user_id = ? AND run_date = ?
            """,
            (user_id, run_date),
        ).fetchone()
        audit_rows = self.connection.execute(
            """
            SELECT stream_name, action, outcome, reason, duplicate_key, created_at
            FROM writeback_audit_log
            WHERE user_id = ? AND run_date = ?
            ORDER BY created_at ASC
            """,
            (user_id, run_date),
        ).fetchall()
        return {
            "run_payload": {
                "reflection_run": json.loads(run_row["reflection_run_json"]),
                "dashboard_snapshot": json.loads(run_row["dashboard_snapshot_json"]),
                "writeback_candidates": json.loads(run_row["writeback_candidates_json"]),
                "import_drafts": json.loads(run_row["import_drafts_json"]),
                "source_context_status": json.loads(run_row["source_context_status_json"]),
                "operator_summary": json.loads(run_row["operator_summary_json"]),
            },
            "discernment_layers": [
                {
                    "layer_type": row["layer_type"],
                    "content": row["content"],
                    "confidence": row["confidence"],
                    "working_hypothesis": bool(row["working_hypothesis"]),
                    "status": row["status"],
                    "created_at": row["created_at"],
                }
                for row in discernment_rows
            ],
            "truth_mappings": [
                {
                    "mapping_type": row["mapping_type"],
                    "code": row["code"],
                    "title": row["title"],
                    "pattern_type": row["pattern_type"],
                    "score": row["score"],
                    "confidence": row["confidence"],
                    "metadata": json.loads(row["metadata_json"]),
                }
                for row in truth_mapping_rows
            ],
            "dashboard_snapshot": json.loads(run_row["dashboard_snapshot_json"]),
            "dashboard_metrics": dict(dashboard_metrics_row) if dashboard_metrics_row else None,
            "audit_log": [dict(row) for row in audit_rows],
        }

    def list_users(self) -> list[str]:
        rows = self.connection.execute("SELECT DISTINCT user_id FROM reflection_runs ORDER BY user_id ASC").fetchall()
        return [row["user_id"] for row in rows]

    def fetch_metrics(self, *, user_id: str) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT run_date, clarity_score, emotional_intensity_score, alignment_score, boundary_score,
                   truth_discernment_score, memory_confidence_score
            FROM dashboard_daily_metrics
            WHERE user_id = ?
            ORDER BY run_date ASC
            """,
            (user_id,),
        ).fetchall()

    def fetch_dimension_scores(self, *, user_id: str) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT run_date, code, score
            FROM reflection_truth_mappings
            WHERE user_id = ? AND mapping_type = 'dimension'
            ORDER BY run_date ASC, code ASC
            """,
            (user_id,),
        ).fetchall()

    def fetch_pattern_rows(self, *, user_id: str) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT pattern_key, title, count_increment, last_seen_at
            FROM dashboard_pattern_snapshots
            WHERE user_id = ?
            ORDER BY last_seen_at ASC
            """,
            (user_id,),
        ).fetchall()

    def fetch_belief_shift_rows(self, *, user_id: str) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT belief_before, belief_after, tag, run_date, created_at
            FROM belief_log_candidate_events
            WHERE user_id = ?
            ORDER BY created_at ASC
            """,
            (user_id,),
        ).fetchall()

    def fetch_blind_spot_rows(self, *, user_id: str) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT title, trigger_pattern, run_date, created_at
            FROM blind_spot_candidate_events
            WHERE user_id = ?
            ORDER BY created_at ASC
            """,
            (user_id,),
        ).fetchall()

    def reset_materialized_cache(self, *, user_id: str) -> None:
        for table in (
            "dashboard_overview_cache",
            "dimension_trends_cache",
            "recurring_patterns_cache",
            "belief_shift_cache",
            "blind_spot_heatmap_cache",
        ):
            self.connection.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))

    def insert_materialized_rows(self, table: str, rows: list[dict[str, Any]]) -> int:
        return self.insert_ignore_many(table, rows)

    def fetch_overview_rows(self, *, user_id: str) -> list[sqlite3.Row]:
        return self.connection.execute(
            """
            SELECT window_days, generated_at, overview_json
            FROM dashboard_overview_view
            WHERE user_id = ?
            ORDER BY window_days ASC
            """,
            (user_id,),
        ).fetchall()

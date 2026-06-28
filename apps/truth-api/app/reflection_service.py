from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from uuid import uuid4

from app.db import connect_db
from app.reflection_models import DashboardOverviewResponse
from app.reflection_models import DashboardOverviewWindowModel
from app.reflection_models import ReflectionMaterializeRequest
from app.reflection_models import ReflectionMaterializeResponse
from app.reflection_models import ReflectionRunReadResponse
from app.reflection_models import ReflectionWritebackRequest
from app.reflection_models import ReflectionWritebackResponse
from app.reflection_repository import ReflectionRepository


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fingerprint(payload: ReflectionWritebackRequest) -> str:
    canonical = json.dumps(payload.model_dump(mode="json"), ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _windowed_rows(rows: list[dict], window_days: int) -> list[dict]:
    if len(rows) <= window_days:
        return rows
    return rows[-window_days:]


class ReflectionWritebackService:
    def writeback(self, payload: ReflectionWritebackRequest) -> ReflectionWritebackResponse:
        fingerprint = _fingerprint(payload)
        now = _utc_now()
        accepted_streams: list[str] = []
        skipped_streams: list[str] = []
        duplicate_keys: list[str] = []
        blocked_reasons: list[str] = []
        written_records: dict[str, int] = defaultdict(int)
        next_actions = ["Run POST /api/reflection/materialize after a successful writeback."]
        audit_rows: list[dict] = []

        with connect_db() as connection:
            repository = ReflectionRepository(connection)
            existing = repository.get_existing_run(user_id=payload.user_id, run_date=payload.run_date)
            if existing and existing["payload_fingerprint"] == fingerprint:
                duplicate_key = f"{payload.user_id}:{payload.run_date}"
                duplicate_keys.append(duplicate_key)
                skipped_streams.extend(
                    [
                        "reflection_runs",
                        "reflection_discernment_layers",
                        "reflection_truth_mappings",
                        "dashboard_snapshots",
                        "dashboard_daily_metrics",
                    ]
                )
                audit_rows.append(
                    self._audit_row(
                        payload=payload,
                        now=now,
                        stream_name="reflection_runs",
                        action="writeback",
                        outcome="duplicate",
                        reason="matching payload fingerprint",
                        duplicate_key=duplicate_key,
                    )
                )
                repository.insert_audit_logs(audit_rows)
                connection.commit()
                return ReflectionWritebackResponse(
                    accepted_streams=[],
                    skipped_streams=sorted(set(skipped_streams)),
                    duplicate_keys=duplicate_keys,
                    blocked_reasons=[],
                    written_records={},
                    next_actions=["No-op duplicate payload detected."],
                )

            repository.upsert_reflection_run(
                {
                    "id": existing["id"] if existing else uuid4().hex,
                    "run_date": payload.run_date,
                    "user_id": payload.user_id,
                    "tenant_id": payload.tenant_id,
                    "source_file": payload.source_file,
                    "source_run_id": payload.source_run_id or f"{payload.user_id}:{payload.run_date}",
                    "status": "accepted",
                    "confidence": 1.0,
                    "generated_from_run_date": payload.run_date,
                    "payload_fingerprint": fingerprint,
                    "source_context_status_json": json.dumps(
                        payload.source_context_status.model_dump(mode="json"),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "operator_summary_json": json.dumps(
                        payload.operator_summary.model_dump(mode="json"),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "reflection_run_json": json.dumps(
                        payload.reflection_run.model_dump(mode="json"),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "dashboard_snapshot_json": json.dumps(
                        payload.dashboard_snapshot.model_dump(mode="json"),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "writeback_candidates_json": json.dumps(
                        payload.writeback_candidates.model_dump(mode="json"),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "import_drafts_json": json.dumps(
                        payload.import_drafts.model_dump(mode="json"),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "created_at": existing["created_at"] if existing else now,
                    "updated_at": now,
                }
            )
            accepted_streams.append("reflection_runs")
            written_records["reflection_runs"] = 1
            audit_rows.append(
                self._audit_row(
                    payload=payload,
                    now=now,
                    stream_name="reflection_runs",
                    action="upsert",
                    outcome="accepted",
                    reason="primary snapshot upserted",
                )
            )

            discernment_rows = self._discernment_rows(payload=payload, now=now)
            repository.replace_discernment_layers(
                user_id=payload.user_id, run_date=payload.run_date, rows=discernment_rows
            )
            accepted_streams.append("reflection_discernment_layers")
            written_records["reflection_discernment_layers"] = len(discernment_rows)

            truth_mapping_rows = self._truth_mapping_rows(payload=payload, now=now)
            repository.replace_truth_mappings(
                user_id=payload.user_id, run_date=payload.run_date, rows=truth_mapping_rows
            )
            accepted_streams.append("reflection_truth_mappings")
            written_records["reflection_truth_mappings"] = len(truth_mapping_rows)

            repository.upsert_dashboard_snapshot(self._dashboard_snapshot_row(payload=payload, now=now))
            accepted_streams.append("dashboard_snapshots")
            written_records["dashboard_snapshots"] = 1

            repository.upsert_dashboard_metrics(self._dashboard_metrics_row(payload=payload, now=now))
            accepted_streams.append("dashboard_daily_metrics")
            written_records["dashboard_daily_metrics"] = 1

            pattern_rows = self._pattern_rows(payload=payload, now=now)
            written_records["dashboard_pattern_snapshots"] = repository.insert_ignore_many(
                "dashboard_pattern_snapshots", pattern_rows
            )
            accepted_streams.append("dashboard_pattern_snapshots")

            soul_map_rows = self._soul_map_rows(payload=payload, now=now)
            if soul_map_rows:
                written_records["soul_map_candidate_events"] = repository.insert_ignore_many(
                    "soul_map_candidate_events", soul_map_rows
                )
                accepted_streams.append("soul_map_candidate_events")
            else:
                skipped_streams.append("soul_map_candidate_events")

            blind_spot_rows = self._blind_spot_rows(payload=payload, now=now)
            if blind_spot_rows:
                written_records["blind_spot_candidate_events"] = repository.insert_ignore_many(
                    "blind_spot_candidate_events", blind_spot_rows
                )
                accepted_streams.append("blind_spot_candidate_events")
            else:
                skipped_streams.append("blind_spot_candidate_events")

            belief_rows = self._belief_log_rows(payload=payload, now=now)
            if belief_rows:
                written_records["belief_log_candidate_events"] = repository.insert_ignore_many(
                    "belief_log_candidate_events", belief_rows
                )
                accepted_streams.append("belief_log_candidate_events")
            else:
                skipped_streams.append("belief_log_candidate_events")

            case_summary_rows = self._case_summary_rows(payload=payload, now=now)
            if case_summary_rows:
                written_records["case_summary_candidate_events"] = repository.insert_ignore_many(
                    "case_summary_candidate_events", case_summary_rows
                )
                accepted_streams.append("case_summary_candidate_events")
            else:
                skipped_streams.append("case_summary_candidate_events")

            principle_drafts, principle_blocks = self._principle_draft_rows(payload=payload, now=now)
            blocked_reasons.extend(principle_blocks)
            if principle_drafts:
                written_records["core_principle_draft_events"] = repository.insert_ignore_many(
                    "core_principle_draft_events", principle_drafts
                )
                accepted_streams.append("core_principle_draft_events")
            elif payload.import_drafts.core_principle_candidates:
                skipped_streams.append("core_principle_draft_events")

            puzzle_drafts, puzzle_blocks = self._puzzle_draft_rows(payload=payload, now=now)
            blocked_reasons.extend(puzzle_blocks)
            if puzzle_drafts:
                written_records["truth_puzzle_draft_events"] = repository.insert_ignore_many(
                    "truth_puzzle_draft_events", puzzle_drafts
                )
                accepted_streams.append("truth_puzzle_draft_events")
            elif payload.import_drafts.truth_puzzle_candidates:
                skipped_streams.append("truth_puzzle_draft_events")

            for stream_name in set(accepted_streams):
                audit_rows.append(
                    self._audit_row(
                        payload=payload,
                        now=now,
                        stream_name=stream_name,
                        action="writeback",
                        outcome="accepted",
                        reason=f"{written_records.get(stream_name, 0)} record(s) written",
                    )
                )
            for stream_name in set(skipped_streams):
                audit_rows.append(
                    self._audit_row(
                        payload=payload,
                        now=now,
                        stream_name=stream_name,
                        action="writeback",
                        outcome="skipped",
                        reason="should_write was false or no candidate rows were eligible",
                    )
                )
            for reason in blocked_reasons:
                audit_rows.append(
                    self._audit_row(
                        payload=payload,
                        now=now,
                        stream_name="draft_governance",
                        action="validate",
                        outcome="blocked",
                        reason=reason,
                    )
                )

            if not payload.source_context_status.life_principles_attached:
                next_actions.append("Provide a readable life principles attachment for higher-confidence mapping.")

            repository.insert_audit_logs(audit_rows)
            connection.commit()

        return ReflectionWritebackResponse(
            accepted_streams=sorted(set(accepted_streams)),
            skipped_streams=sorted(set(skipped_streams)),
            duplicate_keys=duplicate_keys,
            blocked_reasons=blocked_reasons,
            written_records=dict(written_records),
            next_actions=next_actions,
        )

    def read_run(self, *, user_id: str, run_date: str) -> ReflectionRunReadResponse | None:
        with connect_db() as connection:
            repository = ReflectionRepository(connection)
            bundle = repository.get_run_bundle(user_id=user_id, run_date=run_date)
            if bundle is None:
                return None
            return ReflectionRunReadResponse(
                run_date=run_date,
                user_id=user_id,
                run_payload=bundle["run_payload"],
                discernment_layers=bundle["discernment_layers"],
                truth_mappings=bundle["truth_mappings"],
                dashboard_snapshot=bundle["dashboard_snapshot"],
                dashboard_metrics=bundle["dashboard_metrics"],
                audit_log=bundle["audit_log"],
            )

    def materialize(self, payload: ReflectionMaterializeRequest) -> ReflectionMaterializeResponse:
        generated_records: dict[str, int] = defaultdict(int)
        with connect_db() as connection:
            repository = ReflectionRepository(connection)
            user_ids = [payload.user_id] if payload.user_id else repository.list_users()
            generated_at = _utc_now()
            for user_id in user_ids:
                repository.reset_materialized_cache(user_id=user_id)
                metrics_rows = [dict(row) for row in repository.fetch_metrics(user_id=user_id)]
                dimension_rows = [dict(row) for row in repository.fetch_dimension_scores(user_id=user_id)]
                pattern_rows = [dict(row) for row in repository.fetch_pattern_rows(user_id=user_id)]
                belief_rows = [dict(row) for row in repository.fetch_belief_shift_rows(user_id=user_id)]
                blind_rows = [dict(row) for row in repository.fetch_blind_spot_rows(user_id=user_id)]

                overview_rows = self._overview_rows(
                    user_id=user_id,
                    metrics_rows=metrics_rows,
                    dimension_rows=dimension_rows,
                    pattern_rows=pattern_rows,
                    generated_at=generated_at,
                )
                generated_records["dashboard_overview_view"] += repository.insert_materialized_rows(
                    "dashboard_overview_cache", overview_rows
                )

                dimension_cache_rows = [
                    {
                        "id": uuid4().hex,
                        "user_id": user_id,
                        "run_date": row["run_date"],
                        "dimension_code": row["code"],
                        "score": row["score"] or 0.0,
                        "generated_at": generated_at,
                    }
                    for row in dimension_rows
                ]
                generated_records["dimension_trends_view"] += repository.insert_materialized_rows(
                    "dimension_trends_cache", dimension_cache_rows
                )

                recurring_rows = self._recurring_pattern_cache_rows(
                    user_id=user_id, pattern_rows=pattern_rows, generated_at=generated_at
                )
                generated_records["recurring_patterns_view"] += repository.insert_materialized_rows(
                    "recurring_patterns_cache", recurring_rows
                )

                belief_cache_rows = self._belief_shift_cache_rows(
                    user_id=user_id, belief_rows=belief_rows, generated_at=generated_at
                )
                generated_records["belief_shift_view"] += repository.insert_materialized_rows(
                    "belief_shift_cache", belief_cache_rows
                )

                blind_cache_rows = self._blind_spot_cache_rows(
                    user_id=user_id, blind_rows=blind_rows, generated_at=generated_at
                )
                generated_records["blind_spot_heatmap_view"] += repository.insert_materialized_rows(
                    "blind_spot_heatmap_cache", blind_cache_rows
                )

            connection.commit()

        return ReflectionMaterializeResponse(
            materialized_views=[
                "dashboard_overview_view",
                "dimension_trends_view",
                "recurring_patterns_view",
                "belief_shift_view",
                "blind_spot_heatmap_view",
            ],
            generated_records=dict(generated_records),
            next_actions=["Call GET /api/reflection/dashboard/overview to inspect the latest projections."],
        )

    def dashboard_overview(self, *, user_id: str) -> DashboardOverviewResponse:
        with connect_db() as connection:
            repository = ReflectionRepository(connection)
            rows = repository.fetch_overview_rows(user_id=user_id)
        windows = [
            DashboardOverviewWindowModel(**json.loads(row["overview_json"]), generated_at=row["generated_at"])
            for row in rows
        ]
        return DashboardOverviewResponse(user_id=user_id, windows=windows)

    def _audit_row(
        self,
        *,
        payload: ReflectionWritebackRequest,
        now: str,
        stream_name: str,
        action: str,
        outcome: str,
        reason: str,
        duplicate_key: str | None = None,
    ) -> dict[str, str | float | None]:
        return {
            "id": uuid4().hex,
            "run_date": payload.run_date,
            "user_id": payload.user_id,
            "tenant_id": payload.tenant_id,
            "source_file": payload.source_file,
            "source_run_id": payload.source_run_id or f"{payload.user_id}:{payload.run_date}",
            "stream_name": stream_name,
            "action": action,
            "outcome": outcome,
            "reason": reason,
            "status": outcome,
            "confidence": 1.0,
            "duplicate_key": duplicate_key,
            "created_at": now,
            "updated_at": now,
        }

    def _discernment_rows(self, *, payload: ReflectionWritebackRequest, now: str) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        base = {
            "run_date": payload.run_date,
            "user_id": payload.user_id,
            "tenant_id": payload.tenant_id,
            "source_file": payload.source_file,
            "source_run_id": payload.source_run_id or f"{payload.user_id}:{payload.run_date}",
            "status": "accepted",
            "created_at": now,
            "updated_at": now,
        }
        for layer_type, items in (
            ("fact", payload.reflection_run.discernment_layers.facts),
            ("interpretation", payload.reflection_run.discernment_layers.interpretations),
            ("guidance", payload.reflection_run.discernment_layers.guidance),
        ):
            for item in items:
                rows.append(
                    {
                        **base,
                        "id": uuid4().hex,
                        "confidence": 1.0 if layer_type == "fact" else 0.7,
                        "layer_type": layer_type,
                        "content": item,
                        "working_hypothesis": 0,
                    }
                )
        for item in payload.reflection_run.discernment_layers.inferences:
            rows.append(
                {
                    **base,
                    "id": uuid4().hex,
                    "confidence": item.confidence,
                    "layer_type": "inference",
                    "content": item.statement,
                    "working_hypothesis": int(item.working_hypothesis),
                }
            )
        return rows

    def _truth_mapping_rows(self, *, payload: ReflectionWritebackRequest, now: str) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        base = {
            "run_date": payload.run_date,
            "user_id": payload.user_id,
            "tenant_id": payload.tenant_id,
            "source_file": payload.source_file,
            "source_run_id": payload.source_run_id or f"{payload.user_id}:{payload.run_date}",
            "status": "accepted",
            "generated_from_run_date": payload.run_date,
            "created_at": now,
            "updated_at": now,
        }
        for dimension in payload.reflection_run.truth_mapping.dimensions:
            rows.append(
                {
                    **base,
                    "id": uuid4().hex,
                    "confidence": dimension.score,
                    "mapping_type": "dimension",
                    "code": dimension.code,
                    "title": None,
                    "pattern_type": None,
                    "score": dimension.score,
                    "metadata_json": json.dumps({"code": dimension.code}, ensure_ascii=False, sort_keys=True),
                }
            )
        for principle in payload.reflection_run.truth_mapping.principles:
            rows.append(
                {
                    **base,
                    "id": uuid4().hex,
                    "confidence": principle.confidence,
                    "mapping_type": "principle",
                    "code": principle.code,
                    "title": principle.title,
                    "pattern_type": None,
                    "score": principle.confidence,
                    "metadata_json": json.dumps(principle.model_dump(mode="json"), ensure_ascii=False, sort_keys=True),
                }
            )
        for puzzle in payload.reflection_run.truth_mapping.puzzles:
            rows.append(
                {
                    **base,
                    "id": uuid4().hex,
                    "confidence": puzzle.confidence,
                    "mapping_type": "puzzle",
                    "code": puzzle.id,
                    "title": puzzle.title,
                    "pattern_type": puzzle.pattern_type,
                    "score": puzzle.confidence,
                    "metadata_json": json.dumps(puzzle.model_dump(mode="json"), ensure_ascii=False, sort_keys=True),
                }
            )
        return rows

    def _dashboard_snapshot_row(self, *, payload: ReflectionWritebackRequest, now: str) -> dict[str, object]:
        return {
            "id": uuid4().hex,
            "run_date": payload.run_date,
            "user_id": payload.user_id,
            "tenant_id": payload.tenant_id,
            "source_file": payload.source_file,
            "source_run_id": payload.source_run_id or f"{payload.user_id}:{payload.run_date}",
            "status": "accepted",
            "confidence": 1.0,
            "summary": payload.dashboard_snapshot.daily_timeline.summary,
            "snapshot_json": json.dumps(payload.dashboard_snapshot.model_dump(mode="json"), ensure_ascii=False, sort_keys=True),
            "created_at": now,
            "updated_at": now,
        }

    def _dashboard_metrics_row(self, *, payload: ReflectionWritebackRequest, now: str) -> dict[str, object]:
        metrics = payload.reflection_run.dashboard_metrics
        return {
            "id": uuid4().hex,
            "run_date": payload.run_date,
            "user_id": payload.user_id,
            "tenant_id": payload.tenant_id,
            "source_file": payload.source_file,
            "source_run_id": payload.source_run_id or f"{payload.user_id}:{payload.run_date}",
            "status": "accepted",
            "confidence": 1.0,
            "clarity_score": metrics.clarity_score,
            "emotional_intensity_score": metrics.emotional_intensity_score,
            "alignment_score": metrics.alignment_score,
            "boundary_score": metrics.boundary_score,
            "truth_discernment_score": metrics.truth_discernment_score,
            "memory_confidence_score": metrics.memory_confidence_score,
            "created_at": now,
            "updated_at": now,
        }

    def _pattern_rows(self, *, payload: ReflectionWritebackRequest, now: str) -> list[dict[str, object]]:
        return [
            {
                "id": uuid4().hex,
                "run_date": payload.run_date,
                "user_id": payload.user_id,
                "tenant_id": payload.tenant_id,
                "source_file": payload.source_file,
                "source_run_id": payload.source_run_id or f"{payload.user_id}:{payload.run_date}",
                "status": "candidate",
                "confidence": pattern.confidence,
                "generated_from_run_date": payload.run_date,
                "snapshot_type": "recurring_pattern",
                "pattern_key": pattern.pattern_key,
                "title": pattern.title,
                "count_increment": pattern.count_increment,
                "last_seen_at": pattern.last_seen,
                "metadata_json": json.dumps(pattern.model_dump(mode="json"), ensure_ascii=False, sort_keys=True),
                "created_at": now,
                "updated_at": now,
            }
            for pattern in payload.dashboard_snapshot.recurring_patterns
        ]

    def _soul_map_rows(self, *, payload: ReflectionWritebackRequest, now: str) -> list[dict[str, object]]:
        soul_map = payload.writeback_candidates.soul_map
        if not soul_map.should_write:
            return []
        rows: list[dict[str, object]] = []
        for candidate_type, values in (
            ("recurring_patterns", soul_map.recurring_patterns),
            ("limiting_beliefs", soul_map.limiting_beliefs),
            ("emotional_signatures", soul_map.emotional_signatures),
            ("active_lessons", soul_map.active_lessons),
        ):
            for value in values:
                rows.append(
                    {
                        "id": uuid4().hex,
                        "run_date": payload.run_date,
                        "user_id": payload.user_id,
                        "tenant_id": payload.tenant_id,
                        "source_file": payload.source_file,
                        "source_run_id": payload.source_run_id or f"{payload.user_id}:{payload.run_date}",
                        "status": "candidate",
                        "confidence": 0.8,
                        "generated_from_run_date": payload.run_date,
                        "candidate_type": candidate_type,
                        "payload_json": json.dumps({"value": value, "evolution_stage": soul_map.evolution_stage}, ensure_ascii=False, sort_keys=True),
                        "should_write": 1,
                        "created_at": now,
                        "updated_at": now,
                    }
                )
        rows.append(
            {
                "id": uuid4().hex,
                "run_date": payload.run_date,
                "user_id": payload.user_id,
                "tenant_id": payload.tenant_id,
                "source_file": payload.source_file,
                "source_run_id": payload.source_run_id or f"{payload.user_id}:{payload.run_date}",
                "status": "candidate",
                "confidence": 0.8,
                "generated_from_run_date": payload.run_date,
                "candidate_type": "evolution_stage",
                "payload_json": json.dumps({"value": soul_map.evolution_stage}, ensure_ascii=False, sort_keys=True),
                "should_write": 1,
                "created_at": now,
                "updated_at": now,
            }
        )
        return rows

    def _blind_spot_rows(self, *, payload: ReflectionWritebackRequest, now: str) -> list[dict[str, object]]:
        rows = []
        for candidate in payload.writeback_candidates.blind_spot_archive:
            if not candidate.should_write:
                continue
            rows.append(
                {
                    "id": uuid4().hex,
                    "run_date": payload.run_date,
                    "user_id": payload.user_id,
                    "tenant_id": payload.tenant_id,
                    "source_file": payload.source_file,
                    "source_run_id": payload.source_run_id or f"{payload.user_id}:{payload.run_date}",
                    "status": "candidate",
                    "confidence": 0.8,
                    "generated_from_run_date": payload.run_date,
                    "title": candidate.title,
                    "trigger_pattern": candidate.trigger_pattern,
                    "payload_json": json.dumps(candidate.model_dump(mode="json"), ensure_ascii=False, sort_keys=True),
                    "should_write": 1,
                    "created_at": now,
                    "updated_at": now,
                }
            )
        return rows

    def _belief_log_rows(self, *, payload: ReflectionWritebackRequest, now: str) -> list[dict[str, object]]:
        rows = []
        for candidate in payload.writeback_candidates.belief_logs:
            if not candidate.should_write:
                continue
            confidence = 0.85 if len(candidate.evidence) > 1 else 0.65
            rows.append(
                {
                    "id": uuid4().hex,
                    "run_date": payload.run_date,
                    "user_id": payload.user_id,
                    "tenant_id": payload.tenant_id,
                    "source_file": payload.source_file,
                    "source_run_id": payload.source_run_id or f"{payload.user_id}:{payload.run_date}",
                    "status": "candidate",
                    "confidence": confidence,
                    "generated_from_run_date": payload.run_date,
                    "belief_before": candidate.belief_before,
                    "belief_after": candidate.belief_after,
                    "tag": candidate.tag,
                    "payload_json": json.dumps(candidate.model_dump(mode="json"), ensure_ascii=False, sort_keys=True),
                    "should_write": 1,
                    "created_at": now,
                    "updated_at": now,
                }
            )
        return rows

    def _case_summary_rows(self, *, payload: ReflectionWritebackRequest, now: str) -> list[dict[str, object]]:
        candidate = payload.writeback_candidates.case_summary
        if not candidate.should_write:
            return []
        return [
            {
                "id": uuid4().hex,
                "run_date": payload.run_date,
                "user_id": payload.user_id,
                "tenant_id": payload.tenant_id,
                "source_file": payload.source_file,
                "source_run_id": payload.source_run_id or f"{payload.user_id}:{payload.run_date}",
                "status": "candidate",
                "confidence": 0.8,
                "generated_from_run_date": payload.run_date,
                "title": candidate.title,
                "payload_json": json.dumps(candidate.model_dump(mode="json"), ensure_ascii=False, sort_keys=True),
                "should_write": 1,
                "created_at": now,
                "updated_at": now,
            }
        ]

    def _principle_draft_rows(
        self, *, payload: ReflectionWritebackRequest, now: str
    ) -> tuple[list[dict[str, object]], list[str]]:
        rows: list[dict[str, object]] = []
        blocked: list[str] = []
        for candidate in payload.import_drafts.core_principle_candidates:
            if candidate.status != "draft":
                blocked.append(f"core principle draft {candidate.id} must keep status=draft")
                continue
            rows.append(
                {
                    "id": uuid4().hex,
                    "run_date": payload.run_date,
                    "user_id": payload.user_id,
                    "tenant_id": payload.tenant_id,
                    "source_file": payload.source_file,
                    "source_run_id": payload.source_run_id or f"{payload.user_id}:{payload.run_date}",
                    "status": "draft",
                    "confidence": 0.7,
                    "generated_from_run_date": candidate.generated_from_run_date,
                    "draft_code": candidate.id,
                    "title": candidate.title,
                    "cross_day_support_count": candidate.cross_day_support_count,
                    "payload_json": json.dumps(candidate.model_dump(mode="json"), ensure_ascii=False, sort_keys=True),
                    "created_at": now,
                    "updated_at": now,
                }
            )
        return rows, blocked

    def _puzzle_draft_rows(
        self, *, payload: ReflectionWritebackRequest, now: str
    ) -> tuple[list[dict[str, object]], list[str]]:
        rows: list[dict[str, object]] = []
        blocked: list[str] = []
        for candidate in payload.import_drafts.truth_puzzle_candidates:
            if candidate.status != "draft":
                blocked.append(f"truth puzzle draft {candidate.id} must keep status=draft")
                continue
            rows.append(
                {
                    "id": uuid4().hex,
                    "run_date": payload.run_date,
                    "user_id": payload.user_id,
                    "tenant_id": payload.tenant_id,
                    "source_file": payload.source_file,
                    "source_run_id": payload.source_run_id or f"{payload.user_id}:{payload.run_date}",
                    "status": "draft",
                    "confidence": 0.7,
                    "generated_from_run_date": candidate.generated_from_run_date,
                    "draft_code": candidate.id,
                    "title": candidate.title,
                    "cross_day_support_count": candidate.cross_day_support_count,
                    "payload_json": json.dumps(candidate.model_dump(mode="json"), ensure_ascii=False, sort_keys=True),
                    "created_at": now,
                    "updated_at": now,
                }
            )
        return rows, blocked

    def _overview_rows(
        self,
        *,
        user_id: str,
        metrics_rows: list[dict],
        dimension_rows: list[dict],
        pattern_rows: list[dict],
        generated_at: str,
    ) -> list[dict[str, object]]:
        rows = []
        dimension_counter = Counter()
        for window_days in (7, 30, 90):
            scoped_metrics = _windowed_rows(metrics_rows, window_days)
            if scoped_metrics:
                average_scores = {
                    key: round(sum(row[key] for row in scoped_metrics) / len(scoped_metrics), 2)
                    for key in (
                        "clarity_score",
                        "emotional_intensity_score",
                        "alignment_score",
                        "boundary_score",
                        "truth_discernment_score",
                        "memory_confidence_score",
                    )
                }
                latest_run_date = scoped_metrics[-1]["run_date"]
                run_dates = {row["run_date"] for row in scoped_metrics}
            else:
                average_scores = {
                    "clarity_score": 0.0,
                    "emotional_intensity_score": 0.0,
                    "alignment_score": 0.0,
                    "boundary_score": 0.0,
                    "truth_discernment_score": 0.0,
                    "memory_confidence_score": 0.0,
                }
                latest_run_date = None
                run_dates = set()
            scoped_dimensions = [row for row in dimension_rows if row["run_date"] in run_dates]
            dimension_counter.clear()
            for row in scoped_dimensions:
                dimension_counter[row["code"]] += 1
            top_dimensions = [
                {"dimension_code": code, "count": count}
                for code, count in dimension_counter.most_common(3)
            ]
            pattern_counter = Counter(row["pattern_key"] for row in pattern_rows)
            pattern_titles = {row["pattern_key"]: row["title"] for row in pattern_rows}
            top_patterns = [
                {"pattern_key": key, "title": pattern_titles.get(key), "count": count}
                for key, count in pattern_counter.most_common(3)
            ]
            overview_json = {
                "window_days": window_days,
                "runs_count": len(scoped_metrics),
                "latest_run_date": latest_run_date,
                "average_scores": average_scores,
                "top_dimensions": top_dimensions,
                "top_patterns": top_patterns,
            }
            rows.append(
                {
                    "id": uuid4().hex,
                    "user_id": user_id,
                    "window_days": window_days,
                    "generated_at": generated_at,
                    "overview_json": json.dumps(overview_json, ensure_ascii=False, sort_keys=True),
                }
            )
        return rows

    def _recurring_pattern_cache_rows(
        self, *, user_id: str, pattern_rows: list[dict], generated_at: str
    ) -> list[dict[str, object]]:
        grouped: dict[str, dict[str, object]] = {}
        for row in pattern_rows:
            current = grouped.setdefault(
                row["pattern_key"],
                {
                    "title": row["title"],
                    "frequency": 0,
                    "last_seen_at": row["last_seen_at"],
                },
            )
            current["frequency"] += row["count_increment"]
            current["last_seen_at"] = max(str(current["last_seen_at"]), str(row["last_seen_at"]))
        return [
            {
                "id": uuid4().hex,
                "user_id": user_id,
                "pattern_key": key,
                "title": value["title"],
                "frequency": value["frequency"],
                "last_seen_at": value["last_seen_at"],
                "generated_at": generated_at,
            }
            for key, value in grouped.items()
        ]

    def _belief_shift_cache_rows(
        self, *, user_id: str, belief_rows: list[dict], generated_at: str
    ) -> list[dict[str, object]]:
        grouped: dict[str, dict[str, object]] = {}
        for row in belief_rows:
            belief_key = f"{row['belief_before']}->{row['belief_after']}|{row['tag']}"
            current = grouped.setdefault(
                belief_key,
                {
                    "belief_before": row["belief_before"],
                    "belief_after": row["belief_after"],
                    "frequency": 0,
                    "last_seen_at": row["created_at"],
                },
            )
            current["frequency"] += 1
            current["last_seen_at"] = max(str(current["last_seen_at"]), str(row["created_at"]))
        return [
            {
                "id": uuid4().hex,
                "user_id": user_id,
                "belief_key": key,
                "belief_before": value["belief_before"],
                "belief_after": value["belief_after"],
                "frequency": value["frequency"],
                "last_seen_at": value["last_seen_at"],
                "generated_at": generated_at,
            }
            for key, value in grouped.items()
        ]

    def _blind_spot_cache_rows(
        self, *, user_id: str, blind_rows: list[dict], generated_at: str
    ) -> list[dict[str, object]]:
        grouped: dict[str, dict[str, object]] = {}
        for row in blind_rows:
            blind_key = f"{row['title']}|{row['trigger_pattern']}"
            current = grouped.setdefault(
                blind_key,
                {
                    "title": row["title"],
                    "trigger_pattern": row["trigger_pattern"],
                    "frequency": 0,
                    "last_seen_at": row["created_at"],
                },
            )
            current["frequency"] += 1
            current["last_seen_at"] = max(str(current["last_seen_at"]), str(row["created_at"]))
        return [
            {
                "id": uuid4().hex,
                "user_id": user_id,
                "blind_spot_key": key,
                "title": value["title"],
                "trigger_pattern": value["trigger_pattern"],
                "frequency": value["frequency"],
                "last_seen_at": value["last_seen_at"],
                "generated_at": generated_at,
            }
            for key, value in grouped.items()
        ]

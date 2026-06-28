from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


EVAL_RUBRIC = {
    "truth_alignment": {"weight": 0.35},
    "discoverability": {"weight": 0.25},
    "pattern_accuracy": {"weight": 0.20},
    "objectivity": {"weight": 0.10},
    "wisdom_bridge": {"weight": 0.10},
}


if round(sum(item["weight"] for item in EVAL_RUBRIC.values()), 10) != 1.0:
    raise ValueError("EVAL_RUBRIC weights must sum to exactly 1.0")


class DesignerAgent:
    """Reviews pending hard cases and evolves prompt knowledge."""

    def __init__(self, db_client: Any):
        self.db = db_client

    def review_hard_case(self, hardcase_id: str) -> dict:
        hard_case = self._load_hard_case(hardcase_id)
        diagnosis = self.diagnose_hard_case(hard_case)
        prompt_a, prompt_b = self.generate_prompt_variants(hardcase_id, diagnosis)
        evaluation = self.evaluate_prompt_pair(prompt_a, prompt_b, diagnosis)
        abtest_id = self._record_abtest(hardcase_id, prompt_a, prompt_b, evaluation)
        review = self._record_designer_review(hardcase_id, diagnosis, evaluation)
        evolution = self._record_knowledge_evolution(hardcase_id, evaluation, review)
        self._update_hard_case_status(hardcase_id, diagnosis, evaluation)
        self._commit()

        return {
            "hardcase_id": hardcase_id,
            "diagnosis": diagnosis,
            "prompt_a": prompt_a,
            "prompt_b": prompt_b,
            "abtest_id": abtest_id,
            "evaluation": evaluation,
            "designer_review": review,
            "knowledge_evolution": evolution,
        }

    def review_pending(self, limit: int = 5) -> dict:
        rows = self._fetchall(
            """
            SELECT userid
              FROM hardcasebuffer
             WHERE COALESCE(status, 'pending') = 'pending'
             ORDER BY createdat ASC
             LIMIT ?
            """,
            (limit,),
        )
        reviews = [self.review_hard_case(dict(row)["userid"]) for row in rows]
        return {"processed": len(reviews), "reviews": reviews}

    def diagnose_hard_case(self, hard_case: dict) -> dict:
        hardcase_id = hard_case["userid"]
        reasons = self._loads(hard_case.get("reasons"), [])
        soul_map = self._load_soul_map(hardcase_id)
        blind_spots = self._load_blind_spots(hardcase_id)
        primary_pattern = self._primary_pattern(soul_map, reasons)
        primary_pattern_id = self._primary_pattern_id(soul_map, primary_pattern)
        recurring_count = self._pattern_frequency(soul_map, primary_pattern_id)
        severity = self._max_blind_spot_severity(blind_spots)

        findings = {
            "hardcase_id": hardcase_id,
            "reasons": reasons,
            "primary_pattern": primary_pattern,
            "primary_pattern_id": primary_pattern_id,
            "recurring_count": recurring_count,
            "severity": severity,
            "evolution_stage": (soul_map or {}).get("evolutionstage", "unknown"),
            "blind_spot_count": len(blind_spots),
            "diagnosis": self._diagnosis_text(primary_pattern, severity, reasons),
            "needs_human_coach_if_inconclusive": True,
        }
        return findings

    def generate_prompt_variants(
        self,
        hardcase_id: str,
        diagnosis: dict,
    ) -> tuple[dict, dict]:
        now = self._now()
        pattern = diagnosis.get("primary_pattern") or "the recurring pattern"
        prompt_a = {
            "id": f"pv_{uuid4().hex}",
            "hardcaseid": hardcase_id,
            "prompttemplate": (
                "Name only the observable pattern, then ask one Socratic question "
                f"that lets the user discover how '{pattern}' is operating right now. "
                "Do not diagnose, comfort, or debate."
            ),
            "promptlabel": "Pattern Mirror Question",
            "prompttype": "dialogue",
            "version": 1,
            "parentversionid": None,
            "createdat": now,
        }
        prompt_b = {
            "id": f"pv_{uuid4().hex}",
            "hardcaseid": hardcase_id,
            "prompttemplate": (
                "Invite the user to test the truth in one concrete life action within 24 hours. "
                f"Use '{pattern}' as the pattern anchor, then ask what evidence would confirm a shift."
            ),
            "promptlabel": "Evidence Bridge Experiment",
            "prompttype": "evidence",
            "version": 1,
            "parentversionid": None,
            "createdat": now,
        }
        self._insert_prompt_version(prompt_a)
        self._insert_prompt_version(prompt_b)
        return prompt_a, prompt_b

    def evaluate_prompt_pair(self, prompt_a: dict, prompt_b: dict, diagnosis: dict) -> dict:
        if not diagnosis.get("reasons") and diagnosis.get("severity") == "none":
            return {
                "status": "inconclusive",
                "winner_id": None,
                "scores": {},
                "rubric": EVAL_RUBRIC,
                "reason": "Hard case lacks enough evidence for safe prompt evolution.",
                "recommended_action": "escalate_to_human_coach",
            }

        scores = {
            prompt_a["id"]: self._score_prompt(prompt_a, diagnosis),
            prompt_b["id"]: self._score_prompt(prompt_b, diagnosis),
        }
        totals = {
            prompt_id: round(
                sum(
                    section_scores[key] * EVAL_RUBRIC[key]["weight"]
                    for key in EVAL_RUBRIC
                ),
                4,
            )
            for prompt_id, section_scores in scores.items()
        }
        winner_id = max(totals, key=totals.get)
        loser_id = prompt_b["id"] if winner_id == prompt_a["id"] else prompt_a["id"]
        margin = totals[winner_id] - totals[loser_id]
        if margin < 0.03:
            return {
                "status": "inconclusive",
                "winner_id": None,
                "scores": scores,
                "totals": totals,
                "rubric": EVAL_RUBRIC,
                "reason": "Prompt scores were too close to declare a reliable winner.",
                "recommended_action": "escalate_to_human_coach",
            }
        return {
            "status": "completed",
            "winner_id": winner_id,
            "scores": scores,
            "totals": totals,
            "rubric": EVAL_RUBRIC,
            "reason": "Winner selected by weighted truth-first rubric.",
            "recommended_action": "apply_prompt_winner",
        }

    def _score_prompt(self, prompt: dict, diagnosis: dict) -> dict:
        text = f"{prompt['promptlabel']} {prompt['prompttemplate']}".lower()
        is_dialogue = prompt["prompttype"] == "dialogue"
        is_evidence = prompt["prompttype"] == "evidence"
        severity = diagnosis.get("severity")
        reason_count = len(diagnosis.get("reasons", []))
        pattern_known = bool(diagnosis.get("primary_pattern"))

        return {
            "truth_alignment": 0.90 if "truth" in text or "observable pattern" in text else 0.75,
            "discoverability": 0.92 if is_dialogue and "ask" in text else 0.74,
            "pattern_accuracy": 0.88 if pattern_known else 0.62,
            "objectivity": 0.86 if "observable" in text or "evidence" in text else 0.70,
            "wisdom_bridge": 0.90 if is_evidence or severity in {"high", "critical"} or reason_count >= 2 else 0.76,
        }

    def _load_hard_case(self, hardcase_id: str) -> dict:
        row = self._fetchone(
            "SELECT * FROM hardcasebuffer WHERE userid = ?",
            (hardcase_id,),
        )
        if not row:
            raise ValueError(f"Hard case '{hardcase_id}' was not found")
        return dict(row)

    def _load_soul_map(self, user_id: str) -> dict | None:
        row = self._fetchone("SELECT * FROM soulmaps WHERE userid = ?", (user_id,))
        return dict(row) if row else None

    def _load_blind_spots(self, user_id: str) -> list[dict]:
        rows = self._fetchall(
            """
            SELECT *
              FROM blindspotarchives
             WHERE userid = ?
             ORDER BY frequency DESC
            """,
            (user_id,),
        )
        return [dict(row) for row in rows]

    def _primary_pattern(self, soul_map: dict | None, reasons: list) -> str:
        if soul_map:
            patterns = self._loads(soul_map.get("recurringpatternsjson"), [])
            weights = self._loads(soul_map.get("patternweightsjson"), {})
            if patterns:
                top = sorted(
                    patterns,
                    key=lambda item: weights.get(item.get("id", ""), {}).get("weight", 0),
                    reverse=True,
                )[0]
                return top.get("description") or top.get("id", "")
        return str(reasons[0]) if reasons else ""

    def _primary_pattern_id(self, soul_map: dict | None, fallback: str) -> str:
        if soul_map:
            patterns = self._loads(soul_map.get("recurringpatternsjson"), [])
            weights = self._loads(soul_map.get("patternweightsjson"), {})
            if patterns:
                top = sorted(
                    patterns,
                    key=lambda item: weights.get(item.get("id", ""), {}).get("weight", 0),
                    reverse=True,
                )[0]
                return top.get("id", fallback)
        return fallback

    def _pattern_frequency(self, soul_map: dict | None, pattern_id: str) -> int:
        if not soul_map or not pattern_id:
            return 0
        weights = self._loads(soul_map.get("patternweightsjson"), {})
        return int(weights.get(pattern_id, {}).get("frequency", 0))

    def _max_blind_spot_severity(self, blind_spots: list[dict]) -> str:
        rank = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        severity = "none"
        for spot in blind_spots:
            candidate = spot.get("severity") or "medium"
            if rank.get(candidate, 0) > rank[severity]:
                severity = candidate
        return severity

    def _diagnosis_text(self, pattern: str, severity: str, reasons: list) -> str:
        if not pattern and not reasons:
            return "Insufficient evidence to safely evolve the prompt."
        return (
            f"Hard case centers on '{pattern or reasons[0]}', "
            f"with severity '{severity}'. The prompt should increase discoverability "
            "without turning the pattern into a user identity label."
        )

    def _insert_prompt_version(self, prompt: dict) -> None:
        self._execute(
            """
            INSERT INTO promptversions (
              id, hardcaseid, prompttemplate, promptlabel, prompttype,
              version, parentversionid, createdat
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                prompt["id"],
                prompt["hardcaseid"],
                prompt["prompttemplate"],
                prompt["promptlabel"],
                prompt["prompttype"],
                prompt["version"],
                prompt["parentversionid"],
                prompt["createdat"],
            ),
        )

    def _record_abtest(
        self,
        hardcase_id: str,
        prompt_a: dict,
        prompt_b: dict,
        evaluation: dict,
    ) -> str:
        now = self._now()
        abtest_id = f"ab_{uuid4().hex}"
        self._execute(
            """
            INSERT INTO promptabtests (
              id, hardcaseid, promptaid, promptbid, status,
              winnerid, evaluationjson, startdat, completedat
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                abtest_id,
                hardcase_id,
                prompt_a["id"],
                prompt_b["id"],
                evaluation["status"],
                evaluation.get("winner_id"),
                json.dumps(evaluation, ensure_ascii=False),
                now,
                now,
            ),
        )
        return abtest_id

    def _record_designer_review(
        self,
        hardcase_id: str,
        diagnosis: dict,
        evaluation: dict,
    ) -> dict:
        now = self._now()
        review = {
            "id": f"dr_{uuid4().hex}",
            "hardcaseid": hardcase_id,
            "reviewedby": "designer_agent",
            "findingsjson": diagnosis,
            "newprincipleproposed": False,
            "promptwinner": evaluation.get("winner_id"),
            "action": evaluation["recommended_action"],
            "createdat": now,
        }
        self._execute(
            """
            INSERT INTO designerreviews (
              id, hardcaseid, reviewedby, findingsjson, newprincipleproposed,
              promptwinner, action, createdat
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                review["id"],
                review["hardcaseid"],
                review["reviewedby"],
                json.dumps(review["findingsjson"], ensure_ascii=False),
                int(review["newprincipleproposed"]),
                review["promptwinner"],
                review["action"],
                review["createdat"],
            ),
        )
        return review

    def _record_knowledge_evolution(
        self,
        hardcase_id: str,
        evaluation: dict,
        review: dict,
    ) -> dict:
        evolution = {
            "id": f"ke_{uuid4().hex}",
            "sourcetype": "hardcasebuffer",
            "sourceid": hardcase_id,
            "changetype": (
                "prompt_variant_won"
                if evaluation.get("winner_id")
                else "coach_escalation_required"
            ),
            "targetid": evaluation.get("winner_id"),
            "rationaljson": {
                "evaluation": evaluation,
                "designer_review_id": review["id"],
            },
            "createdat": self._now(),
        }
        self._execute(
            """
            INSERT INTO knowledgeevolutions (
              id, sourcetype, sourceid, changetype, targetid, rationaljson, createdat
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evolution["id"],
                evolution["sourcetype"],
                evolution["sourceid"],
                evolution["changetype"],
                evolution["targetid"],
                json.dumps(evolution["rationaljson"], ensure_ascii=False),
                evolution["createdat"],
            ),
        )
        return evolution

    def _update_hard_case_status(
        self,
        hardcase_id: str,
        diagnosis: dict,
        evaluation: dict,
    ) -> None:
        resolved = evaluation["status"] == "completed"
        status = "resolved" if resolved else "coach_review"
        self._execute(
            """
            UPDATE hardcasebuffer SET
              status = ?,
              summaryjson = ?,
              resolvedat = ?,
              resolutionnote = ?
             WHERE userid = ?
            """,
            (
                status,
                json.dumps(
                    {"diagnosis": diagnosis, "evaluation": evaluation},
                    ensure_ascii=False,
                ),
                self._now() if resolved else None,
                evaluation["reason"],
                hardcase_id,
            ),
        )

    def _loads(self, raw: Any, default: Any) -> Any:
        if raw in (None, ""):
            return default
        try:
            return json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            return default

    def _fetchone(self, sql: str, params: tuple = ()):  # type: ignore[no-untyped-def]
        getter = getattr(self.db, "fetchone", None)
        if callable(getter):
            return getter(sql, params)
        return self.db.execute(sql, params).fetchone()

    def _fetchall(self, sql: str, params: tuple = ()):  # type: ignore[no-untyped-def]
        getter = getattr(self.db, "fetchall", None)
        if callable(getter):
            return getter(sql, params)
        return self.db.execute(sql, params).fetchall()

    def _execute(self, sql: str, params: tuple = ()):  # type: ignore[no-untyped-def]
        executor = getattr(self.db, "execute", None)
        if callable(executor):
            return executor(sql, params)
        raise TypeError("db_client must provide execute()")

    def _commit(self) -> None:
        committer = getattr(self.db, "commit", None)
        if callable(committer):
            committer()

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

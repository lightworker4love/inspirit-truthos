from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4


EVOLUTION_STAGES = [
    "awakening",
    "recognizing",
    "understanding",
    "practicing",
    "integrating",
    "transcended",
]


class SoulMapEngine:
    """Accumulates, weights, and evolves a user's Soul Map."""

    def __init__(self, db_client: Any):
        self.db = db_client

    def get_soul_map(self, user_id: str) -> Optional[dict]:
        row = self._fetchone("SELECT * FROM soulmaps WHERE userid = ?", (user_id,))
        if not row:
            return None
        return self._deserialize(row)

    def get_or_create_soul_map(self, user_id: str) -> dict:
        soul_map = self.get_soul_map(user_id)
        if soul_map:
            return soul_map

        now = datetime.now(timezone.utc).isoformat()
        soul_map = self._create_empty(user_id, now)
        self._save(user_id, soul_map, now)
        return soul_map

    def get_primary_pattern(self, user_id: str) -> str:
        soul_map = self.get_soul_map(user_id)
        if not soul_map:
            return "Soul Map not yet built for this user."

        weights = soul_map.get("pattern_weights", {})
        patterns = soul_map.get("recurring_patterns", [])
        if not patterns:
            return "No recurring patterns detected yet."

        sorted_patterns = sorted(
            patterns,
            key=lambda pattern: weights.get(pattern.get("id", ""), {}).get("weight", 0),
            reverse=True,
        )
        top = sorted_patterns[0]
        return top.get("description") or top.get("label") or "Unknown pattern"

    def get_summary_for_injection(self, user_id: str) -> str:
        soul_map = self.get_soul_map(user_id)
        if not soul_map:
            return ""
        return soul_map.get("soul_map_summary", "")

    def update_from_query_result(
        self,
        user_id: str,
        detected_patterns: list[str],
        matched_dimension: str,
        matched_principle_id: str,
        belief_shift_detected: bool,
        discovery_triggered: bool,
        session_id: str,
    ) -> dict:
        soul_map = self.get_or_create_soul_map(user_id)
        now = datetime.now(timezone.utc).isoformat()
        changes = {"updated": [], "new_patterns": [], "stage_change": None}
        delta = {
            "new_patterns": [],
            "stage_change": None,
            "new_blind_spots": [],
            "lessons_updated": [],
            "truth_score": 0,
        }

        clean_patterns = [pattern for pattern in detected_patterns if pattern]
        for pattern in clean_patterns:
            soul_map, change = self._update_pattern_weight(soul_map, pattern, now)
            if change:
                changes["updated"].append(change)

        existing_ids = {pattern.get("id") for pattern in soul_map.get("recurring_patterns", [])}
        for pattern in clean_patterns:
            if pattern not in existing_ids:
                soul_map["recurring_patterns"].append(
                    {
                        "id": pattern,
                        "description": pattern,
                        "first_seen": now,
                        "dimension": matched_dimension,
                        "source_session_id": session_id,
                    }
                )
                existing_ids.add(pattern)
                changes["new_patterns"].append(pattern)
                delta["new_patterns"].append(pattern)

        if matched_principle_id:
            existing_lessons = {
                lesson.get("principle_id")
                for lesson in soul_map.get("active_lessons", [])
            }
            soul_map = self._update_active_lessons(
                soul_map, matched_principle_id, matched_dimension, now
            )
            if matched_principle_id not in existing_lessons:
                delta["lessons_updated"].append(matched_principle_id)

        if belief_shift_detected or discovery_triggered:
            soul_map["last_truth_shift_at"] = now
            new_stage = self._evaluate_evolution_stage(soul_map)
            if new_stage != soul_map.get("evolution_stage"):
                old_stage = soul_map.get("evolution_stage", "awakening")
                trigger = clean_patterns[-1] if clean_patterns else matched_dimension
                soul_map["evolution_stage"] = new_stage
                soul_map = self._record_evolution_history(
                    soul_map, old_stage, new_stage, trigger, now
                )
                changes["stage_change"] = {"from": old_stage, "to": new_stage}
                delta["stage_change"] = changes["stage_change"]

        self._save(user_id, soul_map, now)
        changes["updated_at"] = now
        changes["updated"] = changes["updated"]
        changes["delta"] = delta
        changes["was_updated"] = bool(
            changes["updated"]
            or changes["new_patterns"]
            or changes["stage_change"]
            or delta["lessons_updated"]
        )
        return changes

    def update_soul_map(self, user_id: str, truth_result: dict, query: str) -> dict:
        patterns = truth_result.get("detected_patterns") or truth_result.get("patterns") or []
        if isinstance(patterns, str):
            patterns = [patterns]
        result = self.update_from_query_result(
            user_id=user_id,
            detected_patterns=patterns,
            matched_dimension=truth_result.get("matched_dimension")
            or truth_result.get("dimension")
            or "discernment",
            matched_principle_id=truth_result.get("matched_principle_id", ""),
            belief_shift_detected=bool(truth_result.get("belief_shift_detected")),
            discovery_triggered=bool(truth_result.get("discovery_triggered")),
            session_id=truth_result.get("session_id", ""),
        )
        result["delta"]["truth_score"] = truth_result.get("truth_score", 0)
        return {"updated": bool(result.get("was_updated")), "delta": result.get("delta", {})}

    def update_blind_spot(
        self,
        user_id: str,
        trigger_pattern: str,
        known_theory: str,
        practical_failure_mode: str,
        domains: list[str],
        related_puzzle_ids: list[str],
    ) -> str:
        now = datetime.now(timezone.utc).isoformat()
        existing = self._fetchone(
            "SELECT * FROM blindspotarchives WHERE userid = ? AND triggerpattern = ?",
            (user_id, trigger_pattern),
        )
        clean_domains = [domain for domain in domains if domain]

        if existing:
            existing_row = dict(existing)
            new_frequency = (existing_row.get("frequency") or 1) + 1
            severity = self._calculate_severity(new_frequency, clean_domains)
            self._execute(
                """
                UPDATE blindspotarchives SET
                  frequency = ?, lastseenat = ?, knowntheory = ?,
                  practicalfailuremode = ?, domainsjson = ?,
                  relatedpuzzlesjson = ?, severity = ?
                 WHERE id = ?
                """,
                (
                    new_frequency,
                    now,
                    known_theory,
                    practical_failure_mode,
                    json.dumps(clean_domains, ensure_ascii=False),
                    json.dumps(related_puzzle_ids, ensure_ascii=False),
                    severity,
                    existing_row["id"],
                ),
            )
            self._commit()
            return existing_row["id"]

        new_id = str(uuid4())
        self._execute(
            """
            INSERT INTO blindspotarchives (
              id, userid, title, triggerpattern, knowntheory,
              practicalfailuremode, suggestedanchorsjson, relatedpuzzlesjson,
              frequency, lastseenat, domainsjson, severity, resolutionstatus, createdat
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                new_id,
                user_id,
                trigger_pattern[:80] or "Unlabeled blind spot",
                trigger_pattern,
                known_theory,
                practical_failure_mode,
                json.dumps([], ensure_ascii=False),
                json.dumps(related_puzzle_ids, ensure_ascii=False),
                1,
                now,
                json.dumps(clean_domains, ensure_ascii=False),
                "medium",
                "active",
                now,
            ),
        )
        self._commit()
        return new_id

    def detect_hard_case(self, user_id: str) -> dict:
        soul_map = self.get_soul_map(user_id)
        if not soul_map:
            return {"is_hard_case": False}

        reasons = []
        weights = soul_map.get("pattern_weights", {})
        history = soul_map.get("evolution_history", [])

        stuck = [
            pattern_id
            for pattern_id, data in weights.items()
            if data.get("frequency", 0) >= 5 and data.get("weight", 0) > 0.6
        ]
        if stuck:
            reasons.append(f"Pattern(s) {stuck} recurring 5+ times with high weight")

        critical_spots = self._fetchall(
            "SELECT title FROM blindspotarchives WHERE userid = ? AND severity = 'critical'",
            (user_id,),
        )
        if critical_spots:
            reasons.append(f"{len(critical_spots)} critical blind spot(s) detected")

        if len(history) >= 10:
            recent_stages = [entry.get("to_stage") for entry in history[-10:]]
            if len(set(recent_stages)) == 1:
                reasons.append(
                    f"Evolution stage stagnant at '{recent_stages[-1]}' for 10+ interactions"
                )

        return {
            "is_hard_case": bool(reasons),
            "reasons": reasons,
            "recommended_action": "escalate_to_coach_review" if reasons else None,
        }

    def _evaluate_evolution_stage(self, soul_map: dict) -> str:
        patterns = soul_map.get("recurring_patterns", [])
        weights = soul_map.get("pattern_weights", {})
        integrated = soul_map.get("integrated_dimensions", [])
        history = soul_map.get("evolution_history", [])

        score = 0
        if len(patterns) >= 1:
            score += 1
        if soul_map.get("last_truth_shift_at"):
            score += 1
        if any(data.get("frequency", 0) >= 3 for data in weights.values()):
            score += 1
        if integrated:
            score += 1
        if len(history) >= 3:
            score += 1
        if len(history) >= 7:
            score += 1

        stage_map = {
            0: "awakening",
            1: "awakening",
            2: "recognizing",
            3: "understanding",
            4: "practicing",
            5: "integrating",
            6: "transcended",
        }
        return stage_map.get(min(score, 6), "awakening")

    def _update_pattern_weight(self, soul_map: dict, pattern_id: str, now: str):
        weights = soul_map.setdefault("pattern_weights", {})
        entry = weights.get(pattern_id, {"frequency": 0, "weight": 0.0, "last_seen": now})
        entry["frequency"] += 1
        entry["last_seen"] = now
        raw_weight = round(1 - math.exp(-entry["frequency"] / 5), 4)
        entry["weight"] = min(raw_weight, 0.9999)
        weights[pattern_id] = entry
        soul_map["pattern_weights"] = weights
        return soul_map, {"pattern": pattern_id, "new_weight": entry["weight"]}

    def _update_active_lessons(self, soul_map, principle_id, dimension, now):
        lessons = soul_map.setdefault("active_lessons", [])
        existing_ids = {lesson.get("principle_id") for lesson in lessons}
        if principle_id not in existing_ids:
            lessons.append(
                {
                    "principle_id": principle_id,
                    "dimension": dimension,
                    "first_activated": now,
                    "status": "active",
                }
            )
        soul_map["active_lessons"] = lessons
        return soul_map

    def _record_evolution_history(self, soul_map, old_stage, new_stage, trigger, now):
        history = soul_map.setdefault("evolution_history", [])
        history.append(
            {
                "from_stage": old_stage,
                "to_stage": new_stage,
                "trigger_pattern": trigger,
                "timestamp": now,
            }
        )
        soul_map["evolution_history"] = history
        return soul_map

    def _calculate_severity(self, frequency: int, domains: list) -> str:
        if len(domains) >= 3 or frequency >= 7:
            return "critical"
        if len(domains) >= 2 or frequency >= 4:
            return "high"
        if frequency >= 2:
            return "medium"
        return "low"

    def _create_empty(self, user_id: str, now: str) -> dict:
        return {
            "user_id": user_id,
            "recurring_patterns": [],
            "limiting_beliefs": [],
            "emotional_signatures": [],
            "active_lessons": [],
            "evolution_stage": "awakening",
            "last_truth_shift_at": None,
            "pattern_weights": {},
            "integrated_dimensions": [],
            "transcended_patterns": [],
            "evolution_history": [],
            "soul_map_summary": "",
            "created_at": now,
            "updated_at": now,
        }

    def _deserialize(self, row: Any) -> dict:
        raw = dict(row)
        return {
            "id": raw.get("id"),
            "user_id": raw.get("userid"),
            "recurring_patterns": self._json_value(raw.get("recurringpatternsjson"), []),
            "limiting_beliefs": self._json_value(raw.get("limitingbeliefsjson"), []),
            "emotional_signatures": self._json_value(raw.get("emotionalsignaturesjson"), []),
            "active_lessons": self._json_value(raw.get("activelessonsjson"), []),
            "evolution_stage": raw.get("evolutionstage") or "awakening",
            "last_truth_shift_at": raw.get("lasttruthshiftat"),
            "pattern_weights": self._json_value(raw.get("patternweightsjson"), {}),
            "integrated_dimensions": self._json_value(raw.get("integrateddimensionsjson"), []),
            "transcended_patterns": self._json_value(raw.get("transcendedpatternsjson"), []),
            "evolution_history": self._json_value(raw.get("evolutionhistoryjson"), []),
            "soul_map_summary": raw.get("soulmapsummary") or "",
            "created_at": raw.get("createdat"),
            "updated_at": raw.get("updatedat"),
        }

    def _save(self, user_id: str, soul_map: dict, now: str):
        existing = self._fetchone("SELECT id FROM soulmaps WHERE userid = ?", (user_id,))
        data = (
            json.dumps(soul_map.get("recurring_patterns", []), ensure_ascii=False),
            json.dumps(soul_map.get("limiting_beliefs", []), ensure_ascii=False),
            json.dumps(soul_map.get("emotional_signatures", []), ensure_ascii=False),
            json.dumps(soul_map.get("active_lessons", []), ensure_ascii=False),
            soul_map.get("evolution_stage", "awakening"),
            soul_map.get("last_truth_shift_at"),
            json.dumps(soul_map.get("pattern_weights", {}), ensure_ascii=False),
            json.dumps(soul_map.get("integrated_dimensions", []), ensure_ascii=False),
            json.dumps(soul_map.get("transcended_patterns", []), ensure_ascii=False),
            json.dumps(soul_map.get("evolution_history", []), ensure_ascii=False),
            soul_map.get("soul_map_summary", ""),
            now,
        )
        if existing:
            self._execute(
                """
                UPDATE soulmaps SET
                  recurringpatternsjson = ?, limitingbeliefsjson = ?,
                  emotionalsignaturesjson = ?, activelessonsjson = ?,
                  evolutionstage = ?, lasttruthshiftat = ?,
                  patternweightsjson = ?, integrateddimensionsjson = ?,
                  transcendedpatternsjson = ?, evolutionhistoryjson = ?,
                  soulmapsummary = ?, updatedat = ?
                 WHERE userid = ?
                """,
                (*data, user_id),
            )
        else:
            self._execute(
                """
                INSERT INTO soulmaps (
                  id, userid, recurringpatternsjson, limitingbeliefsjson,
                  emotionalsignaturesjson, activelessonsjson,
                  evolutionstage, lasttruthshiftat,
                  patternweightsjson, integrateddimensionsjson,
                  transcendedpatternsjson, evolutionhistoryjson,
                  soulmapsummary, createdat, updatedat
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (str(uuid4()), user_id, *data[:-1], now, data[-1]),
            )
        self._commit()

    def _json_value(self, raw: Any, default: Any) -> Any:
        if raw in (None, ""):
            return default
        try:
            value = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            return default
        return value

    def _fetchone(self, sql: str, params: tuple = ()): 
        getter = getattr(self.db, "fetchone", None)
        if callable(getter):
            return getter(sql, params)
        return self.db.execute(sql, params).fetchone()

    def _fetchall(self, sql: str, params: tuple = ()): 
        getter = getattr(self.db, "fetchall", None)
        if callable(getter):
            return getter(sql, params)
        return self.db.execute(sql, params).fetchall()

    def _execute(self, sql: str, params: tuple = ()): 
        executor = getattr(self.db, "execute", None)
        if callable(executor):
            return executor(sql, params)
        raise TypeError("db_client must provide execute()")

    def _commit(self) -> None:
        committer = getattr(self.db, "commit", None)
        if callable(committer):
            committer()

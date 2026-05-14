from __future__ import annotations

from enum import Enum
from typing import Any


class VerificationTrack(str, Enum):
    STILLNESS = "stillness"
    DIALOGUE = "dialogue"
    EVIDENCE = "evidence"


class TruthVerificationLayer:
    def __init__(self, belief_log_client: Any, soul_map_client: Any):
        self.belief_log = belief_log_client
        self.soul_map = soul_map_client

    def select_track(
        self,
        puzzle_verification_mode: str,
        discernment_score: float,
        user_id: str,
        related_principle_id: str | None,
    ) -> VerificationTrack:
        if puzzle_verification_mode == VerificationTrack.STILLNESS.value and discernment_score >= 0.85:
            return VerificationTrack.STILLNESS

        if related_principle_id:
            evidence = self.get_life_evidence_for_principle(
                user_id=user_id,
                principle_id=related_principle_id,
            )
            if evidence:
                return VerificationTrack.EVIDENCE

        return VerificationTrack.DIALOGUE

    def build_verification_context(
        self,
        track: VerificationTrack,
        truth_view: str,
        life_evidence: list,
        soul_map_patterns: list,
    ) -> dict:
        normalized_track = VerificationTrack(track)
        base = {
            "track": normalized_track.value,
            "objectivity_reminder": (
                "This truth exists regardless of whether the person knows, "
                "believes, or imagines it. Do not frame it as the person's creation."
            ),
            "truth_view": truth_view,
        }

        if normalized_track == VerificationTrack.EVIDENCE:
            base["life_evidence"] = life_evidence
            base["instruction"] = (
                "Reference the user's own recorded life events as evidence. "
                "Let their lived experience speak louder than any argument."
            )
        elif normalized_track == VerificationTrack.STILLNESS:
            base["instruction"] = (
                "Present this truth quietly and directly. "
                "Do not invite debate. The truth is self-evident. "
                "Ask only: 'Does this land as true for you?'"
            )
        elif normalized_track == VerificationTrack.DIALOGUE:
            base["soul_map_patterns"] = soul_map_patterns
            base["instruction"] = (
                "Use Socratic questions only. Do not state the truth directly. "
                "Guide the user to discover it through their own reasoning. "
                "The goal is discoverability - they must arrive at it themselves."
            )

        return base

    def get_life_evidence_for_principle(self, user_id: str, principle_id: str | None) -> list:
        if not principle_id or not self.belief_log:
            return []
        getter = getattr(self.belief_log, "get_evidence_for_principle", None)
        if not callable(getter):
            return []
        return getter(user_id=user_id, principle_id=principle_id) or []

    def get_soul_map_patterns(self, user_id: str) -> list:
        if not self.soul_map:
            return []
        getter = getattr(self.soul_map, "get_patterns", None)
        if not callable(getter):
            getter = getattr(self.soul_map, "get_recurring_patterns", None)
        if not callable(getter):
            return []
        return getter(user_id=user_id) or []


def detect_discovery_triggered(
    track: VerificationTrack,
    coach_review_flag: bool | None = None,
    user_confirmation: str | None = None,
) -> int:
    if VerificationTrack(track) != VerificationTrack.DIALOGUE:
        return 0
    if coach_review_flag is True:
        return 1
    if not user_confirmation:
        return 0

    normalized = user_confirmation.strip().lower()
    discovery_markers = (
        "i see",
        "i realize",
        "i discovered",
        "i found",
        "that is true",
        "this lands",
        "makes sense now",
        "我發現",
        "我明白",
        "我懂了",
        "是真的",
    )
    return int(any(marker in normalized for marker in discovery_markers))

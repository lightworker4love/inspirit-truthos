from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/truth-api"))

from app import truth_verification
from app.truth_map import build_truth_map


class BeliefLogClient:
    def __init__(self, evidence=None):
        self.evidence = evidence or []

    def get_evidence_for_principle(self, user_id, principle_id):
        return self.evidence


class SoulMapClient:
    def __init__(self, patterns=None):
        self.patterns = patterns or []

    def get_recurring_patterns(self, user_id):
        return self.patterns


def test_selects_stillness_for_high_discernment_stillness_puzzle():
    layer = truth_verification.TruthVerificationLayer(BeliefLogClient(), SoulMapClient())

    track = layer.select_track(
        puzzle_verification_mode="stillness",
        discernment_score=0.91,
        user_id="user-1",
        related_principle_id="principle-1",
    )

    assert track == truth_verification.VerificationTrack.STILLNESS


def test_stillness_mode_below_threshold_defaults_to_dialogue_without_evidence():
    layer = truth_verification.TruthVerificationLayer(BeliefLogClient(), SoulMapClient())

    track = layer.select_track(
        puzzle_verification_mode="stillness",
        discernment_score=0.84,
        user_id="user-1",
        related_principle_id="principle-1",
    )

    assert track == truth_verification.VerificationTrack.DIALOGUE


def test_selects_evidence_when_belief_log_has_life_evidence():
    layer = truth_verification.TruthVerificationLayer(
        BeliefLogClient(evidence=[{"event": "Repeated cause-effect pattern"}]),
        SoulMapClient(),
    )

    track = layer.select_track(
        puzzle_verification_mode="dialogue",
        discernment_score=0.2,
        user_id="user-1",
        related_principle_id="principle-1",
    )

    assert track == truth_verification.VerificationTrack.EVIDENCE


def test_evidence_requires_related_principle_id():
    layer = truth_verification.TruthVerificationLayer(
        BeliefLogClient(evidence=[{"event": "Evidence exists"}]),
        SoulMapClient(),
    )

    track = layer.select_track(
        puzzle_verification_mode="dialogue",
        discernment_score=0.2,
        user_id="user-1",
        related_principle_id=None,
    )

    assert track == truth_verification.VerificationTrack.DIALOGUE


def test_dialogue_context_uses_socratic_instruction_and_patterns():
    layer = truth_verification.TruthVerificationLayer(BeliefLogClient(), SoulMapClient())

    context = layer.build_verification_context(
        track=truth_verification.VerificationTrack.DIALOGUE,
        truth_view="The axiom is already true.",
        life_evidence=[],
        soul_map_patterns=["avoidance repeats under pressure"],
    )

    assert context["track"] == "dialogue"
    assert "Socratic questions only" in context["instruction"]
    assert context["soul_map_patterns"] == ["avoidance repeats under pressure"]
    assert "regardless" in context["objectivity_reminder"]


def test_evidence_context_includes_life_evidence():
    layer = truth_verification.TruthVerificationLayer(BeliefLogClient(), SoulMapClient())

    context = layer.build_verification_context(
        track=truth_verification.VerificationTrack.EVIDENCE,
        truth_view="Cause and effect operates.",
        life_evidence=[{"event": "A repeated outcome"}],
        soul_map_patterns=[],
    )

    assert context["track"] == "evidence"
    assert context["life_evidence"] == [{"event": "A repeated outcome"}]
    assert "lived experience" in context["instruction"]


def test_detects_dialogue_self_discovery_from_user_confirmation():
    result = truth_verification.detect_discovery_triggered(
        track=truth_verification.VerificationTrack.DIALOGUE,
        user_confirmation="I realize this pattern is true in my life.",
    )

    assert result == 1


def test_does_not_mark_discovery_for_non_dialogue_track():
    result = truth_verification.detect_discovery_triggered(
        track=truth_verification.VerificationTrack.STILLNESS,
        coach_review_flag=True,
    )

    assert result == 0


def test_truth_map_is_additive_and_keeps_existing_fields():
    truth_map = build_truth_map(
        user_message="I keep avoiding direct conversations.",
        top_puzzle={"fact_layer": "Avoided conversation"},
        soul_map_patterns=[{"pattern": "avoidance repeats under relational pressure"}],
        matched_principle={
            "axiom": "Avoidance compounds until it is faced.",
            "objectivity_statement": "This principle operates even if the person does not believe it.",
        },
        action="Practice one honest conversation.",
    )

    assert truth_map["fact_layer"] == "Avoided conversation"
    assert truth_map["wisdom_anchor"] == "Practice one honest conversation."
    assert "Avoidance compounds" in truth_map["truth_claim"]["axiom"]

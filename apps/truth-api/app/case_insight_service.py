"""
CaseInsightService — minimal post-session blueprint updates with guarded inference.

This service intentionally stays conservative:
  - Only updates verified blueprint fields with lightweight heuristics.
  - Never fabricates soul age.
  - Returns "undetermined" unless the conversation history is both deep enough
    and signal-stable enough to justify an advisory classification.
"""
from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.case_models import CaseContext, CaseProfile
from app.case_resolver import save_case_profile

logger = logging.getLogger(__name__)

MIN_SOUL_AGE_ROUNDS = 4
MIN_STABLE_SIGNAL_MATCHES = 4

_THEME_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("boundaries and self-worth", ("界線", "boundary", "boundaries", "self-worth", "worth", "value")),
    ("career transition and purpose", ("事業", "career", "job", "work", "purpose", "calling", "轉型")),
    ("trust and allowing", ("allow", "allowing", "trust", "控制", "surrender", "放下")),
    ("authentic expression", ("表達", "speak", "voice", "authentic", "truth", "真實")),
    ("relationships and intimacy", ("關係", "relationship", "partner", "family", "親密")),
    ("emotional regulation", ("anxiety", "焦慮", "情緒", "nervous", "panic", "fear")),
)

_BLIND_SPOT_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("over-explaining to earn safety", ("explain", "解釋", "prove", "justify", "合理化")),
    ("people-pleasing over direct boundaries", ("please", "討好", "不敢拒絕", "can't say no", "迎合")),
    ("control before trust", ("control", "控制", "force", "push", "緊抓")),
    ("self-criticism over self-contact", ("critic", "批判", "self-blame", "責怪自己", "不夠好")),
    ("avoidance or delay under pressure", ("avoid", "逃避", "delay", "procrast", "拖延")),
    ("perfectionism blocking motion", ("perfect", "perfection", "完美", "不敢開始", "not ready")),
)

_SOUL_AGE_SIGNAL_PATTERNS: dict[str, tuple[str, ...]] = {
    "young": (
        "status",
        "win",
        "prove",
        "control",
        "beat",
        "competition",
        "成功",
        "輸贏",
        "掌控",
    ),
    "mature": (
        "responsibility",
        "repair",
        "relationship",
        "meaning",
        "service",
        "accountability",
        "修復",
        "責任",
        "意義",
        "關係",
    ),
    "old": (
        "presence",
        "acceptance",
        "inner truth",
        "compassion",
        "allowing",
        "alignment",
        "臣服",
        "接納",
        "慈悲",
        "允許",
        "真實",
    ),
}


def _normalize_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for key in ("content", "message", "text", "truth_view", "mirror", "action"):
            nested = value.get(key)
            if isinstance(nested, str) and nested.strip():
                return nested.strip()
        return " ".join(_normalize_text(v) for v in value.values() if v is not None).strip()
    if isinstance(value, list):
        return " ".join(_normalize_text(item) for item in value if item is not None).strip()
    return str(value).strip()


def _conversation_text(conversation_messages: object, model_response: object) -> str:
    return "\n".join(
        part for part in (_normalize_text(conversation_messages), _normalize_text(model_response)) if part
    ).strip()


def _find_patterns(text: str, patterns: tuple[tuple[str, tuple[str, ...]], ...]) -> list[str]:
    lowered = text.lower()
    matches: list[str] = []
    for label, keywords in patterns:
        if any(keyword.lower() in lowered for keyword in keywords):
            matches.append(label)
    return matches


def _dedupe_preserve_order(values: list[str], *, limit: int = 6) -> list[str]:
    out: list[str] = []
    for value in values:
        if value not in out:
            out.append(value)
        if len(out) >= limit:
            break
    return out


def _derive_last_session_insight(model_response: object, fallback_text: str) -> str | None:
    if isinstance(model_response, dict):
        for key in ("truth_view", "mirror", "action", "coach_question"):
            candidate = _normalize_text(model_response.get(key))
            if candidate:
                break
        else:
            candidate = ""
    else:
        candidate = _normalize_text(model_response)

    source = candidate or fallback_text
    if not source:
        return None

    sentence = re.split(r"(?<=[。！？.!?])\s+", source.strip(), maxsplit=1)[0].strip()
    sentence = sentence[:240].strip()
    return sentence or None


def _user_message_texts(conversation_history: object) -> list[str]:
    if not isinstance(conversation_history, list):
        return []
    out: list[str] = []
    for item in conversation_history:
        if isinstance(item, dict):
            role = str(item.get("role", "")).lower()
            if role and role != "user":
                continue
            text = _normalize_text(item.get("content") or item.get("text") or item.get("message"))
        else:
            text = _normalize_text(item)
        if text:
            out.append(text)
    return out


def infer_soul_age(case_profile: "CaseProfile", conversation_history: object) -> dict:
    """
    Advisory-only soul-age inference.

    This is intentionally conservative and explainable:
      - Requires enough conversation rounds.
      - Requires repeated, stable signal patterns across multiple user turns.
      - Returns eligible=False with a reason whenever confidence would be speculative.
    """
    user_messages = _user_message_texts(conversation_history)
    rounds = len(user_messages)
    if rounds < MIN_SOUL_AGE_ROUNDS:
        return {
            "eligible": False,
            "soul_age": None,
            "confidence": 0.0,
            "reasoning_signals": [],
            "why_not_eligible": (
                f"Need at least {MIN_SOUL_AGE_ROUNDS} user rounds; only {rounds} available."
            ),
            "experimental": True,
        }

    scores: dict[str, int] = {bucket: 0 for bucket in _SOUL_AGE_SIGNAL_PATTERNS}
    message_hits: dict[str, int] = {bucket: 0 for bucket in _SOUL_AGE_SIGNAL_PATTERNS}
    reasoning_signals: list[str] = []

    for idx, message in enumerate(user_messages, start=1):
        lowered = message.lower()
        for bucket, keywords in _SOUL_AGE_SIGNAL_PATTERNS.items():
            hits = [keyword for keyword in keywords if keyword.lower() in lowered]
            if not hits:
                continue
            scores[bucket] += len(hits)
            message_hits[bucket] += 1
            reasoning_signals.append(
                f"round {idx}: {bucket} signals -> {', '.join(sorted(set(hits))[:3])}"
            )

    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top_bucket, top_score = ordered[0]
    runner_up_score = ordered[1][1] if len(ordered) > 1 else 0
    top_message_hits = message_hits[top_bucket]

    if top_score < MIN_STABLE_SIGNAL_MATCHES or top_message_hits < 3 or (top_score - runner_up_score) < 2:
        return {
            "eligible": False,
            "soul_age": None,
            "confidence": 0.0,
            "reasoning_signals": reasoning_signals,
            "why_not_eligible": (
                "Signals were not stable enough across multiple rounds to support an advisory classification."
            ),
            "experimental": True,
        }

    confidence = min(0.88, 0.45 + (top_score * 0.05) + ((top_score - runner_up_score) * 0.03))
    return {
        "eligible": True,
        "soul_age": top_bucket,
        "confidence": round(confidence, 2),
        "reasoning_signals": reasoning_signals,
        "why_not_eligible": None,
        "experimental": True,
    }


def update_case_blueprint_from_conversation(
    case_profile: "CaseProfile",
    conversation_messages: object,
    model_response: object,
    metadata: dict | None = None,
) -> "CaseProfile":
    """
    Update only the minimal blueprint fields required for Phase 1.5:
      - last_session_insight
      - life_themes
      - blind_spots

    The function preserves all case identity fields and writes the updated
    profile back to the current case store.
    """
    conversation_text = _conversation_text(conversation_messages, model_response)
    life_themes = _find_patterns(conversation_text, _THEME_PATTERNS)
    blind_spots = _find_patterns(conversation_text, _BLIND_SPOT_PATTERNS)
    insight = _derive_last_session_insight(model_response, conversation_text)
    updated_fields: list[str] = []
    skip_reasons: list[str] = []

    if insight:
        updated_fields.append("last_session_insight")
    else:
        skip_reasons.append("missing_last_session_insight")
    if life_themes:
        updated_fields.append("life_themes")
    else:
        skip_reasons.append("no_life_theme_signal")
    if blind_spots:
        updated_fields.append("blind_spots")
    else:
        skip_reasons.append("no_blind_spot_signal")

    soul_age_guard = infer_soul_age(case_profile, conversation_messages)
    soul_age_guard_status = {
        "eligible": soul_age_guard.get("eligible"),
        "soul_age": soul_age_guard.get("soul_age"),
        "confidence": soul_age_guard.get("confidence"),
        "why_not_eligible": soul_age_guard.get("why_not_eligible"),
        "experimental": soul_age_guard.get("experimental", True),
    }

    updated = case_profile.model_copy(
        update={
            "last_session_insight": insight,
            "life_themes": _dedupe_preserve_order([*case_profile.life_themes, *life_themes]),
            "blind_spots": _dedupe_preserve_order([*case_profile.blind_spots, *blind_spots]),
        }
    )
    log_payload = {
        "event": "case_blueprint_writeback",
        "case_id": case_profile.case_id,
        "triggered": bool(updated_fields),
        "updated_fields": updated_fields,
        "life_themes": updated.life_themes,
        "blind_spots": updated.blind_spots,
        "skip_reason": ", ".join(skip_reasons) if skip_reasons else None,
        "soul_age_guard": soul_age_guard_status,
    }
    if metadata:
        log_payload["metadata"] = {
            "session_id": metadata.get("session_id"),
            "source_channel": metadata.get("source_channel"),
        }

    save_case_profile(updated)
    logger.info("case_blueprint_writeback: %s", log_payload)
    return updated


class CaseInsightService:
    """
    Stub service for post-session case insight extraction and life blueprint updates.

    All public methods are Phase 2 hooks. Call them from the post-session
    pipeline once real analysis capability is available.
    """

    # ------------------------------------------------------------------
    # Phase 2 hooks (stubs)
    # ------------------------------------------------------------------

    def update_case_blueprint_from_conversation(
        self,
        profile: "CaseProfile",
        conversation_messages: object,
        model_response: object,
        metadata: dict | None = None,
    ) -> "CaseProfile":
        return update_case_blueprint_from_conversation(
            profile,
            conversation_messages,
            model_response,
            metadata=metadata,
        )

    def extract_case_signals(
        self,
        conversation_text: object,
    ) -> dict:
        text = _normalize_text(conversation_text)
        return {
            "life_themes": _find_patterns(text, _THEME_PATTERNS),
            "blind_spots": _find_patterns(text, _BLIND_SPOT_PATTERNS),
            "insight_candidate": _derive_last_session_insight(text, text),
        }

    def infer_soul_age(
        self,
        profile: "CaseProfile",
        conversation_history: object,
    ) -> dict:
        return infer_soul_age(profile, conversation_history)

    def generate_life_themes_summary(self, profile: "CaseProfile") -> str | None:
        """
        [PHASE 2] Produce a natural-language summary of life themes for
        injection into the prompt. Returns None until implemented.
        """
        return None

    def generate_blind_spot_profile(self, profile: "CaseProfile") -> str | None:
        """
        [PHASE 2] Generate a Consciousness Blind Spot Profile (雁惟式分析).
        Returns None until implemented.
        """
        return None

    def sync_to_memory_store(
        self,
        profile: "CaseProfile",
        *,
        namespace: str,
    ) -> None:
        """
        [PHASE 2] Sync case insights (life_themes, blind_spots, last_session_insight)
        back into the mem0 / Qdrant namespace for retrieval-augmented responses.
        Currently a no-op.
        """
        logger.debug(
            "CaseInsightService.sync_to_memory_store skipped for namespace=%s (Phase 2 integration pending)",
            namespace,
        )

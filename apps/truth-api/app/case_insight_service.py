"""
CaseInsightService — minimal post-session blueprint updates with guarded inference.

This service intentionally stays conservative:
  - Only updates verified blueprint fields with lightweight heuristics.
  - Never fabricates soul age.
  - Returns "undetermined" unless the conversation history is both deep enough
    and signal-stable enough to justify an advisory classification.
"""
from __future__ import annotations

import collections
import logging
import re
from datetime import date as _date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.case_models import CaseContext, CaseProfile
from app.case_resolver import save_case_profile

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Feature flags — set to True only after validation in staging environment
# ---------------------------------------------------------------------------
SOUL_AGE_INFERENCE_ENABLED: bool = False  # Phase 2: enable conservative advisory label

# ---------------------------------------------------------------------------
# Trigger thresholds — must ALL pass before blueprint fields are updated
# ---------------------------------------------------------------------------
MIN_SOUL_AGE_ROUNDS = 4          # minimum user turns in this conversation
MIN_STABLE_SIGNAL_MATCHES = 4    # keyword hits required for soul_age advisory

# Blueprint update thresholds (Phase 2 guard)
_MIN_SESSIONS_FOR_THEME_WRITE = 3     # case must have at least N prior sessions
_MIN_CHARS_FOR_THEME_WRITE = 500      # combined conversation must be ≥ N chars
_MIN_THEME_DETECTIONS = 2             # need ≥ N theme signals before writing
_MAX_DAILY_BLUEPRINT_WRITES = 3       # idempotency guard: cap writes per day

# ---------------------------------------------------------------------------
# Observability helper
# ---------------------------------------------------------------------------

def _log_bp_event(event: str, **fields: object) -> None:
    """Emit one structured log line per blueprint update lifecycle event.

    All blueprint events share the token ``blueprint_event=`` so they can
    be isolated with:  grep 'blueprint_event=' <logfile>
    Per-event:         grep 'blueprint_event=blueprint_update_failed'
    Per-case:          grep 'case_id=<id>'
    """
    parts = " ".join(f"{k}={v!r}" for k, v in fields.items())
    logger.info("blueprint_event=%s %s", event, parts)


# ---------------------------------------------------------------------------
# Daily write cap — in-memory counter; resets on process restart (Phase 2 OK)
# ---------------------------------------------------------------------------

_DAILY_WRITE_COUNTER: collections.Counter = collections.Counter()


def _daily_cap_key(case_id: str) -> str:
    return f"{_date.today().isoformat()}:{case_id}"


def _check_and_inc_daily_cap(case_id: str) -> tuple[bool, str]:
    """Return (allowed, reason). Increments counter only when allowed."""
    key = _daily_cap_key(case_id)
    current = _DAILY_WRITE_COUNTER[key]
    if current >= _MAX_DAILY_BLUEPRINT_WRITES:
        return (
            False,
            f"daily_cap_reached:{current}/{_MAX_DAILY_BLUEPRINT_WRITES}",
        )
    _DAILY_WRITE_COUNTER[key] += 1
    return True, "ok"


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


def _should_update_blueprint(
    *,
    conversation_text: str,
    life_themes: list[str],
    blind_spots: list[str],
    session_count: int = 0,
    force: bool = False,
) -> tuple[bool, str]:
    """
    Phase 2 gate: returns (allowed, reason).

    All three thresholds must pass before we write blueprint fields.
    This prevents speculative updates from short or low-signal sessions.
    Pass force=True only in admin/backfill contexts.
    """
    if force:
        return True, "forced"

    char_count = len(conversation_text)

    if char_count < _MIN_CHARS_FOR_THEME_WRITE:
        return (
            False,
            f"conversation too short ({char_count} chars, need {_MIN_CHARS_FOR_THEME_WRITE})",
        )

    total_signals = len(life_themes) + len(blind_spots)
    if total_signals < _MIN_THEME_DETECTIONS:
        return (
            False,
            f"insufficient signal density ({total_signals} signals, need {_MIN_THEME_DETECTIONS})",
        )

    if session_count < _MIN_SESSIONS_FOR_THEME_WRITE:
        return (
            False,
            f"case too new ({session_count} sessions, need {_MIN_SESSIONS_FOR_THEME_WRITE})",
        )

    return True, "ok"


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
    *,
    force: bool = False,
) -> "CaseProfile":
    """
    Update minimal blueprint fields with Phase 2 threshold guards.

    Events emitted (grep for ``blueprint_event=``):
      - blueprint_update_attempted   : service entered; includes signal counts
      - blueprint_update_blocked     : daily cap or gate prevented all writes
      - blueprint_update_skipped     : no derivable content to write
      - blueprint_update_succeeded   : save_case_profile() completed
      - blueprint_update_failed      : save_case_profile() raised (then re-raises)

    Args:
        force: Bypass session-count and char-count gates. Admin/backfill only.
    """
    meta = metadata or {}
    session_count = int(meta.get("session_count", 0))
    request_id = str(meta.get("request_id", "") or "")
    source_channel = str(meta.get("source_channel", "unknown") or "unknown")
    session_id = str(meta.get("session_id", "") or "")
    case_id = case_profile.case_id

    conversation_text = _conversation_text(conversation_messages, model_response)
    char_count = len(conversation_text)
    life_themes_raw = _find_patterns(conversation_text, _THEME_PATTERNS)
    blind_spots_raw = _find_patterns(conversation_text, _BLIND_SPOT_PATTERNS)

    # Observability baseline — shared across all events for this call
    obs = dict(
        case_id=case_id,
        request_id=request_id,
        session_id=session_id,
        source_channel=source_channel,
        session_count=session_count,
        conversation_char_count=char_count,
        detected_theme_count=len(life_themes_raw) + len(blind_spots_raw),
        soul_age_enabled=SOUL_AGE_INFERENCE_ENABLED,
        force=force,
    )
    _log_bp_event("blueprint_update_attempted", **obs)

    # --- Daily cap (applies to all writes) ---
    cap_ok, cap_reason = _check_and_inc_daily_cap(case_id)
    if not cap_ok:
        _log_bp_event("blueprint_update_blocked", block_reason=cap_reason, **obs)
        return case_profile

    # --- Phase 2 gate (controls list fields; insight is always attempted) ---
    gate_ok, gate_reason = _should_update_blueprint(
        conversation_text=conversation_text,
        life_themes=life_themes_raw,
        blind_spots=blind_spots_raw,
        session_count=session_count,
        force=force,
    )
    if not gate_ok:
        _log_bp_event(
            "blueprint_update_blocked",
            block_reason=f"gate:{gate_reason}",
            fields_blocked="life_themes,blind_spots,soul_age",
            **obs,
        )

    # --- Build update_kwargs ---
    insight = _derive_last_session_insight(model_response, conversation_text)
    update_kwargs: dict = {}
    updated_fields: list[str] = []
    skip_reasons: list[str] = []

    if insight:
        update_kwargs["last_session_insight"] = insight
        updated_fields.append("last_session_insight")
    else:
        skip_reasons.append("no_insight")

    if gate_ok:
        merged_themes = _dedupe_preserve_order([*case_profile.life_themes, *life_themes_raw])
        merged_spots = _dedupe_preserve_order([*case_profile.blind_spots, *blind_spots_raw])
        update_kwargs["life_themes"] = merged_themes
        update_kwargs["blind_spots"] = merged_spots
        if life_themes_raw:
            updated_fields.append("life_themes")
        else:
            skip_reasons.append("no_theme_signal")
        if blind_spots_raw:
            updated_fields.append("blind_spots")
        else:
            skip_reasons.append("no_blind_spot_signal")

        # Soul-age advisory — flag-gated, gate-gated
        soul_age_result = infer_soul_age(case_profile, conversation_messages)
        if SOUL_AGE_INFERENCE_ENABLED and soul_age_result.get("eligible"):
            sa = soul_age_result.get("soul_age")
            if sa:
                update_kwargs["soul_age"] = sa
                updated_fields.append("soul_age")
        elif not SOUL_AGE_INFERENCE_ENABLED:
            skip_reasons.append("soul_age_flag_off")
    else:
        skip_reasons.append(f"gate_blocked:{gate_reason}")

    if not update_kwargs:
        _log_bp_event(
            "blueprint_update_skipped",
            skip_reason=",".join(skip_reasons),
            **obs,
        )
        return case_profile

    # --- Persist ---
    updated = case_profile.model_copy(update=update_kwargs)
    try:
        save_case_profile(updated)
    except Exception as exc:
        _log_bp_event(
            "blueprint_update_failed",
            error_type=type(exc).__name__,
            error=str(exc)[:200],
            updated_fields=updated_fields,
            **obs,
        )
        raise

    _log_bp_event(
        "blueprint_update_succeeded",
        updated_fields=updated_fields,
        skip_reasons=skip_reasons or None,
        **obs,
    )
    return updated



class CaseInsightService:
    """
    Phase 2 case insight extraction and life blueprint update service.

    All methods use conservative, pattern-based heuristics that are
    observable and testable without an LLM dependency. LLM-structured
    extraction is planned for Phase 3 (see docstrings on each method).
    """

    # ------------------------------------------------------------------
    # Core blueprint update (delegates to module-level function)
    # ------------------------------------------------------------------

    def update_case_blueprint_from_conversation(
        self,
        profile: "CaseProfile",
        conversation_messages: object,
        model_response: object,
        metadata: dict | None = None,
        *,
        force: bool = False,
    ) -> "CaseProfile":
        """
        Post-session blueprint update.  Applies Phase 2 threshold guards
        (session_count, char_count, signal density) before writing.

        Args:
            force: Bypass session/char thresholds — admin and backfill only.
        """
        return update_case_blueprint_from_conversation(
            profile,
            conversation_messages,
            model_response,
            metadata=metadata,
            force=force,
        )

    # ------------------------------------------------------------------
    # Signal extraction
    # ------------------------------------------------------------------

    def extract_case_signals(
        self,
        conversation_text: object,
    ) -> dict:
        """
        Extract life-theme and blind-spot signals from conversation text
        using keyword pattern matching.

        Returns a dict with:
          - life_themes: matched theme labels
          - blind_spots: matched blind-spot labels
          - insight_candidate: first-sentence candidate for last_session_insight

        Phase 3 upgrade: replace pattern matching with a structured LLM
        extraction call (e.g., function-calling with JSON schema) so the
        AI can surface latent signals not captured by keyword lists.
        """
        text = _normalize_text(conversation_text)
        return {
            "life_themes": _find_patterns(text, _THEME_PATTERNS),
            "blind_spots": _find_patterns(text, _BLIND_SPOT_PATTERNS),
            "insight_candidate": _derive_last_session_insight(text, text),
        }

    # ------------------------------------------------------------------
    # Soul-age advisory
    # ------------------------------------------------------------------

    def infer_soul_age(
        self,
        profile: "CaseProfile",
        conversation_history: object,
    ) -> dict:
        """
        Conservative soul-age advisory.

        Returns eligible=False whenever conversation history is too short,
        signal count is too low, or the feature flag is off.

        The returned dict always contains:
          eligible, soul_age, confidence, reasoning_signals, why_not_eligible, experimental
        """
        if not SOUL_AGE_INFERENCE_ENABLED:
            return {
                "eligible": False,
                "soul_age": None,
                "confidence": 0.0,
                "reasoning_signals": [],
                "why_not_eligible": "SOUL_AGE_INFERENCE_ENABLED=False — feature flag is off",
                "experimental": True,
            }
        return infer_soul_age(profile, conversation_history)

    # ------------------------------------------------------------------
    # Summary generators (Phase 2 — pattern-based)
    # ------------------------------------------------------------------

    def generate_life_themes_summary(self, profile: "CaseProfile") -> str | None:
        """
        Return a short natural-language summary of the case's detected life themes,
        suitable for injection into the prompt context block.

        Returns None if the profile has no themes yet.

        Phase 3 upgrade: feed themes + session excerpts to LLM for a
        richer, personalized paragraph rather than a template fill.
        """
        if not profile.life_themes:
            return None
        theme_lines = "、".join(profile.life_themes[:4])
        return f"主要生命課題：{theme_lines}。"

    def generate_blind_spot_profile(self, profile: "CaseProfile") -> str | None:
        """
        Return a short natural-language Consciousness Blind Spot Profile
        (意識盲點剖析) for prompt injection.

        Returns None if no blind spots have been detected.

        Phase 3 upgrade: combine with LLM reflection to produce the
        full Andromedian-style Blind Spot Profile narrative.
        """
        if not profile.blind_spots:
            return None
        spot_lines = "；".join(profile.blind_spots[:3])
        return f"常見意識盲點：{spot_lines}。請在引導中留意，不要直接點破，而是用提問方式邀請覺察。"

    # ------------------------------------------------------------------
    # Memory store sync (Phase 2 stub — integration pending)
    # ------------------------------------------------------------------

    def sync_to_memory_store(
        self,
        profile: "CaseProfile",
        *,
        namespace: str,
    ) -> None:
        """
        Sync case insights (life_themes, blind_spots, last_session_insight)
        back into a mem0 / Qdrant namespace for retrieval-augmented responses.

        Phase 2 status: no-op — logs the sync intent for observability.

        Phase 3 upgrade: call the mem0 REST API to upsert a document keyed
        by (namespace, case_id) containing the serialized insights. Add a
        dry_run=True flag for testing the upsert path without persistence.
        """
        logger.info(
            "CaseInsightService.sync_to_memory_store intent: namespace=%s case_id=%s "
            "life_themes=%s blind_spots=%s last_insight=%s (Phase 3 integration pending)",
            namespace,
            profile.case_id,
            profile.life_themes,
            profile.blind_spots,
            bool(profile.last_session_insight),
        )

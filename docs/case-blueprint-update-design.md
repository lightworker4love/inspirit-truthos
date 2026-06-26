# Case Blueprint Update Design
## `update_case_blueprint_from_conversation()`

**Status**: Phase 2 draft — pattern-based implementation live, LLM extraction planned for Phase 3  
**Owner**: TruthOS backend  
**Updated**: 2026-05

---

## 1. Purpose

After every significant AI conversation session, the system should incrementally refine
the user's **life blueprint** — the structured record of what we know about their soul
journey. `update_case_blueprint_from_conversation()` is the single entry point for this
post-session update.

Goals:
- Keep the CaseProfile accurate without human intervention.
- Never fabricate. Only update fields with sufficient signal evidence.
- Protect against speculative writes during short or noisy sessions.

---

## 2. Extraction Targets

| Field | Source | Notes |
|---|---|---|
| `last_session_insight` | Last AI response first sentence | Always extracted if non-empty |
| `life_themes` | Keyword pattern match in full conversation | Appended (deduped) to existing themes |
| `blind_spots` | Keyword pattern match | Appended (deduped) to existing blind spots |
| `soul_age` | Multi-round signal accumulation | Only when `SOUL_AGE_INFERENCE_ENABLED=True` |

Fields that are **never auto-written**:
- `preferred_name` / `display_name` / `login_username` — identity fields require human confirmation.
- `aliases` — managed by admin.
- `memory_namespace` — set at case creation.

---

## 3. Phase 2 Trigger Gate (`_should_update_blueprint`)

Before writing `life_themes` or `blind_spots`, all three thresholds must pass:

| Threshold | Current value | Rationale |
|---|---|---|
| `_MIN_CHARS_FOR_THEME_WRITE` | 500 chars | Reject trivial greetings and single-exchange sessions |
| `_MIN_THEME_DETECTIONS` | 2 signals | At least two signals (themes + blind spots combined) needed |
| `_MIN_SESSIONS_FOR_THEME_WRITE` | 3 sessions | Trust only established patterns, not first impressions |

`last_session_insight` always writes if derivable — it is the lowest-risk field.

`force=True` bypasses session-count and char-count checks (admin backfill only).

---

## 4. Auto vs. Human-Confirm Fields

```
Auto-write (this function):          Human-confirm (admin panel only):
  - last_session_insight               - preferred_name
  - life_themes (append)               - soul_age label (if advisory confidence < 0.7)
  - blind_spots (append)               - case_name alias changes
  - soul_age (when flag on + eligible) - memory_namespace changes
```

### Merge strategy for list fields

New detections are appended to the tail of the existing list, then deduped with
`_dedupe_preserve_order(limit=6)`. The **first-detected item stays first** (oldest
observation has positional seniority). Items are never automatically removed.

If the same theme appears in 5 consecutive sessions, it still only appears once in
the list — repetition proves importance but does not change the list.

---

## 5. Soul-Age Advisory Path

Soul-age inference is deliberately **advisory-only** and guarded behind a feature flag:

```
SOUL_AGE_INFERENCE_ENABLED = False    ← default; flip in staging first
```

When the flag is True, `infer_soul_age()` applies these additional checks:

1. Minimum `MIN_SOUL_AGE_ROUNDS = 4` user turns in the conversation.
2. Top bucket must have ≥ `MIN_STABLE_SIGNAL_MATCHES = 4` keyword hits.
3. Top bucket must lead the runner-up by ≥ 2 hits (avoid ambiguous signals).
4. Confidence is capped at 0.88 — never returns 1.0.

Even when eligible, the advisory is logged and stored but the counselor is
expected to review before presenting it to the user.

**Planned upgrade**: Replace keyword accumulation with a multi-turn LLM assessment
that evaluates narrative arc, not just keyword frequency.

---

## 6. Failure Protection

| Scenario | Behaviour |
|---|---|
| `save_case_profile` raises | Exception propagates; no partial write (Pydantic model_copy is atomic in-memory) |
| Pattern match finds nothing | Function still writes `last_session_insight` if available; skips list fields |
| Gate blocked (threshold miss) | Returns the original profile unmodified; logs `gate_blocked` reason |
| `model_response` is None/empty | `last_session_insight` skipped gracefully; patterns run against conversation only |

---

## 7. mem0 / Qdrant Sync (`sync_to_memory_store`)

Currently a no-op (Phase 2 log-only stub). Planned Phase 3 contract:

```python
CaseInsightService().sync_to_memory_store(
    profile,
    namespace=profile.memory_namespace,
)
```

The method will upsert a document into the mem0 / Qdrant store keyed by
`(namespace, case_id)` containing:
- `life_themes` (list)
- `blind_spots` (list)
- `last_session_insight` (string)
- `soul_age` advisory (if present)

This enables retrieval-augmented responses: when a new session starts, the case
context is fetched from the vector store and injected into the system prompt.

---

## 8. Integration Points

```
POST /api/truth/query
  └─ CaseResolver.resolve()                    # get CaseContext
  └─ (AI model call)
  └─ update_case_blueprint_from_conversation() # post-session, best-effort
       ├─ _should_update_blueprint()           # gate check
       ├─ _find_patterns()                     # theme + blind_spot extraction
       ├─ _derive_last_session_insight()       # insight extraction
       ├─ infer_soul_age()                     # advisory (flag-gated)
       └─ save_case_profile()                  # JSON persistence
```

---

## 9. Recommended Next Steps (Phase 3)

1. **LLM extraction**: Replace `_find_patterns()` with a function-calling / structured output call that returns `{life_themes: [], blind_spots: [], insight: ""}` — eliminates keyword list maintenance.
2. **Session counter**: Track `session_count` in `wisdom-cases.db` (increment per gateway session close event) so the `_MIN_SESSIONS_FOR_THEME_WRITE` gate uses real data.
3. **Retroactive backfill**: Add a CLI script `backfill_blueprints.py` that replays stored conversation logs through the extraction pipeline with `force=True`.
4. **Human review queue**: Surface unconfirmed soul_age advisories in the admin panel with approve/reject actions.
5. **Dry-run mode**: Add `dry_run=True` flag — returns the would-be updated profile without persisting, useful for preview UI.

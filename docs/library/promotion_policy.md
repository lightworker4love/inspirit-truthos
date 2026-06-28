# Canonical Promotion Policy

## Purpose
Rules for moving a draft/hypothesis insight (e.g., a proposed blueprint update or new core principle) into the canonical TruthOS memory store (LanceDB/SQLite + `MEMORY.md`).

## Scope
Applies to all automated insights, case reflections, and agent-generated wisdom entries.

## Promotion Criteria
1. **Structural Validity:** Must validate perfectly against `promotion_record.schema.json`.
2. **No Anti-Patterns:** Must explicitly pass an anti-pattern resonance check.
3. **Human-in-the-Loop (HITL):** Currently, all blueprint updates require explicit Operator (human) approval. [VERIFY: Future threshold for auto-promotion if available].
4. **Audit Trail:** Every promotion must write an event matching `audit_event.schema.json`.

## Audit Notes
- Promotions must log the original `prompt_id` or `agent_session_id` that generated the insight.

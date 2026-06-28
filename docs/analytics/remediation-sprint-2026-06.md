# TruthOS Remediation Sprint 2026-06

## Sprint 1

- Added additive-only guardrail metadata for Hermes truth-layer degradation via `_truth_degraded`.
- Added classifier metadata without changing ranking logic:
  `confidence`, `low_confidence`, `low_confidence_reason`.
- Added retrieval metadata without changing retrieval selection logic:
  `top_similarity`, `is_fallback`, `fallback_reason`.
- Added per-step warning logging and internal partial-failure metadata on `truth_query`.
- Kept user-facing copy and primary control flow unchanged; all new fields are internal or underscore-prefixed.

## Sprint 3

- Pending. Current repository does not expose Alembic wiring yet; migration path needs to be reconciled with the existing SQL migration setup before execution.

## Sprint 2

- Pending until after Sprint 3 per requested order.

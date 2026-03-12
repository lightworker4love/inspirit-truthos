# Phase 2 Technical Roadmap

## Direction

Phase 2 should turn the current safe scaffolding into a robust case-memory pipeline without sacrificing explainability, rollback safety, or identity consistency.

## Workstreams

### 1. preferred_name hardening

- persist source-of-truth provenance for each naming signal
- add explicit conflict logging when request/store/admin names disagree
- add admin review tools for identity merge and alias management

### 2. blueprint automation

- replace keyword heuristics with structured extraction prompts or classifiers
- separate per-session observations from durable blueprint facts
- add review thresholds before durable writeback

### 3. guarded soul-age inference

- keep inference opt-in and advisory
- keep public UX non-prominent; expose only in internal/debug/admin surfaces when enabled
- add richer signal provenance and multi-session evidence windows
- expose eligibility diagnostics before any candidate label

### 4. multi-account linking

- support one person across multiple channels/accounts
- keep canonical `case_id` stable while storing linked identities
- require explicit merge workflows with audit trails

### 5. mem0 / Qdrant sync

- sync only validated blueprint summaries, not raw speculative fields
- preserve `memory_namespace` stability during sync
- add reconciliation checks between JSON/DB state and vector memory state

### 6. store migration

- Phase 2a: JSON + SQLite dual-write
- Phase 2b: Postgres primary store with migration tooling
- Phase 2c: retire JSON as primary write path, keep export/import support

### 7. observability and rollback

- emit metrics for identity resolution source, blueprint writes, and inference eligibility
- add structured logs for writeback decisions and skip reasons
- add feature flags for blueprint updater and soul-age inference
- keep rollback paths for UI metadata propagation and backend writeback independently

## Milestones

### Milestone A

- stable preferred-name propagation in production
- conflict logging
- admin visibility for name provenance

### Milestone B

- reviewed blueprint extraction pipeline
- dual-write case store
- mem0/Qdrant summary sync

### Milestone C

- guarded multi-session soul-age eligibility engine
- observability dashboards
- rollback-ready feature flags

### Milestone D

- account linking
- Postgres-backed case profile service
- migration tooling and backfill jobs

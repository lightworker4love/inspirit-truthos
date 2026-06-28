# TruthOS Schema

## `core_principles`

Sprint 004 adds these truth-property columns:

- `worldly_example TEXT`: material-domain example of the axiom.
- `spiritual_example TEXT`: spiritual-domain expression of the same axiom.
- `objectivity_statement TEXT`: sentence confirming the axiom operates independent of awareness or belief.
- `truth_property_primary TEXT`: dominant property, one of `consistency`, `plurality`, `objectivity`, `discoverability`, `verifiability`.

## `truth_puzzles`

Sprint 004 adds these puzzle verification columns:

- `truth_property_tags TEXT`: JSON array of Truth property tags.
- `verification_mode TEXT DEFAULT 'dialogue'`: one of `stillness`, `dialogue`, `evidence`.
- `fact_layer TEXT`: observable event or symptom described by the user.
- `reality_layer TEXT`: deeper life pattern beneath the observable fact.

## `truth_evals`

Sprint 004 introduces `truth_evals` for query verification audit records:

- `id TEXT PRIMARY KEY`
- `user_id TEXT NOT NULL`
- `session_id TEXT`
- `question TEXT`
- `verification_track TEXT`: selected track, one of `stillness`, `dialogue`, `evidence`.
- `life_evidence_confirmed INTEGER DEFAULT 0`
- `discovery_triggered INTEGER DEFAULT 0`
- `created_at TEXT NOT NULL`

## `soulmaps`

Sprint 006 adds Soul Map depth tracking. If the table does not exist yet,
migration 005 creates it before adding the depth columns.

- `patternweightsjson TEXT`: JSON object keyed by pattern id with frequency, last-seen timestamp, and decay-weighted significance.
- `integrateddimensionsjson TEXT`: JSON array of dimensions where the user shows consistent truth-alignment.
- `transcendedpatternsjson TEXT`: JSON array of resolved historical patterns retained for longitudinal context.
- `evolutionhistoryjson TEXT`: JSON array of stage transitions and their trigger patterns.
- `soulmapsummary TEXT`: 3-5 sentence synthesis used as query context.

## `blindspotarchives`

Sprint 006 adds blind-spot depth tracking:

- `severity TEXT DEFAULT 'medium'`: one of `low`, `medium`, `high`, `critical`.
- `domainsjson TEXT`: JSON array of life domains where the blind spot appears.
- `resolutionstatus TEXT DEFAULT 'active'`: one of `active`, `softening`, `integrated`, `transcended`.
- `resolutionat TEXT`: timestamp for the first non-active resolution state.

## `hardcasebuffer`

Sprint 006 introduces `hardcasebuffer` for Coach Review escalation. Sprint 007
adds Designer Agent resolution state:

- `userid TEXT PRIMARY KEY`
- `reasons TEXT NOT NULL`: JSON array of hard-case reasons.
- `sessionid TEXT`
- `createdat TEXT NOT NULL`
- `status TEXT DEFAULT 'pending'`: one of `pending`, `resolved`, `coach_review`.
- `summaryjson TEXT`: JSON block containing Designer Agent diagnosis and AB evaluation.
- `resolvedat TEXT`: timestamp when the system resolved the hard case without human escalation.
- `resolutionnote TEXT`: human-readable resolution or escalation reason.

## `promptversions`

Sprint 007 adds prompt-variant storage for hard-case experiments:

- `id TEXT PRIMARY KEY`
- `hardcaseid TEXT NOT NULL`
- `prompttemplate TEXT NOT NULL`
- `promptlabel TEXT NOT NULL`
- `prompttype TEXT NOT NULL`
- `version INTEGER NOT NULL`
- `parentversionid TEXT`
- `createdat TEXT NOT NULL`

## `promptabtests`

Sprint 007 adds deterministic AB-test audit records:

- `id TEXT PRIMARY KEY`
- `hardcaseid TEXT NOT NULL`
- `promptaid TEXT NOT NULL`
- `promptbid TEXT NOT NULL`
- `status TEXT NOT NULL`: `completed` or `inconclusive`.
- `winnerid TEXT`
- `evaluationjson TEXT`: weighted rubric scores and recommendation.
- `startdat TEXT NOT NULL`
- `completedat TEXT`

## `designerreviews`

Sprint 007 records the Designer Agent's diagnosis and action:

- `id TEXT PRIMARY KEY`
- `hardcaseid TEXT NOT NULL`
- `reviewedby TEXT NOT NULL`
- `findingsjson TEXT NOT NULL`
- `newprincipleproposed INTEGER DEFAULT 0`
- `promptwinner TEXT`
- `action TEXT NOT NULL`
- `createdat TEXT NOT NULL`

## `knowledgeevolutions`

Sprint 007 records knowledge-layer changes created from hard-case review:

- `id TEXT PRIMARY KEY`
- `sourcetype TEXT NOT NULL`
- `sourceid TEXT NOT NULL`
- `changetype TEXT NOT NULL`
- `targetid TEXT`
- `rationaljson TEXT`
- `createdat TEXT NOT NULL`

## API Additions

`POST /api/truth/query` keeps existing response fields and adds:

- `verification_track`
- `verification_context`
- `truth_eval_id`
- `truth_map.fact_layer`
- `truth_map.reality_layer`
- `truth_map.truth_claim`
- `truth_map.wisdom_anchor`
- `writeback.soul_map_changes`
- `hard_case_flag` and `coach_review_recommended` when hard-case detection triggers
- `designer_review` and `knowledge_evolution_written` when a hard case is automatically resolved by Sprint 007 Designer Agent

Sprint 006 also adds:

- `GET /api/soul-map/{user_id}`
- `GET /api/soul-map/{user_id}/blind-spots`

Sprint 007 also adds:

- `POST /api/designer/hard-cases/{hardcase_id}/review`
- `POST /api/designer/hard-cases/review-pending`

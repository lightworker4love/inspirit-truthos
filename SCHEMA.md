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

## API Additions

`POST /api/truth/query` keeps existing response fields and adds:

- `verification_track`
- `verification_context`
- `truth_eval_id`
- `truth_map.fact_layer`
- `truth_map.reality_layer`
- `truth_map.truth_claim`
- `truth_map.wisdom_anchor`

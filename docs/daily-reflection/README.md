# TruthOS Daily Reflection Pipeline Spec

## Purpose

This document defines the production-oriented engineering spec for the TruthOS Daily Reflection Pipeline.

The pipeline is not a generic daily summary.
It is the daily evolution node of TruthOS and must produce:

- a human-readable daily reflection report
- machine-readable structured output for writeback and governance
- appendable dashboard data
- import drafts for future principle and puzzle governance

## Product Position

TruthOS Daily Reflection Pipeline must remain aligned with the platform identity:

- in spirit AI is a Human Consciousness Operating System
- the goal is to restore inner discernment, not create dependence
- inference must never be disguised as truth
- high-level interpretations must stay labeled as possible, tendency, or working hypothesis
- when context is incomplete, the system must name the gap instead of filling it with style
- memory is continuity of care, not surveillance

## Required Inputs

The pipeline may use only these sources unless the run context explicitly grants more:

- current session context
- retrievable user memory
- attached files and accessible local documents
- TruthOS seeds and structured datasets already present in the repo
- explicitly provided external context for the run

Default rule:

- do not browse the web
- do not assume hidden context
- do not fabricate life principles content when the attachment is missing

## Pipeline Stages

### 1. Context Collection

Collect the last 24 hours of available context in `Asia/Taipei`.

If the last 24 hours are too sparse to support a stable reflection:

- widen to the last 72 hours
- mark that expansion explicitly in the report and JSON

### 2. Discernment Layer

Before any interpretation, split the material into four layers:

- `fact`
- `interpretation`
- `inference`
- `guidance`

Rules:

- inference cannot be promoted into fact
- guidance cannot be framed as truth
- any claim about soul lesson, life blueprint, causality, karmic pattern, or higher-order personality structure must be marked as `working_hypothesis`

### 3. Truth Mapping

Map the run into the canonical TruthOS 12 dimensions only:

- `motive`
- `cognition`
- `emotion`
- `relationship`
- `belief`
- `evolution`
- `causality`
- `manifestation`
- `suffering`
- `freedom`
- `compassion`
- `discernment`

Per run:

- choose 1 to 3 primary dimensions
- choose 2 to 4 core principle candidates
- choose 2 to 4 truth puzzle candidates
- every candidate must carry a confidence score

### 4. Report Composition

Generate one markdown report with the fixed eight sections:

1. `昨日整體脈絡`
2. `重要事件與內在波動`
3. `可能涉及的 TruthOS 維度（12 維度中的 1-3 個）`
4. `可能對應的核心心法（2-4 條）`
5. `真理拼圖觀察（2-4 片）`
6. `今日可執行的提醒 / 行動 / 提問`
7. `資料限制與不確定性聲明`
8. `是否建議回寫：soul_map / blind_spot / belief_log / case_summary`

### 5. Structured JSON Emission

Emit a machine-readable JSON document that:

- preserves time window and timezone
- preserves discernment layers
- preserves confidence and uncertainty
- carries writeback candidates without directly mutating canonical truth

### 6. Writeback Gate

Writeback must respect scope boundaries:

- `session-level`: raw run report, run JSON, uncertainty notes, source context state
- `user-level`: promoted Soul Map, Blind Spot, Belief Log, Case Summary candidates after threshold checks
- `agent-level`: operational diagnostics, run metadata, prompt version, fallback path, traceability fields

Hard boundary:

- session observations do not automatically become user truths
- agent diagnostics must never be mixed into user memory objects

### 7. Dashboard Projection

Append one dashboard snapshot per run.

The dashboard layer must support:

- daily timeline
- dimension trend over 7 / 30 / 90 days
- recurring pattern tracker
- belief shift tracker
- blind spot heatmap
- alignment trend

### 8. Truth Import Draft Generation

Generate principle and puzzle drafts only when governance gates are met.

A single day may suggest a draft, but it may not elevate that draft into immutable truth.

## Cross-Day Evolution Rules

- single-day signals remain observations only
- a signal must appear 3 or more times before becoming a `recurring pattern candidate`
- a limiting belief needs before/after evidence or multiple supporting events before becoming a `belief_log candidate`
- a blind spot candidate must satisfy `knows the theory but fails in practice`
- a principle or puzzle draft must include `source_refs` or `source_doc`

## Missing Attachment Rule

If no life principles attachment, seed note, or readable TruthOS source is provided for the run, the output must include this exact statement:

`目前未提供生命心法附件或可讀連結，因此本次僅能根據現有對話與記憶脈絡整理，不能補想、不能虛構、不能假設其內容。`

## Recommended Artifact Paths

Use append-only or date-partitioned paths under the repo `data/` directory:

- `data/daily_reflections/YYYY-MM-DD/report.md`
- `data/daily_reflections/YYYY-MM-DD/reflection.json`
- `data/dashboard/reflection_snapshots.jsonl`
- `data/dashboard/daily_metrics.jsonl`
- `data/dashboard/pattern_snapshots.jsonl`
- `data/writebacks/soul_map_candidates.jsonl`
- `data/writebacks/blind_spot_archive_candidates.jsonl`
- `data/writebacks/belief_log_candidates.jsonl`
- `data/writebacks/case_summary_candidates.jsonl`
- `data/import_drafts/core_principle_candidates.jsonl`
- `data/import_drafts/truth_puzzle_candidates.jsonl`

## OpenClaw Cron Job Shape

Recommended OpenClaw scheduler settings:

- name: `每日靈性觀察`
- timezone: `Asia/Taipei`
- cron: `0 9 * * *`
- session target: `isolated`
- delivery: `none`
- status: `enabled`

Reasoning:

- isolated execution avoids polluting the main conversation
- 09:00 local time supports a clean previous-day window
- no-delivery avoids accidental noisy channel announcements while the pipeline is still staging writebacks into governed files

## Runtime Assets

The cron job should read these local files each run:

- `docs/daily-reflection/automation-prompt.md`
- `docs/daily-reflection/daily-reflection-report.template.md`
- `docs/daily-reflection/schemas/daily-reflection-run.schema.json`
- `docs/daily-reflection/schemas/dashboard-reflection-snapshot.schema.json`
- `docs/daily-reflection/schemas/truthos-import-drafts.schema.json`

## Current Implementation Gaps

This spec intentionally stages writebacks into append-only files first.

What is already aligned:

- TruthOS dimensions, principles, puzzles, belief logs, and blind spot archives exist as governed concepts
- OpenClaw cron exists as a runnable scheduler
- local-first paths and degraded-mode thinking already exist

What still needs application-layer implementation if you want full DB-native writeback:

- dedicated writeback endpoints for Soul Map / Blind Spot / Belief Log / Case Summary
- deduplication service for JSONL to SQLite projection
- dashboard materialization jobs
- review workflow for promoting import drafts into canonical seeds

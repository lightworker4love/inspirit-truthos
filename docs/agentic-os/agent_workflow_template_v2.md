# Agent Workflow Template v2

## Purpose
Defines the state-machine and standard operating procedure for the TruthOS agent when processing a user query or life case.

## Scope
Operates strictly between request ingestion and final response composition. Integrates with the `retriever.py` and `reasoning.py` pipelines [VERIFY: exact hook points].

## Required Sections
1. **Ingestion & Classification:** Determine truth dimension.
2. **Retrieval (Read-Only):** Fetch relevant Truth Puzzles and Core Principles via LanceDB -> SQLite fallback.
3. **Drafting (Hypothesis):** Generate initial `mirror`, `truth_view`, `coach_question`, `action`.
4. **Resonance Check:** Does this violate any known `anti_patterns.md`?
5. **Proposal (Staging):** If this updates the user's Soul Blueprint, generate a `blueprint_instance` hypothesis. Do NOT write to DB.
6. **Output:** Return reasoning payload.

## Review Rules
- The agent MUST NOT bypass the drafting phase. 
- Auto-promotion to canonical requires an explicit human override or future verified policy update.

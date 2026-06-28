# README_PROMPTS.md

This directory includes three Codex prompt presets for `inspirit-truthos`.

## Files

- `CODEX_PROMPT_ULTRA_SHORT.md`
- `CODEX_PROMPT_SHORT.md`
- `CODEX_PROMPT_FULL.md`

## Which one to use

### `CODEX_PROMPT_ULTRA_SHORT.md`

Use this when:

- you need the fastest possible start
- the task is small and localized
- you already know the agent has little context budget

Good fit:

- one-file fixes
- tiny prompt windows
- quick sanity edits

Tradeoff:

- minimal context
- weakest architecture reminder

### `CODEX_PROMPT_SHORT.md`

Use this when:

- you want a practical default
- the task touches runtime behavior or API behavior
- you want the key architectural and fallback rules without a long preamble

Good fit:

- normal feature work
- bug fixes
- endpoint changes
- retrieval / fallback related changes

Tradeoff:

- balanced context size
- enough constraints for most tasks

### `CODEX_PROMPT_FULL.md`

Use this when:

- the task is architectural
- the task may affect fallback logic, data model, API contracts, seed baseline, or system boundaries
- you want the strongest alignment with TruthOS design intent

Good fit:

- multi-file changes
- refactors
- runtime mode changes
- retrieval pipeline changes
- health / observability changes

Tradeoff:

- largest prompt size
- strongest constraint coverage

## Recommended default

If unsure, start with:

- `CODEX_PROMPT_SHORT.md`

Escalate to:

- `CODEX_PROMPT_FULL.md` for architectural or higher-risk work

Downgrade to:

- `CODEX_PROMPT_ULTRA_SHORT.md` for tiny edits or very small context windows

## Suggested opener

You can prepend one of the prompt files with:

```text
Use the repository rules in this prompt as binding constraints for all code and design decisions in this task.
```

For seed or environment work, append:

```text
Also read SEED_AUTHORING_GUIDE.md and use the seeds/ and env/ templates as the canonical seed-authoring and environment configuration baseline.
```

## Repository context

These prompt files are designed to work with:

- `AGENTS.md`
- `PROJECT_RULES.md`
- `ARCHITECTURE.md`
- `OPERATIONS.md`
- `ENVIRONMENT.md`
- `DATA_MODEL.md`
- `API_CONTRACTS.md`
- `SEED_AUTHORING_GUIDE.md`

Together they define:

- agent behavior constraints
- human engineering rules
- system architecture intent
- runtime recovery expectations
- environment and configuration boundaries
- truth data and seed governance boundaries
- API shape and degraded-mode contract boundaries
- canonical seed-authoring and baseline template boundaries

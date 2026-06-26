# CONTENTS.md

# inspirit-truthos Manifest

This file is a quick index of the governance docs, prompt helpers, and utility scripts in the repository root.

Use it as the human-friendly companion to `ls`.

The repository homepage Quick Start already uses the canonical `.env.example`, `env/`, and `seeds/` baseline.

---

## Core Entry

- `README.md`
  - formal repository homepage
  - start here if you are opening the repo for the first time

- `CONTENTS.md`
  - quick manifest of root-level governance docs and prompt tools

---

## Repository Constitution

- `AGENTS.md`
  - rules for Codex, agents, and automated modifiers

- `PROJECT_RULES.md`
  - rules for human engineers and maintainers

- `ARCHITECTURE.md`
  - formal TruthOS system blueprint

- `OPERATIONS.md`
  - runbook for health checks, recovery, fallback, and troubleshooting

- `ENVIRONMENT.md`
  - formal environment and configuration contract

- `DATA_MODEL.md`
  - canonical truth schema and seed data authority

- `API_CONTRACTS.md`
  - canonical endpoint contracts and degraded-mode response authority

- `SEED_AUTHORING_GUIDE.md`
  - canonical guide for authoring, reviewing, and expanding seed data

- `README_CONSTITUTION.md`
  - one-page overview of how the core documents relate

Recommended reading order:

- Human engineer: `PROJECT_RULES.md` -> `ARCHITECTURE.md` -> `OPERATIONS.md` -> `ENVIRONMENT.md` -> `DATA_MODEL.md` -> `API_CONTRACTS.md` -> `SEED_AUTHORING_GUIDE.md` -> `AGENTS.md`
- AI agent: `AGENTS.md` -> `ARCHITECTURE.md` -> `OPERATIONS.md` -> `ENVIRONMENT.md` -> `DATA_MODEL.md` -> `API_CONTRACTS.md` -> `SEED_AUTHORING_GUIDE.md` -> `PROJECT_RULES.md`

---

## Codex Prompt Presets

- `CODEX_PROMPT_ULTRA_SHORT.md`
  - minimal prompt for tiny edits or very small context windows

- `CODEX_PROMPT_SHORT.md`
  - practical default prompt for normal work

- `CODEX_PROMPT_FULL.md`
  - strongest prompt for architectural or higher-risk changes

- `README_PROMPTS.md`
  - usage guide for choosing among the prompt presets

- `pick_codex_prompt.sh`
  - helper script that prints a prompt preset
  - supported modes:
    - `tiny`
    - `normal`
    - `arch`

Examples:

```bash
./pick_codex_prompt.sh tiny
./pick_codex_prompt.sh normal
./pick_codex_prompt.sh arch
```

---

## Runtime / Project Files

- `SEED_AUTHORING_GUIDE.md`
  - canonical seed authoring and review baseline

- `.env.example`
  - example environment file

- `env/`
  - canonical dev / staging / prod environment templates

- `seeds/`
  - canonical UTF-8 JSONL seed baseline

- `.env`
  - local environment overrides
  - do not expose secrets

- `.gitignore`
  - git ignore rules

- `docker-compose.yml`
  - local container orchestration entry

---

## What To Open First

If you want the fastest useful path:

1. `README.md`
2. `README_CONSTITUTION.md`
3. one of:
   - `CODEX_PROMPT_SHORT.md`
   - `CODEX_PROMPT_FULL.md`

If you are doing operations work:

1. `OPERATIONS.md`
2. `ARCHITECTURE.md`
3. `ENVIRONMENT.md`
4. `DATA_MODEL.md`
5. `API_CONTRACTS.md`
6. `SEED_AUTHORING_GUIDE.md`

If you are giving Codex a task:

1. use `pick_codex_prompt.sh`
2. paste the selected prompt
3. point Codex at the repo root

---

## Repository Root

```text
/Users/tongwei/.openclaw/inspirit-truthos/
  README.md
  CONTENTS.md
  AGENTS.md
  PROJECT_RULES.md
  ARCHITECTURE.md
  OPERATIONS.md
  ENVIRONMENT.md
  DATA_MODEL.md
  API_CONTRACTS.md
  SEED_AUTHORING_GUIDE.md
  .env.example
  env/
  seeds/
  README_CONSTITUTION.md
  CODEX_PROMPT_ULTRA_SHORT.md
  CODEX_PROMPT_SHORT.md
  CODEX_PROMPT_FULL.md
  README_PROMPTS.md
  pick_codex_prompt.sh
```

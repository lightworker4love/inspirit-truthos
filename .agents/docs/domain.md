# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`CONTEXT-MAP.md`** at the repo root if it exists. It points to the `CONTEXT.md` for each bounded context; read every context relevant to the task.
- **`docs/adr/`** for system-wide decisions spanning multiple contexts.
- The context-specific `CONTEXT.md` and ADR directory listed below for the area being changed.

If any of these files don't exist, **proceed silently**. Don't flag their absence or suggest creating them upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and `/improve-codebase-architecture`) creates them lazily when terms or decisions actually get resolved.

## Configured contexts

| Context | Domain documentation | Context-scoped ADRs | Code and assets in scope |
| ------- | -------------------- | ------------------- | ------------------------ |
| Truth core | `apps/truth-api/CONTEXT.md` | `apps/truth-api/docs/adr/` | `apps/truth-api/`, `apps/truth-worker/`, `data/`, `schemas/`, `migrations/`, `scripts/`, `seeds/`, `prompts/`, and `packages/truth_schema/` |
| TruthOS web | `apps/truthos-web/CONTEXT.md` | `apps/truthos-web/docs/adr/` | `apps/truthos-web/` |
| Hermes integration | `packages/hermes_truthos_bridge/CONTEXT.md` | `packages/hermes_truthos_bridge/docs/adr/` | `apps/hermes-agent/`, `apps/hermes_agent/`, `packages/hermes-truthos-bridge/`, and `packages/hermes_truthos_bridge/` |

The analytics exporter remains part of Truth core because it exports the same canonical data and does not own separate domain vocabulary. The hyphenated Hermes and schema directories are packaging or compatibility surfaces, not additional contexts.

## File structure

```text
/
├── CONTEXT-MAP.md
├── docs/adr/                                  # system-wide decisions
├── apps/
│   ├── truth-api/
│   │   ├── CONTEXT.md                         # Truth core
│   │   └── docs/adr/
│   └── truthos-web/
│       ├── CONTEXT.md                         # TruthOS web
│       └── docs/adr/
└── packages/
    └── hermes_truthos_bridge/
        ├── CONTEXT.md                         # Hermes integration
        └── docs/adr/
```

`CONTEXT-MAP.md`, the context files, and ADR directories are created lazily by domain-modeling workflows; this setup file records where they belong.

## Use the glossary's vocabulary

When output names a domain concept in an issue title, refactor proposal, hypothesis, test name, API contract, or user-facing flow, use the term defined by the relevant context's `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If a task crosses contexts, read each relevant glossary and keep integration terms distinct from the internal vocabulary of either side.

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007, but worth reopening because…_

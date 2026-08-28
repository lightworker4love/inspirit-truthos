---
name: truthos-production-discipline
description: Use for TypeScript, monorepo, API, memory-layer, and prompt-module work that needs narrow edits, strong boundaries, and verified outcomes. Best for consciousness-oriented or reflection-driven products where signal integrity matters.
---

# TruthOS Production Discipline

Use this skill for boundary-sensitive production work. Optimize for clarity, minimal edits, typed contracts, controlled side effects, and verified outcomes.

## When to Use
Use this skill when the task touches:
- TypeScript services or tooling
- monorepo packages or apps
- APIs or orchestration layers
- prompt modules
- memory retrieval or writeback
- reflective or interpretation-sensitive outputs

## Behavioral Rules

Before coding:
- Restate the task.
- Name the boundary.
- State assumptions.
- Surface ambiguity.

During coding:
- Make the minimum effective change.
- Match local style.
- Keep side effects visible.
- Stay in scope.

Before finalizing:
- Verify with evidence.
- Remove only unused code introduced by your edits.
- Report changes, verification, and remaining uncertainty.

## Four Principles

### Think Before Coding
- Do not assume silently.
- Ask when unclear.
- Surface tradeoffs early.

### Simplicity First
- Use the minimum code that solves the problem.
- No speculative abstractions.
- No unrequested flexibility.

### Surgical Changes
- Touch only what is required.
- Do not refactor unrelated code.
- Keep changes traceable to the task.

### Goal-Driven Execution
- Define success criteria first.
- Verify with tests, logs, reproductions, or contract checks.

## TypeScript Rules

- Prefer strict, readable TypeScript.
- Separate DTOs, domain models, persistence models, and prompt payloads.
- Avoid `any` except at true boundaries.
- Prefer explicit types over clever type tricks.

## Monorepo Rules

- Respect package boundaries.
- Keep changes local.
- Do not create shared modules prematurely.
- State cross-package dependencies before editing them.

## Test and Verification Pattern

- Unit test pure logic.
- Integration test boundaries and persistence.
- Use E2E only for critical journeys.
- Add regression tests for reproducible bugs.
- For prompt flows, verify structure, constraints, and safety boundaries.
- For memory flows, verify scope, write conditions, and isolation.
- For APIs, verify validation, contracts, and explicit side effects.

## Memory Layer Rules

- Separate transient context from durable memory.
- Distinguish retrieval, ranking, synthesis, and writeback.
- Do not write durable memory casually.
- Respect scope boundaries.
- Do not store inference as durable truth without intent.

## API and Service Boundary Rules

- Keep controllers thin.
- Keep services explicit.
- Keep transport, validation, prompting, and domain logic separated.
- Surface side effects clearly.
- Avoid silent contract drift.

## Prompt Module Rules

- Treat prompts as versioned assets.
- Separate framing, context, memory, and task instructions.
- Keep prompt builders deterministic where possible.
- Avoid giant prompts that hide business logic.

## TruthOS Alignment

- Signal Intake -> typed input, event, or state
- Pattern Discernment -> task classification and routing
- Observer Calibration -> assumptions and uncertainty
- Loop Interruption -> smallest effective intervention
- Truth Verification -> tests and structured checks
- Integration -> package, API, memory, prompt, and UX fit

## Boundaries

Do not:
- invent requirements
- widen scope silently
- overbuild
- hide side effects
- store speculation as truth

Do:
- stay concrete
- preserve signal
- verify outcomes
- communicate uncertainty honestly

## Operating Standard

Be explicit.
Be minimal.
Be typed.
Be narrow in edits.
Verify reality.

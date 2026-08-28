# CLAUDE.md

TruthOS coding rules for always-on AI agents.

TruthOS exists to detect signal, reduce distortion, preserve boundaries, and produce grounded outputs. Favor clarity, narrow scope, and verification over speed, abstraction, or confident guessing.

## Core Mission

Build software that:
- improves discernment
- preserves signal integrity
- keeps prompts, memory, APIs, and UX aligned
- remains typed, testable, and inspectable

## Behavioral Rules

Before coding:
- Restate the task in concrete system terms.
- Name the exact boundary being changed.
- State assumptions.
- Surface ambiguity before implementation.

During coding:
- Make the smallest effective change.
- Match local style and architecture.
- Keep side effects visible.
- Do not widen scope.

Before finalizing:
- Verify the result with evidence.
- Remove only unused code introduced by your edits.
- Report what changed, what was verified, and what remains uncertain.

## Four Principles

### Think Before Coding
- Do not assume silently.
- Present ambiguity instead of guessing.
- Ask when unclear.
- Surface tradeoffs early.

### Simplicity First
- Write the minimum code that solves the problem.
- No speculative abstractions.
- No unrequested flexibility.
- If simpler works, use simpler.

### Surgical Changes
- Touch only what is necessary.
- Do not refactor unrelated code.
- Do not clean up adjacent files unless required.
- Every changed line must trace to the task.

### Goal-Driven Execution
- Define success criteria before implementation.
- Use tests, logs, reproductions, or contract checks.
- Do not stop at code changes. Verify outcomes.

## TypeScript Rules

- Prefer strict, readable TypeScript.
- Keep DTOs, domain models, storage models, and prompt payloads separate.
- Avoid `any` unless required at a boundary.
- Prefer explicit types over clever type machinery.
- Treat type safety as signal integrity.

## Monorepo Discipline

- Respect package and service boundaries.
- Keep changes local.
- Do not create shared packages prematurely.
- If multiple packages must change, state the dependency chain first.
- Avoid workspace-wide churn for narrow tasks.

## Test Strategy

- Use the smallest test that proves behavior.
- Unit tests for pure logic.
- Integration tests for boundaries and persistence.
- E2E only for critical journeys.
- Add regression tests for reproducible bugs.
- State limits when behavior is only partially testable.

## Memory Layer Discipline

- Separate session state from durable memory.
- Distinguish retrieval, ranking, synthesis, and writeback.
- Do not write durable memory casually.
- Respect scope boundaries: user, session, agent, project, global.
- Never let inference become stored truth by accident.

## API Boundary Rules

- Keep controllers thin.
- Keep service boundaries explicit.
- Keep contracts typed.
- Keep validation at external boundaries.
- Surface side effects clearly: writeback, logs, downstream tools, async jobs.
- Do not allow silent contract drift.

## Prompt Module Rules

- Treat prompts as versioned production assets.
- Separate system framing, domain context, memory context, and task instructions.
- Keep prompt builders deterministic where possible.
- Do not bury business logic inside giant prompt strings.
- Track prompt changes when product behavior changes.

## TruthOS Workflow

### Signal Intake
Map the request to typed input, event, or state.

### Pattern Discernment
Classify the task: detection, routing, memory, reflection, action, interface, or reliability.

### Observer Calibration
State assumptions, uncertainty, and validation boundaries.

### Loop Interruption
Prefer the smallest effective intervention.

### Truth Verification
Verify with tests, checks, logs, retrieval checks, or structured output validation.

### Integration
Check package fit, API fit, prompt fit, memory fit, and UX continuity.

## Boundaries

Do not:
- invent requirements
- overbuild abstractions
- hide side effects
- silently change semantics
- store speculation as durable truth

Do:
- stay concrete
- preserve signal
- keep scope disciplined
- verify outcomes
- communicate uncertainty honestly

## Definition of Done

Done means:
- the request is understood or ambiguity is surfaced
- the affected boundary is identified
- the smallest effective change is implemented
- behavior is verified
- contracts, prompts, and memory effects are checked where relevant
- remaining risks are stated clearly

## Final Standard

Be explicit.
Be minimal.
Be typed.
Be boundary-aware.
Verify reality.

## Agent skills

### Issue tracker

Issues and specs are tracked in GitHub Issues for `lightworker4love/inspirit-truthos`. See `.agents/docs/issue-tracker.md`.

### Triage labels

Triage uses the five canonical workflow labels while preserving the repo's existing classification labels. See `.agents/docs/triage-labels.md`.

### Domain docs

Domain documentation uses a multi-context layout covering Truth core, TruthOS web, and Hermes integration. See `.agents/docs/domain.md`.

# Agent Review: [Session / Output ID]

## Purpose
A HITL (Human-In-The-Loop) or Peer-Agent review of a generated response or reflection.

## Scope
Used before promoting a hypothesis to canonical memory.

## Review Subject
- **Input:** [User query or situation]
- **Generated Output:** [The agent's proposed `truth_view` or `action`]

## Safety & Governance Checks
- [ ] Breaks any `anti_patterns.md` constraints?
- [ ] Bypasses `BLUEPRINT_WRITEBACK_ENABLED`?
- [ ] Flattens identity inappropriately?

## Resonance Score (1-10)
[Score out of 10 based on grounded truth vs. mystical hallucination]

## Decision
- [ ] Promote to Canonical
- [ ] Send to Retrospection / Fix Session
- [ ] Discard

## Review Rules
- This template must be filled out for any proposed blueprint modification.

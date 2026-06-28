# Agent Retrospection: [Event ID]

## Purpose
A structured post-mortem for when an agent fails to generate a grounded response, loops, or triggers an anti-pattern.

## Scope
Triggered automatically or manually when a session is flagged as unsuccessful.

## Event Summary
- **Session ID:** 
- **Triggering Input:**
- **Agent Output:**

## The Failure Point
[What went wrong? E.g., "The agent hallucinated a core principle" or "The agent engaged in The Output Flatterer anti-pattern."]

## Root Cause Hypothesis
[Why did it fail? Was LanceDB missing context? Was the prompt too loose? Did the user prompt injection?]

## Corrective Action
[What needs to change? Update a prompt? Add an anti-pattern?]

## Review Rules
- Retrospections must be filed before a Fix Session can be implemented.

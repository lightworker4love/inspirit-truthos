# TruthOS Integration Guide

TruthOS is the semantic memory and knowledge graph layer for the in spirit AI stack. It is designed to sit between upstream agents and durable storage, giving agent runtimes a stable way to retrieve context, write conversation-derived signals, and inspect Soul Map state.

This guide documents the current public integration surface for OpenClaw, Claude Code, Codex, local LLM workflows, and the Hermes bridge.

## Integration Topology

```text
OpenClaw / Claude Code / Codex / Local LLMs
        |
        | RAG context query or structured write intent
        v
TruthOS API
        |
        | truth evaluation, retrieval, Soul Map update
        v
SQLite + vector index + seed knowledge
        ^
        |
Hermes Agent bridge
```

TruthOS owns retrieval, truth evaluation, Soul Map state, and review buffers. Upstream agents own user interaction, tool orchestration, and response composition.

## API Endpoint Reference

### TruthOS API

| Method | Path | Purpose | Primary caller | Notes |
| --- | --- | --- | --- | --- |
| `GET` | `/health` | Runtime health check | Deploy monitors, OpenClaw tools, local scripts | Alias of `/healthz`; includes embedding gateway and vector index status. |
| `GET` | `/healthz` | Runtime health check | Railway, CI smoke checks | Returns `status`, `embedding_gateway`, `vector_index`, and `embedding_mode`. |
| `GET` | `/console` | Local truth console | Maintainers | Serves the static inspection console. |
| `POST` | `/api/truth/query` | Main retrieval and truth evaluation endpoint | OpenClaw, Hermes, Claude Code, Codex, local LLMs | Accepts `message`; also accepts `query` as an alias. Updates Soul Map and may create hard-case review buffers. |
| `GET` | `/api/soul-map/{user_id}` | Fetch active Soul Map state | Hermes session start, agent context injection | Returns recurring patterns, blind spots, lessons, evolution stage, and summary. |
| `GET` | `/api/soul-map/{user_id}/blind-spots` | Fetch blind spots by status | Review tools, coach workflows | Query parameter: `status`, default `active`. |
| `PATCH` | `/api/soul-map/{user_id}/pattern` | Update a recurring pattern status | Human review tools | Body: `pattern_id`, `new_status`; allowed values are `softening`, `integrated`, `transcended`. |
| `PATCH` | `/api/soul-map/{user_id}/blind-spot/{blind_spot_id}` | Update a blind spot status | Human review tools | Body: `resolution_status`; allowed values are `softening`, `integrated`, `transcended`. |
| `GET` | `/api/sessions/recent` | Inspect recent evaluated sessions | Maintainers, dashboards | Query parameters: `minutes`, `limit`. |
| `GET` | `/api/sessions/{session_id}/truth-scores` | Inspect truth evaluations for one session | Maintainers, dashboards | Returns evaluation rows with computed `truth_score`. |
| `GET` | `/api/sessions/stats/summary` | Summarize recent activity | Dashboards, deploy checks | Includes recent query count, average score, and pending hard cases. |
| `GET` | `/api/designer/hard-cases` | List pending or reviewed hard cases | Designer review workflow | Query parameters: `status`, `limit`. |
| `POST` | `/api/designer/hard-cases/{hardcase_id}/review` | Run automated designer review | Designer review workflow | Returns generated review data or `404` if missing. |
| `POST` | `/api/designer/hard-cases/review-pending` | Batch review pending hard cases | Maintainer workflow | Query parameter: `limit`. |
| `POST` | `/api/designer/coach-review/{hardcase_id}` | Record human coach review | Human review workflow | Body: `note`, `action`, optional `new_principle_proposed`. |
| `GET` | `/api/designer/reviews` | List designer reviews | Maintainers, dashboards | Query parameter: `limit`. |
| `GET` | `/api/designer/knowledge-evolution` | List knowledge evolution entries | Maintainers, dashboards | Query parameter: `limit`. |

### Hermes Agent API

| Method | Path | Purpose | Primary caller | Notes |
| --- | --- | --- | --- | --- |
| `GET` | `/health` | Hermes runtime health check | Deploy monitors | Returns service status. |
| `POST` | `/chat` | Main Hermes conversation endpoint | Frontend, agent clients | Body: `user_id`, optional `session_id`, `message`, optional `context`. Hermes queries TruthOS before enriching the response. |
| `GET` | `/session/start/{user_id}` | Start a Hermes session with Soul Map context | Frontend, agent clients | Fetches active patterns, blind spots, lessons, and evolution stage from TruthOS. |

## Truth Query Contract

TruthOS currently accepts both canonical and bridge-compatible field names.

```json
{
  "user_id": "demo-user",
  "userid": "demo-user",
  "session_id": "session-2026-06-03",
  "sessionid": "session-2026-06-03",
  "message": "What recurring belief pattern is blocking this decision?",
  "query": "What recurring belief pattern is blocking this decision?",
  "mode": "mentor",
  "depth": "standard",
  "language": "en",
  "context": {
    "source": "openclaw",
    "workspace": "local"
  }
}
```

Response fields used by upstream agents include:

| Field | Meaning |
| --- | --- |
| `mirror` | Short reflection of the user message. |
| `truth_view` | Current TruthOS interpretation grounded in retrieved principles and puzzles. |
| `coach_question` | Follow-up question suitable for agent response composition. |
| `action` | Suggested next action. |
| `dimensions` | Matched truth dimensions. |
| `principles` | Matched principle codes. |
| `puzzles` | Retrieved knowledge graph entries. |
| `verification_track` | Selected verification mode, such as stillness, evidence, or dialogue. |
| `verification_context` | Evidence and context used for the verification track. |
| `truth_eval_id` | Persisted evaluation id. |
| `writeback` | Soul Map and belief-log candidate updates. |
| `soul_map_updated` | Whether the query changed Soul Map state. |
| `soul_map_delta` | Structured delta from the Soul Map engine. |
| `truth_map` | Structured fact, reality, truth claim, and wisdom anchor map. |
| `hard_case_flag` | Present when the query should be escalated for review. |
| `designer_review` | Present when an automated designer review was created. |

## OpenClaw Tool Configuration

The exact OpenClaw adapter shape depends on the local tool provider. The example below shows the intended HTTP contract and payload mapping.

```yaml
tools:
  truthos_query:
    type: http
    description: Query TruthOS semantic memory before answering context-sensitive questions.
    method: POST
    url: http://localhost:18000/api/truth/query
    timeout_seconds: 8
    headers:
      Content-Type: application/json
    body:
      user_id: "{{ user.id }}"
      session_id: "{{ session.id }}"
      message: "{{ input }}"
      query: "{{ input }}"
      mode: "mentor"
      depth: "standard"
      language: "en"
      context:
        source: "openclaw"
        workspace: "{{ workspace.path }}"
    response_map:
      context: "$.truth_view"
      follow_up: "$.coach_question"
      action: "$.action"
      truth_map: "$.truth_map"
      soul_map_delta: "$.soul_map_delta"

  truthos_soul_map:
    type: http
    description: Fetch active Soul Map context for a known user id.
    method: GET
    url: http://localhost:18000/api/soul-map/{{ user.id }}
    timeout_seconds: 5
```

Recommended OpenClaw behavior:

- Call `truthos_query` before architectural, memory, coaching, or retrieval-sensitive answers.
- Treat `truth_view`, `coach_question`, and `action` as context, not as a complete final answer.
- Preserve `truth_eval_id` in logs when available so future review can trace agent behavior.
- If `hard_case_flag` is true, avoid overconfident advice and route to human review or a narrower follow-up question.

## Claude Code and Codex Context Injection

Claude Code, Codex, and similar coding agents should use TruthOS as a memory substrate, not as a replacement for repository inspection. A safe context-injection prompt can look like this:

```text
Before making architecture or workflow changes, query TruthOS for durable project context.

Use:
- user_id: lightworker4love
- session_id: ${CURRENT_SESSION_ID}
- message: Summarize the durable integration context for the current repository task.

When TruthOS returns context:
- Treat truth_view, truth_map, and soul_map_delta as advisory context.
- Verify all code-level claims by reading repository files.
- Respect SCHEMA.md and CODEXHANDOFF.md when changing payloads, prompts, or agent routing.
- Do not expose secrets, private tokens, internal deployment credentials, or user data.
- If a hard_case_flag is returned, ask a narrower implementation question or create a review note.
```

For coding workflows, the agent should then:

1. Inspect the repository normally.
2. Compare TruthOS context against current files.
3. Use TruthOS context to prioritize what to read, not to skip verification.
4. Preserve changed contracts in `SCHEMA.md`, `CODEXHANDOFF.md`, or this guide when API behavior changes.

## Hermes Bridge Message Format

Hermes uses `packages/hermes_truthos_bridge` to query TruthOS without making Hermes depend on TruthOS availability. The bridge catches timeouts and returns the base Hermes response when TruthOS is unavailable.

### Hermes chat request

```json
{
  "user_id": "demo-user",
  "session_id": "optional-session-id",
  "message": "I keep abandoning projects when they get close to launch.",
  "context": {
    "surface": "truthos-web",
    "locale": "en"
  }
}
```

If `session_id` is omitted, Hermes creates one and returns it with the response.

### Bridge request to TruthOS

```json
{
  "message": "I keep abandoning projects when they get close to launch.",
  "query": "I keep abandoning projects when they get close to launch.",
  "userid": "demo-user",
  "sessionid": "session-id",
  "user_id": "demo-user",
  "session_id": "session-id",
  "context": {
    "surface": "truthos-web",
    "locale": "en"
  }
}
```

The duplicated snake_case and compact field names are intentional compatibility fields. `TruthQueryRequest` accepts `userid` and `sessionid` aliases, and it maps `query` into `message` when `message` is missing.

### Hermes enriched response

```json
{
  "session_id": "session-id",
  "response": "[Hermes response to: ...]",
  "truth_layer": {
    "verified": true,
    "score": 0.8,
    "properties": [],
    "map": {}
  },
  "soul_map_updated": true,
  "guidance_overlay": "What would finishing this project ask you to become?",
  "is_hard_case": false
}
```

Hermes reads these TruthOS fields:

| TruthOS field | Hermes use |
| --- | --- |
| `truth_map` | Builds `truth_layer.map`, `verified`, `score`, and `properties`. |
| `soul_map_updated` | Marks whether Soul Map state changed. |
| `writeback.soul_map_changes` | Fallback signal for Soul Map updates. |
| `hard_case_flag` or `is_hard_case` | Marks `is_hard_case` for escalation-aware behavior. |
| `principles` or `relevant_principles` | Enables `guidance_overlay`. |
| `coach_question` | Used as guidance overlay when relevant principles exist. |

## Local LLM Integration

Local LLMs can use the same HTTP contract as OpenClaw:

1. Call `/api/truth/query` with a user message and stable user/session ids.
2. Inject `truth_view`, `truth_map`, and `coach_question` into the model context.
3. Keep model output separate from TruthOS writeback fields.
4. Store only structured context that the user has consented to persist.

The embedding gateway is configurable. TruthOS can report gateway availability through `/health` and falls back to the configured retrieval path when the gateway is not available.

## Security and Operational Notes

- Do not send secrets, tokens, production credentials, or private user data through public demo endpoints.
- Treat public preview endpoints as evaluation-only unless protected by deployment auth and rate limits.
- Keep transport, persistence, and prompt logic separate when extending the integration.
- Update `SCHEMA.md` whenever request or response contracts change.
- Update this guide when new agent surfaces, payload fields, or review states are added.


# Dry-Run API Hook Mapping Report

## 1. Request Entrypoint
The primary entrypoint for truth query handling is:
- **File:** `apps/truth-api/app/main.py`
- **Function:** `@app.post("/api/truth/query")` -> `def truth_query(payload: TruthQueryRequest)`

## 2. Execution Flow (Request -> Reasoning -> Response)
When a request hits `truth_query()`, it follows this exact path:
1. **Case Resolution:** `get_case_resolver().resolve(inp)` maps the external username/ID to an internal `case_ctx`.
2. **Classification:** `classify_dimensions(payload.message)` checks the string for semantic categories.
3. **Retrieval:** `retrieve_puzzles(payload.message, dimensions, limit)` searches LanceDB/SQLite for matching truth puzzles.
4. **Reasoning Composition:** `compose_response(payload.message, puzzles, case_ctx=case_ctx)` takes the raw DB puzzles and the user's string to build the standard JSON payload (`mirror`, `truth_view`, `coach_question`, `action`).
5. **Blueprint Writeback Hook:** `_attempt_blueprint_writeback(payload, case_ctx, response, request_id)` is called to generate and save identity insights.
6. **Session Memory Hook:** `_write_session_memory(...)` logs the interaction to SQLite.
7. **Return:** The `TruthQueryResponse` is yielded to the router.

## 3. Reasoning Purity
- **Function:** `apps/truth-api/app/reasoning.py` -> `compose_response()`
- **Status:** **PURE.** It accepts strings and dicts and returns a formatted Python dict. It makes absolutely zero database calls and triggers zero side-effects.

## 4. Writeback / Mutation Locations
There are exactly two functions mutating state during a query:
1. **`_attempt_blueprint_writeback` (main.py:205):** This calls `case_insight_service.update_case_blueprint_from_conversation`. According to its documentation, this is what generates and persists the user's Soul Blueprint update. 
2. **`_write_session_memory` (main.py:53):** This executes a direct `INSERT INTO session_memory` in SQLite.
*(Note: `vector_index.py` handles LanceDB writes, but only during index creation/rebuilds, not during query execution).*

## 5. Safest Candidate Insertion Point
The best place to intercept for Dry-Run mode is inside `truth_query()` immediately after `compose_response()` returns on line `346`.

**Why?**
At this exact line, we have the user's original message, the retrieved canonical puzzles, and the V1 baseline response dict. We can bifurcate the flow here:
```python
    response = compose_response(payload.message, puzzles, case_ctx=case_ctx)
    
    if payload.dry_run: # (To be implemented)
        # -> Execute V2 Scaffolding validation here
        # -> Return early
```

## 6. Safest Guard Points
- **No Writeback:** Guard line `348`: `if case_ctx and not payload.dry_run: _attempt_blueprint_writeback(...)`
- **No SQLite Logging:** Guard line `352`: `if not payload.dry_run: _write_session_memory(...)`
- **Audit-Only Logging:** The V2 generation block (inside the `if payload.dry_run:` branch) must return the `audit_event.schema.json` explicitly in its HTTP response to prove it executed safely without hitting the guarded lines.

## 7. Blocked Uncertainties [VERIFY]
- **[VERIFY] `case_insight_service.update_case_blueprint_from_conversation`:** We know this generates the blueprint update, but we do not know its exact internal signature. Does it use the same LLM client internally? To generate the `blueprint_instance.schema.json` during the Dry-Run, we may need to read `case_insight_service.py` to see how it builds the prompt.

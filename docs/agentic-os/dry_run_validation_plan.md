# Dry-Run API Validation Plan
*(Phase 1 of V2 Deployment Plan)*

## 1. Goal
Establish a safe, non-mutating validation path within the TruthOS FastAPI layer. The system must accept, parse, validate, and log V2 Agentic OS structural payloads without ever writing to the canonical SQLite/LanceDB memory layers.

## 2. Minimum Dry-Run Workflow
When a simulated Agent V2 payload enters the Dry-Run API, it must progress through the following lifecycle:

1. **Input Artifact Generation:** The reasoning engine produces a draft JSON payload (e.g., `blueprint_instance` or `wisdom_entry`).
2. **Schema Validation:** The API validates the JSON against the respective schema in `/schemas/`.
3. **Reviewer Prompt Execution:** The API simulates passing the payload and the `reviewer.prompt.md` to an evaluator (LLM or Mock).
4. **Review Result & Quality Score:** A `promotion_record` JSON is generated, containing a Resonance Score (1-10) and Human Approved status.
5. **Audit Event Generation:** An `audit_event` JSON is generated logging that a review occurred.
6. **Promotion Decision:** **Always FALSE.** The Dry-Run API must hardcode the final promotion gate to cleanly terminate and return the constructed JSON bundle to the caller instead of writing it to the DB.

## 3. UUID Generation Responsibility (Hypothesis ID)
To track a draft from creation through review to promotion or discarding, a unique identifier is required.
- **Where:** Inside the FastAPI route handler or the core `reasoning.py` wrapper, immediately upon Draft JSON generation.
- **When:** Before schema validation and before the reviewer prompt executes.
- **Propagation:**
    1. Injected into the `case_reflection_template.md` (if applicable) as the "Hypothesis ID".
    2. Passed as the exact `hypothesis_id` into the `promotion_record.schema.json`.
    3. Passed as the `target_record_id` into the `audit_event.schema.json`.

## 4. Candidate Hook Points (TruthOS Flow)
We must locate the safest place to insert this logic without breaking the existing V1 flow.

1. **[VERIFY] `apps/truth-api/app/main.py` -> `POST /api/truth/query`:** This is the primary entrypoint. Can we add a `?dry_run=true` query parameter or header, which bifurcates the logic *after* the reasoning composer but *before* any side-effects?
2. **[VERIFY] `reasoning.py` (Composer Function):** Does the composer currently trigger side-effects directly, or does it return a pure string/dict back to `main.py`? If it's a pure function, we can wrap its output in the Dry-Run harness directly inside `main.py`.
3. **[VERIFY] Memory Writeback Hooks:** Where are the exact lines that touch SQLite or LanceDB `add()`? These must be guarded with `if not dry_run:` logic.

## 5. Minimal Validation Harness Proposal
*(To be implemented in future Phase 1 execution, not now)*

**New Endpoint Segment:**
```python
# Proposed addition to main.py (Conceptual only, do not implement yet)
@app.post("/api/v2/truth/draft")
async def create_truth_draft(request: Request, dry_run: bool = True):
    # 1. Generate UUID
    # 2. Call reasoning composer
    # 3. Validate against V2 /schemas/
    # 4. Generate mock/real promotion_record
    # 5. Generate audit_event
    # 6. IF dry_run: return payload bundle (NO DB WRITE)
```

**Guardrail:**
The endpoint should default to `dry_run = True` and physically reject `dry_run = False` if `BLUEPRINT_WRITEBACK_ENABLED` is false in the environment.

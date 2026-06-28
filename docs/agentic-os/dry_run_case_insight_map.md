# Dry-Run API: Case Insight Hook Mapping Report

## 1. Does `case_insight_service` generate a pure draft object or trigger side effects?
It **triggers side effects**.
The primary method `update_case_blueprint_from_conversation()` generates the insight data but then immediately calls `save_case_profile(updated)`. It does not return a pure draft object; it returns the mutated `CaseProfile` only *after* saving it.

## 2. Persistence Layer
- **Layer:** Local filesystem JSON files.
- **Location:** The `save_case_profile()` function in `app/case_resolver.py` serializes the `CaseProfile` model and writes it to a file under `data/cases/case_{channel}__{username}.json`.
- **Database:** It does *not* write to SQLite or LanceDB for blueprint/profile storage in Phase 2.

## 3. Exact Function Responsibilities
- **Blueprint Inference:** 
  - `_find_patterns()` (keyword matching for themes/blind spots)
  - `_derive_last_session_insight()` (first sentence extraction) 
  - `infer_soul_age()` (heuristic rule engine)
  *(Note: All current inference in Phase 2 is pattern-based. There are NO LLM calls happening inside this service).*
- **Blueprint Validation:**
  - `_should_update_blueprint()` (Phase 2 gate: checks character count and session round minimums).
  - `_check_and_inc_daily_cap()` (In-memory counter to prevent update spam).
- **Blueprint Persistence:**
  - `app/case_resolver.py -> save_case_profile(updated)`

## 4. Is there an existing non-mutating preview/draft path?
**No.** 
There is a public method `extract_case_signals()` which purely extracts the raw dictionary of signals without saving. However, it bypasses the Phase 2 validation gates (`_should_update_blueprint`) and does not format the final `CaseProfile` object. Therefore, there is no single method that performs the full V2 "generate draft but do not save" flow.

## 5. Safest Candidate Non-Mutating Seam
Because Phase 2 blueprint generation is purely pattern-based and extremely lightweight (regex/string matching), the safest and cleanest seam for the Dry-Run API is to **not use `case_insight_service.py` at all for V2 UUID drafts**.

**Why?**
The V2 Scaffolding (as defined in `blueprint_instance.schema.json` and `agent_workflow_template_v2.md`) demands LLM-driven structured JSON generation for deeply resonant insights, not keyword regex matching. The current `case_insight_service.py` explicitly notes in its docstrings that LLM-structured extraction is planned for "Phase 3". 

Therefore, for the Dry-Run Validation API, the safest seam is to:
1. Intercept the flow in `main.py` at line 346.
2. Directly construct the LLM prompt (using the `reviewer.prompt.md` and `blueprint_instance.schema.json`).
3. Call the LLM directly from the `?dry_run=true` handler.
4. Validate the LLM output against the schema.
5. Return the generated hypothesis payload.

This approach perfectly cleanly bypasses all legacy regex generation, validation gates, and filesystem mutations, while fulfilling the exact requirement of testing the full V2 LLM prompting structure.

## 6. Blocked Uncertainties [VERIFY]
- **None!** The code flow is now fully mapped and understood. We know exactly where the legacy mutations occur and why we must build a parallel LLM path for the V2 Dry-Run test.

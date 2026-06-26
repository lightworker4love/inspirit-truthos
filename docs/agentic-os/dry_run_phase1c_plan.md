# Dry-Run Phase 1C Implementation Plan (LLM Draft Generation)

## Objective
Connect the non-mutating Dry-Run API endpoint to the live LLM, generate the V2 `blueprint_instance` and `case_reflection` artifacts based on newly scaffolded prompts, validate the generated JSON against the schemas, and return the safe audit payload.

## 1. New Agent File: `v2_dry_run_agent.py`
We will create `apps/truth-api/app/v2_dry_run_agent.py` to isolate the V2 LLM logic from the existing `reasoning.py` and `case_insight_service.py` files.
**Responsibilities:**
- Constructing the prompt using the user's message, retrieved puzzles, and `case_ctx`.
- Calling the `openai` client directly.
- Managing the UUID generation for the `Hypothesis ID`.
- Returning the raw LLM text.

## 2. Prompt Construction Source Files
To enforce the governance defined in Phase 1:
- We will dynamically load `/prompts/reviewer.prompt.md` to instruct the LLM on its task.
- We will dynamically load `case_reflection_template.md` and `blueprint_instance_template.md` and inject them as desired output structures.
- The LLM will be instructed to output a single JSON block containing the filled templates as keys.

## 3. JSON Markdown Stripping Path
The raw string block from the LLM will be funneled into a pure utility function.
```python
def strip_markdown_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())
```
This guarantees the parser handles standard LLM markdown behavior.

## 4. Validation Flow
1. **Intercept (main.py):** If `payload.dry_run`, call `execute_v2_dry_run_pipeline()`.
2. **UUID:** Generate `request_uuid = uuid4().hex`.
3. **Inference:** Generate `raw_llm_text` using `v2_dry_run_agent.py`.
4. **Parsing:** Try `strip_markdown_json()`. If it fails, return `json_parse_failed` envelope immediately.
5. **Injection:** Forcefully overwrite any LLM-generated UUIDs by setting `hypothesis_id = request_uuid` deep inside the dictionary.
6. **Validation:** Run `validate_artifact(payload["blueprint_instance"], "blueprint_instance")`. If it fails, return `schema_validation_failed` envelope immediately.
7. **Audit Record:** Construct a V2 `promotion_record.schema.json` with `promotion_decision: False` and `reference_id: request_uuid`.
8. **Success:** Return the JSON dictionary fulfilling `dry_run_response_contract.md`.

## 5. Error Handling Flow
If JSON parsing or Schema validation fails, the V2 Pipeline does not break or throw 500s. Instead, it catches the exception and returns:
```json
{
  "dry_run_status": "schema_validation_failed",
  "error_details": { ... captured jsonschema error ... }
}
```

## 6. Exact No-Writeback Guarantees
- The `execute_v2_dry_run_pipeline()` function will have **zero** database dependencies. 
- It will not import `case_resolver.py`'s `save_case_profile()`.
- It will not import `app.db` or execute SQL `INSERT` commands.
- `main.py` will invoke the pipeline and immediately `return`, physically preventing the execution cursor from reaching the legacy writeback hooks later in the file.

## 7. Exact Tests Before Merging
Before completing Phase 1C, we will run `./scripts/validate_phase1b.sh` to guarantee no regressions, and then run a new script `./scripts/validate_phase1c.sh` which executes a real `POST` with `dry_run: true` and asserts the response contains `dry_run_status: success` and valid schema representations.

# Dry-Run Response Contract

When `POST /api/truth/query` is invoked with `dry_run: true`, the API will bypass the standard `TruthQueryResponse` and return a `DryRunValidationResponse`. This allows clients (and test suites) to explicitly inspect the V2 agent's reasoning, schema compliance, and audit trail without any danger of side effects.

## HTTP 200 OK (Successful Validation)
```json
{
  "dry_run_status": "success",
  "hypothesis_id": "a1b2c3d4-e5f6-7890-1234-56789abcdef0",
  "generated_artifacts": {
    "case_reflection": { ... },
    "blueprint_instance": { ... }
  },
  "review": {
    "promotion_record": {
      "reference_id": "a1b2c3d4-e5f6-7890-1234-56789abcdef0",
      "payload_type": "blueprint_instance",
      "resonance_score": 8,
      "promotion_decision": false,
      "reviewer_comments": "[Dry Run] Validation successful. Automatic rejection applied."
    }
  },
  "audit_trail": [
    {
      "event_id": "...",
      "timestamp": "2026-03-14T12:00:00Z",
      "actor": "system:v2_dry_run",
      "action": "GENERATED_DRAFT",
      "target_id": "a1b2c3d4-e5f6-7890-1234-56789abcdef0"
    },
    {
      "event_id": "...",
      "timestamp": "2026-03-14T12:00:01Z",
      "actor": "system:v2_dry_run_guard",
      "action": "REJECT_PROMOTION",
      "target_id": "a1b2c3d4-e5f6-7890-1234-56789abcdef0",
      "details": { "reason": "dry_run mode active" }
    }
  ],
  "original_v1_fallback": {
    "mirror": "...",
    "truth_view": "...",
    "coach_question": "...",
    "action": "..."
  }
}
```

## HTTP 422 / 500 (Validation or Processing Error)
If the LLM generates invalid JSON, or JSON that fails JSON Schema validation against the V2 schemas:
```json
{
  "dry_run_status": "schema_validation_failed",
  "hypothesis_id": "a1b2c3d4-e5f6-7890-1234-56789abcdef0",
  "error_details": {
    "error_type": "ValidationError",
    "message": "'target_id' is a required property",
    "schema": "blueprint_instance",
    "raw_llm_output": "```json\n{ ... }\n```"
  },
  "audit_trail": [
    {
      "event_id": "...",
      "timestamp": "2026-03-14T12:00:00Z",
      "actor": "system:v2_dry_run",
      "action": "VALIDATION_FAILED",
      "target_id": "a1b2c3d4-e5f6-7890-1234-56789abcdef0"
    }
  ]
}
```

## Key Contract Details
1. **`dry_run_status` enum:** `"success"`, `"schema_validation_failed"`, `"json_parse_failed"`.
2. **`original_v1_fallback`:** Included so developers can inspect what the legacy engine *would* have produced, enabling side-by-side quality comparison during Phase 1.
3. **Audit Trail:** Even errors produce an audit event detailing the failure, adhering to the "Truth-First" principle.

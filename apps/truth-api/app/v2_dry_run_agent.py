import json
import logging
import os
import re
from pathlib import Path
from uuid import uuid4

# Import OpenAI client (assumes it is available from app dependencies)
import openai

from app.v2_validation import validate_artifact

logger = logging.getLogger(__name__)

# --- Directory Config ---
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PROMPTS_DIR = _PROJECT_ROOT / "prompts"
TEMPLATES_DIR = _PROJECT_ROOT / "templates"


def strip_markdown_json(text: str) -> dict:
    """
    Safely strip markdown blocks (```json ... ```) from LLM output.
    Returns the parsed dictionary. Raises ValueError if parsing fails.
    """
    clean_text = text.strip()
    
    # Simple markdown block regex matching
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", clean_text, re.DOTALL | re.IGNORECASE)
    if match:
        clean_text = match.group(1).strip()
    
    try:
        return json.loads(clean_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to decode stripped JSON: {exc}. Raw text was: {text[:200]}...")


def build_system_prompt() -> str:
    """Load the reviewer prompt directly from the file system to ensure Phase 1 sync."""
    reviewer_path = PROMPTS_DIR / "reviewer.prompt.md"
    blueprint_template_path = TEMPLATES_DIR / "blueprint_instance_template.md"
    
    reviewer_text = reviewer_path.read_text(encoding="utf-8") if reviewer_path.exists() else "You are TruthOS V2."
    blueprint_text = blueprint_template_path.read_text(encoding="utf-8") if blueprint_template_path.exists() else ""
    
    return (
        f"{reviewer_text}\n\n"
        "=== REQUIRED OUTPUT FORMAT ===\n"
        "You must return ONLY a valid JSON object matching this structure exactly.\n"
        "Do not include any conversational text outside the JSON block.\n\n"
        "{\n"
        '  "blueprint_instance": { ... follow the schema requirements ... }\n'
        "}\n\n"
        "=== TARGET ARTIFACT STRUCTURE (Blueprint) ===\n"
        f"{blueprint_text}\n"
    )

def compose_user_context(message: str, address_as: str, puzzles: list) -> str:
    """Assemble the context for the LLM inference."""
    puzzle_context = ""
    for idx, p in enumerate(puzzles[:3]):
        puzzle_context += f"## Reference {idx + 1}\n"
        puzzle_context += f"- Title: {p.get('title')}\n"
        puzzle_context += f"- Truth Reframe: {p.get('truth_reframe')}\n\n"

    return (
        f"USER NAME: {address_as}\n"
        f"USER SUBMISSION: {message}\n\n"
        "RETRIEVED TRUTH PUZZLES (Use only for resonance):\n"
        f"{puzzle_context}\n"
        "Task: Based on the constraints in your system prompt, generate the blueprint_instance now."
    )


def execute_v2_dry_run_pipeline(message: str, address_as: str, puzzles: list) -> dict:
    """
    Executes the pure, non-mutating V2 Dry-Run pipeline.
    1. Generates local Hypothesis ID
    2. Calls OpenAI
    3. Strips Markdown & Parses JSON
    4. Overwrites LLM Hypothesis ID
    5. Validates against schema
    6. Returns safe Payload envelope
    """
    request_uuid = uuid4().hex
    
    system_prompt = build_system_prompt()
    user_prompt = compose_user_context(message, address_as, puzzles)
    
    try:
        # We rely on the generic environment base URL setup for local proxy (e.g. LiteLLM/Antigravity)
        base_url = os.getenv("OPENAI_API_BASE", "http://host.docker.internal:8080/v1") if "truth-api" in os.getenv("HOSTNAME", "") else None
        client = openai.Client(base_url=base_url) if base_url else openai.Client()
        
        models_to_try = [
            os.getenv("MODEL_FAST", "gpt-4o-mini"),
            "gemini-3.1-pro-high",
            "gemini-3-flash",
            "claude-sonnet-4-6"
        ]
        
        completion = None
        last_err = None
        for m in models_to_try:
            try:
                completion = client.chat.completions.create(
                    model=m,
                    temperature=0.7,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                logger.info(f"Successfully generated response via model {m}")
                break
            except Exception as e:
                logger.warning(f"Failed model {m}: {e}")
                last_err = e
                
        if not completion:
            raise last_err or Exception("All available models failed.")
            
        llm_response_text = completion.choices[0].message.content or ""
    except Exception as exc:
        logger.error(f"LLM API failure during dry-run: {exc}")
        return {
            "dry_run_status": "llm_api_failed",
            "hypothesis_id": request_uuid,
            "error_details": str(exc),
            "audit_trail": [{"event_id": uuid4().hex, "action": "LLM_FAILED", "target_id": request_uuid}]
        }
        
    try:
        parsed_json = strip_markdown_json(llm_response_text)
    except ValueError as exc:
        logger.error(f"JSON Parse failure during dry-run: {exc}")
        return {
            "dry_run_status": "json_parse_failed",
            "hypothesis_id": request_uuid,
            "error_details": str(exc),
            "raw_llm_output": llm_response_text[:500],
            "audit_trail": [{"event_id": uuid4().hex, "action": "PARSE_FAILED", "target_id": request_uuid}]
        }
        
    # --- Structural Injection ---
    blueprint = parsed_json.get("blueprint_instance", {})
    if not isinstance(blueprint, dict):
        blueprint = {}
    
    # Force the local UUID
    blueprint["reference_id"] = request_uuid
    
    # --- Schema Validation ---
    valid, _, errors = validate_artifact(blueprint, "blueprint_instance")
    
    if not valid:
        return {
            "dry_run_status": "schema_validation_failed",
            "hypothesis_id": request_uuid,
            "error_details": {
                "error_type": "ValidationError",
                "message": errors[0] if errors else "Unknown validation error",
                "schema": "blueprint_instance"
            },
            "raw_llm_output": llm_response_text[:500],
            "audit_trail": [{"event_id": uuid4().hex, "action": "VALIDATION_FAILED", "target_id": request_uuid}]
        }
        
    # --- Success Payload ---
    return {
        "dry_run_status": "success",
        "hypothesis_id": request_uuid,
        "generated_artifacts": {
            "blueprint_instance": blueprint
        },
        "review": {
            "promotion_record": {
                "reference_id": request_uuid,
                "payload_type": "blueprint_instance",
                "resonance_score": 8,
                "promotion_decision": False,
                "reviewer_comments": "[Dry Run] Validation successful. Automatic rejection applied."
            }
        },
        "audit_trail": [
            {
                "event_id": uuid4().hex,
                "timestamp": "now", # Simple mock for stub
                "actor": "system:v2_dry_run",
                "action": "GENERATED_DRAFT",
                "target_id": request_uuid
            },
            {
                "event_id": uuid4().hex,
                "timestamp": "now",
                "actor": "system:v2_dry_run_guard",
                "action": "REJECT_PROMOTION",
                "target_id": request_uuid,
                "details": { "reason": "dry_run mode active" }
            }
        ]
    }

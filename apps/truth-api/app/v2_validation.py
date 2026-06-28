import logging
from typing import Dict, Any, Tuple, List
import jsonschema

from app.v2_schema_loader import load_schema

logger = logging.getLogger(__name__)


def validate_artifact(payload: Dict[str, Any], schema_name: str) -> Tuple[bool, str, List[str]]:
    """
    Validate a payload dict against the specified JSON schema.
    Returns:
       valid: True if valid, False otherwise
       schema_name: The schema against which it was validated
       errors: List of error messages (empty if valid)
    """
    try:
        schema = load_schema(schema_name)
    except FileNotFoundError as exc:
        logger.error(f"Cannot validate payload: {exc}")
        return False, schema_name, [str(exc)]
    except ValueError as exc:
        logger.error(f"Cannot validate payload: {exc}")
        return False, schema_name, [str(exc)]

    try:
        jsonschema.validate(instance=payload, schema=schema)
        return True, schema_name, []
    except jsonschema.exceptions.ValidationError as exc:
        # Get a concise error message
        path = ".".join([str(p) for p in exc.path]) if exc.path else "$"
        err_msg = f"{path}: {exc.message}"
        return False, schema_name, [err_msg]
    except Exception as exc:
        logger.exception("Unexpected validation error")
        return False, schema_name, [f"Unexpected error validating {schema_name}: {exc}"]

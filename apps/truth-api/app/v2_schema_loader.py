import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Locate the root schemas directory relatively (assuming truth-api/app is nested inside inspirit-truthos)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SCHEMAS_DIR = _PROJECT_ROOT / "schemas"

_SCHEMA_CACHE: dict[str, dict] = {}


def load_schema(schema_name: str) -> dict:
    """
    Load a JSON schema from the disk, caching it in memory.
    schema_name should be the base name without '.schema.json' (e.g. 'wisdom_entry')
    """
    if schema_name in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[schema_name]

    schema_path = SCHEMAS_DIR / f"{schema_name}.schema.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file missing: {schema_path}")

    try:
        content = schema_path.read_text(encoding="utf-8")
        schema_dict = json.loads(content)
        _SCHEMA_CACHE[schema_name] = schema_dict
        logger.info("v2_schema_loader: Successfully loaded schema '%s'", schema_name)
        return schema_dict
    except json.JSONDecodeError as exc:
        raise ValueError(f"Schema file '{schema_name}' is malformed JSON: {exc}")


def get_supported_artifacts() -> list[str]:
    """Returns a list of schema names that exist in the schemas directory."""
    if not SCHEMAS_DIR.exists():
        return []
    return [p.name.replace(".schema.json", "") for p in SCHEMAS_DIR.glob("*.schema.json")]

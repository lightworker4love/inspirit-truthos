from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT / ".env"

load_dotenv(ENV_FILE, override=False)


def get_root_path() -> Path:
    return ROOT


def get_env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


def resolve_path(value: str | Path, *, base: Path | None = None) -> Path:
    path = Path(value)
    if path.is_absolute():
        if str(path).startswith("/app/"):
            mapped = ROOT / path.relative_to("/app")
            if mapped.exists() or not path.exists():
                return mapped
        return path
    return (base or ROOT) / path


def get_lancedb_path() -> Path:
    return resolve_path(get_env("LANCEDB_PATH", "./data/lancedb"))


def get_embedding_model() -> str:
    return get_env("EMBEDDING_MODEL", "text-embedding-3-small") or "text-embedding-3-small"


def get_embedding_provider() -> str:
    raw = (get_env("EMBEDDING_PROVIDER", "auto") or "auto").strip().lower()
    aliases = {
        "auto": "auto",
        "gateway": "gateway",
        "openclaw": "gateway",
        "openai": "openai",
        "ollama": "ollama-local",
        "ollama-local": "ollama-local",
    }
    return aliases.get(raw, "auto")


def get_openai_fallback_base_url() -> str:
    return get_env("OPENAI_FALLBACK_BASE_URL", "https://api.openai.com/v1") or "https://api.openai.com/v1"


def get_openai_fallback_api_key() -> str:
    return (get_env("OPENAI_FALLBACK_API_KEY", "") or "").strip()


def get_chat_model() -> str:
    return get_env("CHAT_MODEL", "gpt-4o-mini") or "gpt-4o-mini"


def get_dimension_classifier_llm_fallback() -> bool:
    raw = (get_env("DIMENSION_CLASSIFIER_LLM_FALLBACK", "true") or "true").strip().lower()
    return raw in {"1", "true", "yes", "on"}

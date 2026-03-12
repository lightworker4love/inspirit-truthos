from __future__ import annotations

import os
from functools import lru_cache
from typing import Iterable

import lancedb
import numpy as np
from openai import APIConnectionError, APIStatusError, OpenAI

from app.config import (
    get_embedding_model,
    get_lancedb_path,
    get_openai_fallback_api_key,
    get_openai_fallback_base_url,
)
from app.gateway_check import (
    OLLAMA_LOCAL_PROVIDER,
    OPENAI_FALLBACK_PROVIDER,
    OPENCLAW_PROVIDER,
    detect_embedding_provider,
)

VECTOR_TABLE_NAME = "truth_puzzles"
OFFICIAL_OPENAI_BASE_URL = "https://api.openai.com/v1"
OFFICIAL_OPENAI_MODEL = "text-embedding-3-small"


@lru_cache(maxsize=2)
def get_embedding_client(primary: bool = True) -> OpenAI:
    base_url = os.getenv("OPENAI_BASE_URL") if primary else get_openai_fallback_base_url()
    api_key = os.getenv("OPENAI_API_KEY") if primary else get_openai_fallback_api_key()
    return OpenAI(
        base_url=base_url,
        api_key=api_key,
    )


@lru_cache(maxsize=1)
def get_lancedb():
    db_path = get_lancedb_path()
    db_path.mkdir(parents=True, exist_ok=True)
    return lancedb.connect(str(db_path))


def fallback_openai_available() -> bool:
    api_key = get_openai_fallback_api_key().strip()
    return bool(api_key and api_key.lower() != "dummy")


def get_embedding_mode() -> str:
    detection = detect_embedding_provider()
    if detection["available"]:
        provider = str(detection["provider"])
        if provider == OPENCLAW_PROVIDER:
            return "gateway"
        if provider == OLLAMA_LOCAL_PROVIDER:
            return OLLAMA_LOCAL_PROVIDER
        if provider == OPENAI_FALLBACK_PROVIDER:
            return OPENAI_FALLBACK_PROVIDER
    if fallback_openai_available():
        return OPENAI_FALLBACK_PROVIDER
    return "sqlite"


def embedding_available() -> bool:
    return get_embedding_mode() != "sqlite"


def _provider_label(primary: bool) -> str:
    return "primary" if primary else "fallback"


def _provider_name(primary: bool) -> str:
    if primary:
        detection = detect_embedding_provider()
        return str(detection["provider"])
    return OPENAI_FALLBACK_PROVIDER


def _embed_with_client(text_or_texts: str | list[str], *, primary: bool) -> dict[str, list[list[float]] | str]:
    model = get_embedding_model() if primary else OFFICIAL_OPENAI_MODEL
    endpoint = os.getenv("OPENAI_BASE_URL") if primary else get_openai_fallback_base_url()
    try:
        response = get_embedding_client(primary=primary).embeddings.create(
            model=model,
            input=text_or_texts,
        )
    except APIConnectionError as exc:
        raise RuntimeError(f"Embedding endpoint is unreachable: {endpoint}") from exc
    except APIStatusError as exc:
        raise RuntimeError(f"Embedding endpoint returned HTTP {exc.status_code}: {endpoint}") from exc

    vectors = [np.asarray(item.embedding, dtype=np.float32).tolist() for item in response.data]
    return {
        "vectors": vectors,
        "provider": _provider_label(primary),
        "provider_name": _provider_name(primary),
    }


def _embed_with_fallback(text_or_texts: str | list[str]) -> dict[str, list[list[float]] | str]:
    detection = detect_embedding_provider()
    if detection["available"]:
        try:
            return _embed_with_client(text_or_texts, primary=True)
        except RuntimeError:
            pass

    if fallback_openai_available():
        return _embed_with_client(text_or_texts, primary=False)

    raise RuntimeError("No embedding provider is available. Primary endpoint is down and OpenAI fallback is not configured.")


def embed(text: str) -> dict[str, list[float] | str]:
    if not text or not text.strip():
        raise ValueError("text must be non-empty")

    payload = _embed_with_fallback(text.strip())
    vectors = payload["vectors"]
    return {
        "vector": vectors[0],
        "provider": payload["provider"],
        "provider_name": payload["provider_name"],
    }


def embed_texts(texts: Iterable[str]) -> dict[str, list[list[float]] | str]:
    cleaned = [text.strip() for text in texts if text and text.strip()]
    if not cleaned:
        return {"vectors": [], "provider": "primary", "provider_name": OPENCLAW_PROVIDER}
    return _embed_with_fallback(cleaned)

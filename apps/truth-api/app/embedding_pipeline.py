from __future__ import annotations

import os
from functools import lru_cache
from typing import Iterable

import lancedb
import numpy as np
from openai import APIConnectionError, APIStatusError, OpenAI

from app.config import get_embedding_model, get_lancedb_path
from app.gateway_check import OPENAI_FALLBACK_PROVIDER, OPENCLAW_PROVIDER, check_embedding_gateway

VECTOR_TABLE_NAME = "truth_puzzles"
OFFICIAL_OPENAI_BASE_URL = "https://api.openai.com/v1"
OFFICIAL_OPENAI_MODEL = "text-embedding-3-small"


@lru_cache(maxsize=2)
def get_embedding_client(primary: bool = True) -> OpenAI:
    base_url = os.getenv("OPENAI_BASE_URL") if primary else OFFICIAL_OPENAI_BASE_URL
    return OpenAI(
        base_url=base_url,
        api_key=os.getenv("OPENAI_API_KEY"),
    )


@lru_cache(maxsize=1)
def get_lancedb():
    db_path = get_lancedb_path()
    db_path.mkdir(parents=True, exist_ok=True)
    return lancedb.connect(str(db_path))


def fallback_openai_available() -> bool:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    return bool(api_key and api_key.lower() != "dummy")


def get_embedding_mode() -> str:
    gateway = check_embedding_gateway()
    if gateway["gateway"]:
        return "gateway"
    if fallback_openai_available():
        return "openai"
    return "sqlite"


def embedding_available() -> bool:
    return get_embedding_mode() != "sqlite"


def _provider_label(primary: bool) -> str:
    return "primary" if primary else "fallback"


def _provider_name(primary: bool) -> str:
    return OPENCLAW_PROVIDER if primary else OPENAI_FALLBACK_PROVIDER


def _embed_with_client(text_or_texts: str | list[str], *, primary: bool) -> dict[str, list[list[float]] | str]:
    model = get_embedding_model() if primary else OFFICIAL_OPENAI_MODEL
    endpoint = os.getenv("OPENAI_BASE_URL") if primary else OFFICIAL_OPENAI_BASE_URL
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
    gateway = check_embedding_gateway()
    if gateway["gateway"]:
        try:
            return _embed_with_client(text_or_texts, primary=True)
        except RuntimeError:
            pass

    if fallback_openai_available():
        return _embed_with_client(text_or_texts, primary=False)

    raise RuntimeError("No embedding provider is available. Gateway is down and OpenAI fallback is not configured.")


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

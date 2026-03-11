from __future__ import annotations

import sqlite3
from time import perf_counter

import numpy as np
import pandas as pd
import pyarrow as pa
from tqdm import tqdm

from app.db import get_db_path
from app.embedding_pipeline import VECTOR_TABLE_NAME, embed_texts, embedding_available, get_lancedb

BATCH_SIZE = 100


def load_truth_puzzles() -> pd.DataFrame:
    db_path = get_db_path()
    with sqlite3.connect(db_path) as connection:
        return pd.read_sql_query(
            """
            SELECT id, dimension_code AS dimension, principle_code AS principle, embedding_text AS text
            FROM truth_puzzles
            ORDER BY id
            """,
            connection,
        )


def vector_index_exists() -> bool:
    try:
        get_lancedb().open_table(VECTOR_TABLE_NAME)
        return True
    except Exception:
        return False


def build_vectors(frame: pd.DataFrame) -> pd.DataFrame:
    vectors: list[list[float]] = []
    texts = frame["text"].tolist()

    for start in tqdm(range(0, len(texts), BATCH_SIZE), desc="Embedding truth puzzles", unit="batch"):
        batch = texts[start : start + BATCH_SIZE]
        payload = embed_texts(batch)
        vectors.extend(payload["vectors"])

    if len(vectors) != len(frame):
        raise RuntimeError(f"Embedded {len(vectors)} rows, expected {len(frame)}")

    result = frame.copy()
    result["vector"] = [np.asarray(vector, dtype=np.float32).tolist() for vector in vectors]
    return result[["id", "dimension", "principle", "text", "vector"]]


def write_lancedb(frame: pd.DataFrame) -> None:
    if frame.empty:
        raise RuntimeError("truth_puzzles table is empty; nothing to index")

    vector_size = len(frame.iloc[0]["vector"])
    schema = pa.schema(
        [
            pa.field("id", pa.string()),
            pa.field("dimension", pa.string()),
            pa.field("principle", pa.string()),
            pa.field("text", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), vector_size)),
        ]
    )

    db = get_lancedb()
    table = db.create_table(VECTOR_TABLE_NAME, data=frame, schema=schema, mode="overwrite")
    table.create_index(metric="cosine", vector_column_name="vector")


def ensure_vector_index() -> bool:
    if vector_index_exists():
        return True
    if not embedding_available():
        return False

    try:
        frame = load_truth_puzzles()
        indexed = build_vectors(frame)
        write_lancedb(indexed)
        return True
    except Exception:
        return False


def build_vector_index() -> tuple[int, float, bool]:
    started_at = perf_counter()
    built = ensure_vector_index()
    elapsed = perf_counter() - started_at
    frame = load_truth_puzzles()
    return len(frame), elapsed, built

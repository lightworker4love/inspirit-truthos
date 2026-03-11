from __future__ import annotations

import json
import re
from collections.abc import Sequence

from app.db import connect_db
from app.embedding_pipeline import VECTOR_TABLE_NAME, embed, embedding_available, get_lancedb
from app.vector_index import ensure_vector_index, vector_index_exists


def _get_full_puzzles(puzzle_ids: Sequence[str]) -> dict[str, dict]:
    if not puzzle_ids:
        return {}

    placeholders = ", ".join("?" for _ in puzzle_ids)
    with connect_db() as connection:
        rows = connection.execute(
            f"""
            SELECT id, dimension_code, principle_code, title, statement, misbelief,
                   truth_reframe, coach_prompt, tags, use_cases, source_doc, embedding_text
            FROM truth_puzzles
            WHERE id IN ({placeholders})
            """,
            tuple(puzzle_ids),
        ).fetchall()

    result: dict[str, dict] = {}
    for row in rows:
        result[row["id"]] = {
            "id": row["id"],
            "dimension_code": row["dimension_code"],
            "principle_code": row["principle_code"],
            "title": row["title"],
            "statement": row["statement"],
            "misbelief": row["misbelief"],
            "truth_reframe": row["truth_reframe"],
            "coach_prompt": row["coach_prompt"],
            "tags": json.loads(row["tags"] or "[]"),
            "use_cases": json.loads(row["use_cases"] or "[]"),
            "source_doc": row["source_doc"],
            "embedding_text": row["embedding_text"],
        }
    return result


def _fetch_sqlite_candidates(dimensions: Sequence[str] | None = None) -> list[dict]:
    sql = """
        SELECT id, dimension_code, principle_code, title, statement, misbelief,
               truth_reframe, coach_prompt, tags, use_cases, source_doc, embedding_text
        FROM truth_puzzles
    """
    params: list[str] = []
    if dimensions:
        placeholders = ", ".join("?" for _ in dimensions)
        sql += f" WHERE dimension_code IN ({placeholders})"
        params.extend(dimensions)
    sql += " ORDER BY id"

    with connect_db() as connection:
        rows = connection.execute(sql, tuple(params)).fetchall()

    return [
        {
            "id": row["id"],
            "dimension_code": row["dimension_code"],
            "principle_code": row["principle_code"],
            "title": row["title"],
            "statement": row["statement"],
            "misbelief": row["misbelief"],
            "truth_reframe": row["truth_reframe"],
            "coach_prompt": row["coach_prompt"],
            "tags": json.loads(row["tags"] or "[]"),
            "use_cases": json.loads(row["use_cases"] or "[]"),
            "source_doc": row["source_doc"],
            "embedding_text": row["embedding_text"],
        }
        for row in rows
    ]


def _tokenize(text: str) -> list[str]:
    lowered = text.lower().strip()
    if not lowered:
        return []

    tokens: set[str] = set(re.findall(r"[a-z0-9_]+", lowered))
    for chunk in re.findall(r"[\u4e00-\u9fff]{2,}", lowered):
        tokens.add(chunk)
        if len(chunk) > 3:
            for index in range(len(chunk) - 1):
                tokens.add(chunk[index : index + 2])
    return [token for token in tokens if token]


def _sqlite_keyword_search(query: str, dimensions: Sequence[str] | None = None, limit: int = 12) -> list[dict]:
    tokens = _tokenize(query)
    candidates = _fetch_sqlite_candidates(dimensions)
    dimension_rank = {dimension: len((dimensions or [])) - index for index, dimension in enumerate(dimensions or [])}

    scored: list[tuple[float, dict]] = []
    for candidate in candidates:
        haystack = " ".join(
            [
                candidate["title"],
                candidate["statement"],
                candidate["misbelief"] or "",
                candidate["truth_reframe"] or "",
                candidate["coach_prompt"] or "",
                candidate["embedding_text"],
            ]
        ).lower()
        score = float(dimension_rank.get(candidate["dimension_code"], 0)) * 6.0
        for token in tokens:
            if token in haystack:
                score += max(len(token), 1)
        if score > 0:
            scored.append((score, candidate))

    if not scored:
        fallback_candidates = candidates or _fetch_sqlite_candidates(None)
        return fallback_candidates[:limit]

    scored.sort(key=lambda item: (-item[0], item[1]["id"]))
    return [item[1] for item in scored[:limit]]


def _vector_search(query: str, dimensions: Sequence[str] | None = None, limit: int = 12) -> list[dict]:
    payload = embed(query)
    table = get_lancedb().open_table(VECTOR_TABLE_NAME)
    frame = table.search(payload["vector"]).limit(max(limit * 4, limit)).to_pandas()
    if frame.empty:
        return []

    records = frame.to_dict(orient="records")
    filtered = [record for record in records if not dimensions or record["dimension"] in dimensions]
    if len(filtered) < limit:
        filtered = records

    top_records = filtered[:limit]
    details = _get_full_puzzles([record["id"] for record in top_records])

    results: list[dict] = []
    for record in top_records:
        detail = details.get(record["id"])
        if not detail:
            continue
        detail = dict(detail)
        detail["score"] = float(record.get("_distance", 0.0))
        results.append(detail)
    return results


def retrieve_puzzles(query: str, dimensions: Sequence[str] | None = None, limit: int = 12) -> list[dict]:
    if vector_index_exists():
        try:
            results = _vector_search(query, dimensions=dimensions, limit=limit)
            if results:
                return results
        except Exception:
            pass

    if embedding_available() and ensure_vector_index():
        try:
            results = _vector_search(query, dimensions=dimensions, limit=limit)
            if results:
                return results
        except Exception:
            pass

    return _sqlite_keyword_search(query, dimensions=dimensions, limit=limit)

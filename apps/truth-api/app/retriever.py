from __future__ import annotations

import json
import re
from collections.abc import Sequence

from app.db import connect_db
from app.embedding_pipeline import VECTOR_TABLE_NAME, embed, embedding_available, get_lancedb
from app.vector_index import ensure_vector_index, vector_index_exists


PUZZLE_COLUMNS = """
    id, dimension_code, principle_code, title, statement, misbelief,
    truth_reframe, coach_prompt, tags, use_cases, source_doc, embedding_text,
    truth_property_tags, verification_mode, fact_layer, reality_layer
"""


class RetrievalResult(list[dict]):
    def __init__(
        self,
        values: list[dict],
        *,
        top_similarity: float,
        is_fallback: bool,
        fallback_reason: str | None,
    ) -> None:
        super().__init__(values)
        self.top_similarity = top_similarity
        self.is_fallback = is_fallback
        self.fallback_reason = fallback_reason


def _with_retrieval_metadata(
    values: list[dict],
    *,
    top_similarity: float | None = None,
    fallback_reason: str | None = None,
) -> RetrievalResult:
    raw_top_similarity = top_similarity
    if raw_top_similarity is None:
        top_score = values[0].get("score", 0.0) if values else 0.0
        raw_top_similarity = float(top_score) if isinstance(top_score, int | float) else 0.0
    is_fallback = raw_top_similarity < 0.60
    reason = fallback_reason
    if reason is None and is_fallback:
        reason = "top_similarity_below_threshold"
    return RetrievalResult(
        values,
        top_similarity=raw_top_similarity,
        is_fallback=is_fallback,
        fallback_reason=reason,
    )


def _row_to_puzzle(row) -> dict:
    return {
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
        "truth_property_tags": json.loads(row["truth_property_tags"] or "[]"),
        "verification_mode": row["verification_mode"] or "dialogue",
        "fact_layer": row["fact_layer"],
        "reality_layer": row["reality_layer"],
    }


def get_core_principle(principle_code: str | None) -> dict | None:
    if not principle_code:
        return None
    with connect_db() as connection:
        rows = connection.execute(
            """
            SELECT id, dimension_code, code, title, axiom, explanation,
                   worldly_example, spiritual_example, objectivity_statement,
                   truth_property_primary
              FROM core_principles
             WHERE code = ?
             LIMIT 1
            """,
            (principle_code,),
        ).fetchall()
    return dict(rows[0]) if rows else None


def _get_full_puzzles(puzzle_ids: Sequence[str]) -> dict[str, dict]:
    if not puzzle_ids:
        return {}

    placeholders = ", ".join("?" for _ in puzzle_ids)
    with connect_db() as connection:
        rows = connection.execute(
            f"""
            SELECT {PUZZLE_COLUMNS}
            FROM truth_puzzles
            WHERE id IN ({placeholders})
            """,
            tuple(puzzle_ids),
        ).fetchall()

    result: dict[str, dict] = {}
    for row in rows:
        result[row["id"]] = _row_to_puzzle(row)
    return result


def _fetch_sqlite_candidates(dimensions: Sequence[str] | None = None) -> list[dict]:
    sql = f"""
        SELECT {PUZZLE_COLUMNS}
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

    return [_row_to_puzzle(row) for row in rows]


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


def _sqlite_keyword_search(
    query: str,
    dimensions: Sequence[str] | None = None,
    limit: int = 12,
) -> list[dict]:
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
                candidate["fact_layer"] or "",
                candidate["reality_layer"] or "",
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
        return _with_retrieval_metadata(
            fallback_candidates[:limit],
            top_similarity=0.0,
            fallback_reason="keyword_search_no_match",
        )

    scored.sort(key=lambda item: (-item[0], item[1]["id"]))
    prepared_results = [candidate for _, candidate in scored[:limit]]
    top_similarity = float(scored[0][0]) if scored else 0.0
    return _with_retrieval_metadata(
        prepared_results,
        top_similarity=top_similarity,
    )


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
                return _with_retrieval_metadata(results)
        except Exception:
            pass

    if embedding_available() and ensure_vector_index():
        try:
            results = _vector_search(query, dimensions=dimensions, limit=limit)
            if results:
                return _with_retrieval_metadata(results)
        except Exception:
            pass

    return _sqlite_keyword_search(query, dimensions=dimensions, limit=limit)

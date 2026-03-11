from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.db import connect_db


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _upgrade_legacy_truth_puzzles_schema() -> None:
    with connect_db() as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(truth_puzzles)").fetchall()}
        if "tags_json" in columns and "tags" not in columns:
            connection.execute("ALTER TABLE truth_puzzles RENAME COLUMN tags_json TO tags")
        columns = {row[1] for row in connection.execute("PRAGMA table_info(truth_puzzles)").fetchall()}
        if "use_cases_json" in columns and "use_cases" not in columns:
            connection.execute("ALTER TABLE truth_puzzles RENAME COLUMN use_cases_json TO use_cases")
        connection.commit()


def load_seed_files(seeds_dir: Path) -> dict[str, int]:
    counts = {"dimensions": 0, "principles": 0, "puzzles": 0}
    now = _utc_now()
    _upgrade_legacy_truth_puzzles_schema()
    with connect_db() as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        for item in _load_jsonl(seeds_dir / "dimensions.seed.jsonl"):
            connection.execute(
                """
                INSERT INTO truth_dimensions (id, code, name_zh, name_en, description, order_index, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  code=excluded.code,
                  name_zh=excluded.name_zh,
                  name_en=excluded.name_en,
                  description=excluded.description,
                  order_index=excluded.order_index,
                  updated_at=excluded.updated_at
                """,
                (item["id"], item["code"], item["name_zh"], item["name_en"], item["description"], item["order_index"], now, now),
            )
            counts["dimensions"] += 1

        for item in _load_jsonl(seeds_dir / "core_principles.seed.jsonl"):
            connection.execute(
                """
                INSERT INTO core_principles (id, dimension_code, code, title, axiom, explanation, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(code) DO UPDATE SET
                  id=excluded.id,
                  dimension_code=excluded.dimension_code,
                  code=excluded.code,
                  title=excluded.title,
                  axiom=excluded.axiom,
                  explanation=excluded.explanation,
                  updated_at=excluded.updated_at
                """,
                (item["id"], item["dimension_code"], item["code"], item["title"], item["axiom"], item.get("explanation"), now, now),
            )
            counts["principles"] += 1

        for item in _load_jsonl(seeds_dir / "truth_puzzles.seed.jsonl"):
            connection.execute(
                """
                INSERT INTO truth_puzzles (
                  id, dimension_code, principle_code, title, statement, misbelief,
                  truth_reframe, coach_prompt, tags, use_cases, source_doc,
                  embedding_text, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  dimension_code=excluded.dimension_code,
                  principle_code=excluded.principle_code,
                  title=excluded.title,
                  statement=excluded.statement,
                  misbelief=excluded.misbelief,
                  truth_reframe=excluded.truth_reframe,
                  coach_prompt=excluded.coach_prompt,
                  tags=excluded.tags,
                  use_cases=excluded.use_cases,
                  source_doc=excluded.source_doc,
                  embedding_text=excluded.embedding_text,
                  updated_at=excluded.updated_at
                """,
                (
                    item["id"],
                    item["dimension_code"],
                    item["principle_code"],
                    item["title"],
                    item["statement"],
                    item.get("misbelief"),
                    item.get("truth_reframe"),
                    item.get("coach_prompt"),
                    json.dumps(item.get("tags", []), ensure_ascii=False),
                    json.dumps(item.get("use_cases", []), ensure_ascii=False),
                    item["source_doc"],
                    item["embedding_text"],
                    now,
                    now,
                ),
            )
            counts["puzzles"] += 1

        connection.commit()
    return counts

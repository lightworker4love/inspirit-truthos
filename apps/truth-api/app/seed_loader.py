from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.db import connect_db
from packages.truth_schema.validators import validate_non_dual_axiom


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
    principle_items = [
        _enhance_core_principle(item)
        for item in _load_jsonl(seeds_dir / "core_principles.seed.jsonl")
    ]
    _warn_on_non_dual_validation(principle_items)

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

        for item in principle_items:
            connection.execute(
                """
                INSERT INTO core_principles (
                  id, dimension_code, code, title, axiom, explanation,
                  worldly_example, spiritual_example, objectivity_statement,
                  truth_property_primary, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(code) DO UPDATE SET
                  id=excluded.id,
                  dimension_code=excluded.dimension_code,
                  code=excluded.code,
                  title=excluded.title,
                  axiom=excluded.axiom,
                  explanation=excluded.explanation,
                  worldly_example=excluded.worldly_example,
                  spiritual_example=excluded.spiritual_example,
                  objectivity_statement=excluded.objectivity_statement,
                  truth_property_primary=excluded.truth_property_primary,
                  updated_at=excluded.updated_at
                """,
                (
                    item["id"],
                    item["dimension_code"],
                    item["code"],
                    item["title"],
                    item["axiom"],
                    item.get("explanation"),
                    item.get("worldly_example"),
                    item.get("spiritual_example"),
                    item.get("objectivity_statement"),
                    item.get("truth_property_primary"),
                    now,
                    now,
                ),
            )
            counts["principles"] += 1

        for item in _load_jsonl(seeds_dir / "truth_puzzles.seed.jsonl"):
            truth_property_tags = item.get("truth_property_tags")
            if isinstance(truth_property_tags, str):
                json.loads(truth_property_tags)
                truth_property_tags_json = truth_property_tags
            else:
                truth_property_tags_json = json.dumps(truth_property_tags or [], ensure_ascii=False)

            connection.execute(
                """
                INSERT INTO truth_puzzles (
                  id, dimension_code, principle_code, title, statement, misbelief,
                  truth_reframe, coach_prompt, tags, use_cases, source_doc,
                  embedding_text, truth_property_tags, verification_mode,
                  fact_layer, reality_layer, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                  truth_property_tags=excluded.truth_property_tags,
                  verification_mode=excluded.verification_mode,
                  fact_layer=excluded.fact_layer,
                  reality_layer=excluded.reality_layer,
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
                    truth_property_tags_json,
                    item.get("verification_mode") or "dialogue",
                    item.get("fact_layer"),
                    item.get("reality_layer"),
                    now,
                    now,
                ),
            )
            counts["puzzles"] += 1

        connection.commit()
    return counts


def _warn_on_non_dual_validation(principles: list[dict]) -> None:
    failed_principles = 0
    warning_count = 0
    for principle in principles:
        errors = validate_non_dual_axiom(principle)
        if not errors:
            continue
        failed_principles += 1
        warning_count += len(errors)
        for error in errors:
            print(f"  WARN [{principle.get('code', principle.get('id'))}]: {error}")

    warning_rate = failed_principles / max(len(principles), 1)
    if warning_rate > 0.20:
        raise ValueError(
            f"HARD FAIL: {warning_rate:.0%} of principles failed non-dual validation "
            "(threshold: 20%). Fix axiom quality before importing."
        )

    print(
        f"Seed validation: {len(principles)} principles, "
        f"{warning_count} warnings ({warning_rate:.0%} principles affected)"
    )


def _enhance_core_principle(item: dict) -> dict:
    enhanced = dict(item)
    dimension = enhanced.get("dimension_code", "truth")
    title = enhanced.get("title") or enhanced.get("code") or "this principle"
    axiom = enhanced.get("axiom") or ""

    enhanced.setdefault(
        "worldly_example",
        f"In lived situations, {title} appears as repeated observable patterns in choices and consequences.",
    )
    enhanced.setdefault(
        "spiritual_example",
        f"In consciousness, {title} appears as the inner pattern that shapes perception and response.",
    )
    enhanced.setdefault(
        "objectivity_statement",
        "This principle operates even if the person does not know, believe, or imagine it.",
    )
    enhanced.setdefault("truth_property_primary", _infer_primary_truth_property(dimension, title, axiom))
    return enhanced


def _infer_primary_truth_property(dimension: str, title: str, axiom: str) -> str:
    text = f"{dimension} {title} {axiom}".lower()
    if dimension in {"causality", "manifestation"} or any(token in text for token in ("因果", "重複", "pattern")):
        return "consistency"
    if dimension in {"cognition", "belief", "discernment"} or any(token in text for token in ("事實", "真相", "投射")):
        return "objectivity"
    if dimension in {"evolution", "suffering"} or any(token in text for token in ("看見", "覺察", "成長")):
        return "discoverability"
    if dimension in {"motive", "emotion"} or any(token in text for token in ("感受", "練習", "印證")):
        return "verifiability"
    if dimension in {"compassion", "relationship", "freedom"} or any(token in text for token in ("善", "美", "和諧", "慈悲")):
        return "plurality"
    return "discoverability"

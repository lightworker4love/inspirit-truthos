#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/truth-api"))

from app.db import get_db_path


PROPERTY_KEYWORDS = {
    "consistency": ("universal", "pattern", "gravity", "cause", "effect", "consequence", "love", "karma", "sow", "reap", "一致", "重複", "因果"),
    "objectivity": ("real", "reality", "appearance", "appears", "illusion", "belief", "misbelief", "imagine", "known", "unknown", "事實", "真相", "立場", "投射"),
    "discoverability": ("shadow", "discover", "uncover", "reveal", "insight", "awakening", "transform", "truth", "看見", "發現", "覺察", "轉化"),
    "verifiability": ("test", "experiment", "evidence", "experience", "practice", "confirm", "observe", "life", "測試", "實驗", "印證", "練習"),
    "plurality": ("beauty", "beautiful", "good", "goodness", "true", "virtue", "value", "harmony", "真", "善", "美", "價值", "和諧"),
}

AXIOM_KEYWORDS = ("axiom", "principle", "self-evident", "universal law", "always", "公理", "原則", "不辯自明")
TEXT_COLUMNS = ("title", "statement", "misbelief", "truth_reframe", "coach_prompt", "tags", "use_cases", "embedding_text", "fact_layer", "reality_layer")


def infer_tags(row: sqlite3.Row) -> list[str]:
    text = _row_text(row).lower()
    tags = [tag for tag, keywords in PROPERTY_KEYWORDS.items() if any(keyword in text for keyword in keywords)]
    if not tags:
        tags.append("discoverability")
    return tags


def infer_verification_mode(row: sqlite3.Row, tags: list[str]) -> str:
    text = _row_text(row).lower()
    if any(keyword in text for keyword in AXIOM_KEYWORDS):
        return "stillness"
    if "verifiability" in tags and any(keyword in text for keyword in ("evidence", "experiment", "confirm", "印證", "實驗")):
        return "evidence"
    return "dialogue"


def tag_database(db_path: Path) -> dict[str, Any]:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        columns = _table_columns(conn, "truth_puzzles")
        _require_columns(columns, {"truth_property_tags", "verification_mode"})

        rows = conn.execute("SELECT * FROM truth_puzzles").fetchall()
        tag_counts: Counter[str] = Counter()
        mode_counts: Counter[str] = Counter()

        for row in rows:
            tags = infer_tags(row)
            mode = infer_verification_mode(row, tags)
            conn.execute(
                """
                UPDATE truth_puzzles
                   SET truth_property_tags = ?,
                       verification_mode = ?
                 WHERE id = ?
                """,
                (json.dumps(tags, ensure_ascii=False), mode, row["id"]),
            )
            tag_counts.update(tags)
            mode_counts.update([mode])

    return {
        "database": str(db_path),
        "updated_rows": len(rows),
        "tag_counts": dict(sorted(tag_counts.items())),
        "verification_mode_counts": dict(sorted(mode_counts.items())),
    }


def print_report(report: dict[str, Any]) -> None:
    print("Truth Property Tag Distribution:")
    for tag, count in report["tag_counts"].items():
        print(f"  {tag}: {count}")
    print("\nVerification Mode Distribution:")
    for mode, count in report["verification_mode_counts"].items():
        print(f"  {mode}: {count}")
    total = max(report["updated_rows"], 1)
    dominant_tags = [(tag, count) for tag, count in report["tag_counts"].items() if count / total > 0.70]
    if dominant_tags:
        print("\nReview recommended: at least one tag covers more than 70% of puzzles.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Tag TruthOS puzzles with truth properties.")
    parser.add_argument("db_path", nargs="?", type=Path, help="Path to the SQLite database")
    parser.add_argument("--db", dest="db_option", type=Path, help="Path to the SQLite database")
    parser.add_argument("--report", action="store_true", help="Print human-readable distribution report")
    args = parser.parse_args()

    db_path = args.db_option or args.db_path or get_db_path()
    report = tag_database(db_path)
    if args.report:
        print_report(report)
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


def _row_text(row: sqlite3.Row) -> str:
    pieces = []
    keys = set(row.keys())
    for column in TEXT_COLUMNS:
        if column in keys and row[column] is not None:
            pieces.append(str(row[column]))
    return " ".join(pieces)


def _table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def _require_columns(columns: set[str], required: set[str]) -> None:
    missing = sorted(required - columns)
    if missing:
        raise RuntimeError(f"Missing required columns in truth_puzzles: {', '.join(missing)}")


if __name__ == "__main__":
    raise SystemExit(main())

"""
Daily SQLite -> CSV/Parquet export for Codex Data Analytics.
Outputs land in data/exports/.
Run: python -m jobs.export_analytics
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = Path(os.getenv("TRUTHOS_DB_PATH", str(REPO_ROOT / "data/truthos.db")))
EXPORT_DIR = Path(os.getenv("TRUTHOS_EXPORT_DIR", str(REPO_ROOT / "data/exports")))

EXPORT_SPECS = [
    {"name": "truthpuzzles", "candidates": ["truth_puzzles", "truthpuzzles"]},
    {"name": "belieflogs", "candidates": ["belief_logs", "belieflogs"]},
    {"name": "truthevals", "candidates": ["truth_evals", "truthevals"]},
    {"name": "soulmaps", "candidates": ["soulmaps"]},
    {"name": "blindspotarchives", "candidates": ["blindspotarchives", "blind_spot_archives"]},
    {"name": "casesummaries", "candidates": ["casesummaries", "case_summaries"]},
    {"name": "coreprinciples", "candidates": ["core_principles", "coreprinciples"]},
    {"name": "truthdimensions", "candidates": ["truth_dimensions", "truthdimensions"]},
]


def _load_first_available_table(conn: sqlite3.Connection, table_names: list[str]) -> tuple[pd.DataFrame, str]:
    last_error: Exception | None = None
    for table_name in table_names:
        try:
            return pd.read_sql(f"SELECT * FROM {table_name}", conn), table_name
        except Exception as exc:  # pragma: no cover - fallback chain depends on local schema
            last_error = exc
    if last_error is None:
        raise RuntimeError("No candidate tables provided")
    raise last_error


def export_all() -> dict[str, int]:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    summary: dict[str, int] = {}
    try:
        for spec in EXPORT_SPECS:
            export_name = spec["name"]
            try:
                df, source_table = _load_first_available_table(conn, spec["candidates"])
                csv_path = EXPORT_DIR / f"{export_name}_{today}.csv"
                df.to_csv(csv_path, index=False, encoding="utf-8")

                parquet_path = EXPORT_DIR / f"{export_name}_{today}.parquet"
                df.to_parquet(parquet_path, index=False)

                summary[export_name] = len(df)
                print(
                    f"[export_analytics] OK {export_name}: {len(df)} rows "
                    f"from {source_table} -> {csv_path.name}"
                )
            except Exception as exc:  # pragma: no cover - export should continue per table
                print(f"[export_analytics] ERR {export_name}: {exc}")
    finally:
        conn.close()

    manifest_path = EXPORT_DIR / f"manifest_{today}.json"
    manifest = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "db_path": str(DB_PATH),
        "tables": summary,
        "puzzle_source": "SQLite table `truthpuzzles`",
        "api_endpoint": "GET /api/truth/search?dimension=&tag=&limit=",
        "phase": "Phase 1 (1200 seed puzzles)",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[export_analytics] OK manifest -> {manifest_path.name}")
    return summary


if __name__ == "__main__":
    print(f"[export_analytics] Starting export {datetime.now(timezone.utc).isoformat()}")
    result = export_all()
    print(f"[export_analytics] Done. {sum(result.values())} total rows exported.")

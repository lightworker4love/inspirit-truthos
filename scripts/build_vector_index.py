from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/truth-api"))

from app.vector_index import build_vector_index, vector_index_exists


def main() -> int:
    if vector_index_exists():
        print("LanceDB index already exists at data/lancedb/truth_puzzles")
        return 0

    count, elapsed, built = build_vector_index()
    if built:
        print(f"Indexed {count} truth puzzles into LanceDB in {elapsed:.2f}s")
        return 0

    print("Skipped LanceDB build because no embedding provider is currently available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

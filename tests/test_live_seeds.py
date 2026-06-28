from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "apps/truth-api") not in sys.path:
    sys.path.insert(0, str(ROOT / "apps/truth-api"))

from packages.truth_schema.validators import validate_non_dual_axiom
from app.seed_loader import _enhance_core_principle


def _load_jsonl(path: Path) -> list[dict]:
    assert path.exists(), f"Seed file not found: {path}"
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def test_dimensions_seed_integrity():
    dimensions_file = ROOT / "data/seeds/dimensions.seed.jsonl"
    items = _load_jsonl(dimensions_file)
    assert len(items) > 0, "dimensions.seed.jsonl should not be empty"

    ids = set()
    codes = set()
    for index, item in enumerate(items, 1):
        # 欄位檢查
        assert "id" in item, f"Line {index}: Missing 'id'"
        assert "code" in item, f"Line {index}: Missing 'code'"
        assert "name_zh" in item, f"Line {index}: Missing 'name_zh'"
        assert "name_en" in item, f"Line {index}: Missing 'name_en'"

        # 唯一性檢查
        assert item["id"] not in ids, f"Line {index}: Duplicate id '{item['id']}'"
        assert item["code"] not in codes, f"Line {index}: Duplicate code '{item['code']}'"

        ids.add(item["id"])
        codes.add(item["code"])


def test_core_principles_seed_integrity():
    dimensions_file = ROOT / "data/seeds/dimensions.seed.jsonl"
    dimension_codes = {item["code"] for item in _load_jsonl(dimensions_file)}

    principles_file = ROOT / "data/seeds/core_principles.seed.jsonl"
    items = _load_jsonl(principles_file)
    assert len(items) > 0, "core_principles.seed.jsonl should not be empty"

    ids = set()
    codes = set()
    failed_principles = 0
    warning_count = 0

    for index, item in enumerate(items, 1):
        # 欄位檢查
        assert "id" in item, f"Line {index}: Missing 'id'"
        assert "dimension_code" in item, f"Line {index}: Missing 'dimension_code'"
        assert "code" in item, f"Line {index}: Missing 'code'"
        assert "title" in item, f"Line {index}: Missing 'title'"
        assert "axiom" in item, f"Line {index}: Missing 'axiom'"

        # 唯一性檢查
        assert item["id"] not in ids, f"Line {index}: Duplicate id '{item['id']}'"
        assert item["code"] not in codes, f"Line {index}: Duplicate code '{item['code']}'"

        # 外鍵檢查
        assert item["dimension_code"] in dimension_codes, (
            f"Line {index}: Invalid dimension_code '{item['dimension_code']}'. "
            f"Allowed codes: {dimension_codes}"
        )

        ids.add(item["id"])
        codes.add(item["code"])

        # non-dual validation 驗證
        enhanced = _enhance_core_principle(item)
        errors = validate_non_dual_axiom(enhanced)
        if errors:
            failed_principles += 1
            warning_count += len(errors)
            # 可在 test stdout 中顯示 warning，方便 debug
            print(f"WARN [{item['code']}]: {', '.join(errors)}")

    # 檢查警告率是否小於 20%
    warning_rate = failed_principles / len(items)
    assert warning_rate <= 0.20, (
        f"Non-dual validation failed rate too high: {warning_rate:.2%} "
        f"({failed_principles}/{len(items)} principles, threshold 20%)"
    )


def test_truth_puzzles_seed_integrity():
    dimensions_file = ROOT / "data/seeds/dimensions.seed.jsonl"
    dimension_codes = {item["code"] for item in _load_jsonl(dimensions_file)}

    principles_file = ROOT / "data/seeds/core_principles.seed.jsonl"
    principle_codes = {item["code"] for item in _load_jsonl(principles_file)}

    puzzles_file = ROOT / "data/seeds/truth_puzzles.seed.jsonl"
    items = _load_jsonl(puzzles_file)
    assert len(items) > 0, "truth_puzzles.seed.jsonl should not be empty"

    ids = set()
    for index, item in enumerate(items, 1):
        # 欄位檢查
        assert "id" in item, f"Line {index}: Missing 'id'"
        assert "dimension_code" in item, f"Line {index}: Missing 'dimension_code'"
        assert "principle_code" in item, f"Line {index}: Missing 'principle_code'"
        assert "title" in item, f"Line {index}: Missing 'title'"
        assert "statement" in item, f"Line {index}: Missing 'statement'"
        assert "source_doc" in item, f"Line {index}: Missing 'source_doc'"
        assert "embedding_text" in item, f"Line {index}: Missing 'embedding_text'"

        # 唯一性檢查
        assert item["id"] not in ids, f"Line {index}: Duplicate id '{item['id']}'"

        # 外鍵檢查
        assert item["dimension_code"] in dimension_codes, (
            f"Line {index}: Invalid dimension_code '{item['dimension_code']}'. "
            f"Allowed codes: {dimension_codes}"
        )
        assert item["principle_code"] in principle_codes, (
            f"Line {index}: Invalid principle_code '{item['principle_code']}'. "
            f"Allowed codes: {principle_codes}"
        )

        ids.add(item["id"])

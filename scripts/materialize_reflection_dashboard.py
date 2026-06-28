#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRUTH_API_ROOT = ROOT / "apps" / "truth-api"
VENV_PYTHON = ROOT / ".venv311" / "bin" / "python"
if str(TRUTH_API_ROOT) not in sys.path:
    sys.path.insert(0, str(TRUTH_API_ROOT))

try:
    from app.reflection_models import ReflectionMaterializeRequest
    from app.reflection_service import ReflectionWritebackService
except ModuleNotFoundError as exc:
    if exc.name == "pydantic" and VENV_PYTHON.exists() and Path(sys.executable) != VENV_PYTHON:
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__, *sys.argv[1:]])
    raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize TruthOS reflection dashboard projections.")
    parser.add_argument("--user-id", default=None)
    parser.add_argument("--tenant-id", default=None)
    parser.add_argument("--run-date", default=None)
    parser.add_argument("--mode", default="incremental")
    parser.add_argument("--rebuild-all", action="store_true")
    args = parser.parse_args()

    service = ReflectionWritebackService()
    response = service.materialize(
        ReflectionMaterializeRequest(
            user_id=args.user_id,
            tenant_id=args.tenant_id,
            run_date=args.run_date,
            mode=args.mode,
            rebuild_all=args.rebuild_all,
        )
    )
    print(json.dumps(response.model_dump(mode="json"), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

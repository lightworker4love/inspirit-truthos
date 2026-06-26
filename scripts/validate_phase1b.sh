#!/usr/bin/env bash
set -euo pipefail

echo "=== Phase 1B Repeatable Validation Script ==="
echo ""

# 1. Run local schema validations
echo "=> Running Schema Validation Tests (Minimal Payloads & Invalid Case)..."
docker exec inspirit-truthos-truth-api-1 python3 -c '
import sys, json, logging
from pathlib import Path
sys.path.insert(0, "/app/apps/truth-api")
from app.v2_validation import validate_artifact
from app.v2_schema_loader import get_supported_artifacts

logging.basicConfig(level=logging.ERROR)
TEST_PAYLOADS_DIR = Path("/app/minimal_test_payloads")

supported = get_supported_artifacts()
if not supported:
    print("❌ No schemas loaded!")
    sys.exit(1)

for name in supported:
    p = TEST_PAYLOADS_DIR / f"{name}.json"
    if p.exists():
        v, n, errs = validate_artifact(json.loads(p.read_text()), name)
        if v:
            print(f"✅ Validated minimal {name}")
        else:
            print(f"❌ Failed to validate minimal {name}: {errs}")
            sys.exit(1)

# Invalid payload test
invalid = {"invalid": "payload"}
v, n, errs = validate_artifact(invalid, "case_reflection")
if not v:
    print(f"✅ Correctly rejected invalid case_reflection")
else:
    print("❌ Incorrectly validated invalid case_reflection")
    sys.exit(1)
'

echo ""
# 2. Run Baseline V1 Query
echo "=> Testing Baseline V1 Query (No Dry Run)..."
HTTP_STATUS=$(curl -s -o /tmp/v1_out.json -w "%{http_code}" -X POST http://localhost:18000/api/truth/query \
  -H "Content-Type: application/json" -d '{"user_id": "test_v1", "message": "Baseline query test"}')
if [ "$HTTP_STATUS" != "200" ]; then
    echo "❌ Baseline V1 Query Failed. Status: $HTTP_STATUS"
    cat /tmp/v1_out.json
    exit 1
else
    echo "✅ Baseline V1 Query Succeeded."
fi

echo ""
# 3. Run Dry-Run=True Query
echo "=> Testing V2 Dry-Run Stub (dry_run: true)..."
HTTP_STATUS=$(curl -s -o /tmp/v2_out.json -w "%{http_code}" -X POST http://localhost:18000/api/truth/query \
  -H "Content-Type: application/json" -d '{"user_id": "test_v2", "message": "Dry-run query test", "dry_run": true}')
if [ "$HTTP_STATUS" != "200" ]; then
    echo "❌ Dry-Run Query Failed. Status: $HTTP_STATUS"
    cat /tmp/v2_out.json
    exit 1
else
    # Verify the stub payload is returned
    MODE=$(python3 -c "import sys, json; print(json.load(sys.stdin).get('mode', ''))" < /tmp/v2_out.json)
    if [ "$MODE" == "dry_run" ]; then
        echo "✅ Dry-Run Query Succeeded and returned correct mode."
    else
        echo "❌ Dry-Run Query returned unexpected payload mode: $MODE"
        cat /tmp/v2_out.json
        exit 1
    fi
fi

echo ""
echo "🎉 All Phase 1B validations passed!"

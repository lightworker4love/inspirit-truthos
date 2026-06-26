#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from datetime import datetime


APP_DIR = Path("/Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api")
REPORT_ROOT = Path("/Users/tongwei/.openclaw/reports")


CANDIDATES = [
    "README-dev.md",
    "README-prod.md",
    "README-ops-rhythm.md",
    "README-runbooks-index.md",
    "incident-checklist.md",
    "rotate-secrets.md",
    "daily-report.md.template",
    "scripts/backup-restore.sh",
    "scripts/healthcheck.sh",
    "scripts/ops-daily-check.sh",
    "scripts/ops-status.py",
    "scripts/export-audit-log.py",
    "scripts/export-runbook-manifest.py",
    "scripts/render-daily-report.py",
    "scripts/ops-weekly-summary.py",
    "scripts/ops-monthly-summary.py",
    "scripts/render-incident-postmortem.py",
    "scripts/password-reset-admin.py",
    "scripts/db-inspect.py",
    "scripts/reseed-case-demo.py",
    "launchd/ai.inspirit.ops-daily-check.plist",
    "launchd/ai.inspirit.ops-weekly-summary.plist",
    "launchd/ai.inspirit.ops-monthly-summary.plist",
    "docs/ops-architecture.md",
]


def classify(path: str) -> str:
    if path.startswith("scripts/"):
        return "script"
    if path.startswith("launchd/"):
        return "launchd"
    if path.startswith("docs/"):
        return "doc"
    if path.endswith(".md"):
        return "runbook"
    return "other"


def build_manifest():
    items = []
    for rel in CANDIDATES:
        p = APP_DIR / rel
        items.append({
            "path": rel,
            "abs_path": str(p),
            "exists": p.exists(),
            "type": classify(rel),
        })
    return {
        "generated_at": datetime.now().isoformat(),
        "app_dir": str(APP_DIR),
        "items": items,
    }


def write_json(manifest: dict, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def write_md(manifest: dict, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# truth-api Runbook Manifest")
    lines.append("")
    lines.append(f"- generated_at: {manifest['generated_at']}")
    lines.append(f"- app_dir: {manifest['app_dir']}")
    lines.append("")
    lines.append("| type | exists | path |")
    lines.append("|---|---|---|")
    for item in manifest["items"]:
        lines.append(f"| {item['type']} | {item['exists']} | {item['path']} |")
    output.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Export runbook manifest")
    parser.add_argument("--format", choices=["json", "md"], default="json")
    parser.add_argument("--output", default=str(REPORT_ROOT / "runbook-manifest.json"))
    args = parser.parse_args()

    manifest = build_manifest()
    output = Path(args.output)

    if args.format == "md":
        write_md(manifest, output)
    else:
        write_json(manifest, output)

    print(f"[ok] exported manifest to {output}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import os
import socket
from datetime import datetime
from pathlib import Path


REPORT_ROOT = Path("/Users/tongwei/.openclaw/reports")
POSTMORTEM_DIR = REPORT_ROOT / "incidents"


TEMPLATE = """# truth-api Incident Postmortem

- Incident ID: {incident_id}
- Date: {date}
- Host: {host}
- Operator: {operator}
- Severity: {severity}
- Status: {status}

## Summary

{summary}

## Impact

- User impact: {user_impact}
- Service impact: {service_impact}
- Systems involved: {systems_involved}

## Timeline

- Detected at: {detected_at}
- Mitigated at: {mitigated_at}
- Resolved at: {resolved_at}

## Root cause

{root_cause}

## Contributing factors

- {factor_1}
- {factor_2}
- {factor_3}

## Actions taken

1. {action_1}
2. {action_2}
3. {action_3}

## Recovery validation

- truth-api /health: {truth_api_health}
- OpenClaw /v1/models: {openclaw_health}
- login path checked: {login_checked}
- chat path checked: {chat_checked}

## Follow-up items

- {followup_1}
- {followup_2}
- {followup_3}

## Notes

{notes}
"""


def main():
    parser = argparse.ArgumentParser(description="Render incident postmortem markdown")
    parser.add_argument("--incident-id", required=True)
    parser.add_argument("--severity", default="SEV-2")
    parser.add_argument("--status", default="resolved")
    parser.add_argument("--summary", default="Describe the incident in 2-3 sentences.")
    parser.add_argument("--user-impact", default="Unknown")
    parser.add_argument("--service-impact", default="truth-api degraded")
    parser.add_argument("--systems-involved", default="truth-api, OpenClaw Gateway")
    parser.add_argument("--detected-at", default="")
    parser.add_argument("--mitigated-at", default="")
    parser.add_argument("--resolved-at", default="")
    parser.add_argument("--root-cause", default="Root cause not yet documented.")
    parser.add_argument("--factor-1", default="TBD")
    parser.add_argument("--factor-2", default="TBD")
    parser.add_argument("--factor-3", default="TBD")
    parser.add_argument("--action-1", default="Stabilized service boundary.")
    parser.add_argument("--action-2", default="Validated logs and health endpoints.")
    parser.add_argument("--action-3", default="Confirmed recovery with smoke test.")
    parser.add_argument("--truth-api-health", default="OK")
    parser.add_argument("--openclaw-health", default="OK")
    parser.add_argument("--login-checked", default="yes")
    parser.add_argument("--chat-checked", default="yes")
    parser.add_argument("--followup-1", default="Document guardrail or runbook improvement.")
    parser.add_argument("--followup-2", default="Review alerting or backup cadence.")
    parser.add_argument("--followup-3", default="Track repeat risk in weekly summary.")
    parser.add_argument("--notes", default="None.")
    parser.add_argument("--output", default="")

    args = parser.parse_args()

    POSTMORTEM_DIR.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = (
        Path(args.output)
        if args.output
        else POSTMORTEM_DIR / f"incident-{date_str}-{args.incident_id}.md"
    )

    content = TEMPLATE.format(
        incident_id=args.incident_id,
        date=date_str,
        host=socket.gethostname(),
        operator=os.getenv("USER", "unknown"),
        severity=args.severity,
        status=args.status,
        summary=args.summary,
        user_impact=args.user_impact,
        service_impact=args.service_impact,
        systems_involved=args.systems_involved,
        detected_at=args.detected_at or "TBD",
        mitigated_at=args.mitigated_at or "TBD",
        resolved_at=args.resolved_at or "TBD",
        root_cause=args.root_cause,
        factor_1=args.factor_1,
        factor_2=args.factor_2,
        factor_3=args.factor_3,
        action_1=args.action_1,
        action_2=args.action_2,
        action_3=args.action_3,
        truth_api_health=args.truth_api_health,
        openclaw_health=args.openclaw_health,
        login_checked=args.login_checked,
        chat_checked=args.chat_checked,
        followup_1=args.followup_1,
        followup_2=args.followup_2,
        followup_3=args.followup_3,
        notes=args.notes,
    )

    output_path.write_text(content, encoding="utf-8")
    print(f"[ok] rendered incident postmortem: {output_path}")


if __name__ == "__main__":
    main()

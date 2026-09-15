# Security Policy

## Reporting a Vulnerability

Please do not report security vulnerabilities through public GitHub issues.

Email the maintainers at:

- Email: security@inspirit.tw

Include the affected component and version or commit, reproduction steps, the
potential impact, and any suggested mitigation. Do not include secrets or real
private data in the report. The maintainers may move the report into a private
GitHub security advisory for coordinated investigation and disclosure.

## Response expectations

This project is maintained by a solo maintainer. We aim to:

- acknowledge a report within 3 business days;
- provide an initial assessment within 7 business days;
- share a status update at least every 14 days while a confirmed issue remains
  unresolved; and
- coordinate disclosure after a fix or mitigation is available.

These are response targets rather than guaranteed remediation deadlines. Fix
timing depends on severity, complexity, and release risk.

## Scope

This policy covers the TruthOS core repository, including API, frontend, bridge
code, scripts, and CI/CD workflows.

## Notes

Any public demo endpoints mentioned in this repository are for evaluation only,
may be rate-limited, and may be rotated or removed without notice.

Security fixes are applied to the current default branch and, when practical,
the latest supported release. Older snapshots may not receive backports.

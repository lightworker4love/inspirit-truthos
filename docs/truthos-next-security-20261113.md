# TruthOS Next.js security upgrade verification

> Historical initial review. The follow-up remediation and current acceptance scope are recorded in [truthos-security-acceptance-20261113.md](truthos-security-acceptance-20261113.md). The audit counts and no-commit/no-push status below describe the initial review, not the current candidate.

Date: 2026-11-13 (Asia/Taipei)
Baseline: master 7120e25018d54b5873ff5364fe1c17a9c7e149b6 (PR #57).
Scope: isolated Mac mini checkout; no commit, push, PR update, merge or production deployment.

## Decision

Do not merge PR #56 unchanged. Its 16.3.6 target fixes GHSA-vcvr-r3jv-pc5j but is affected by subsequent advisories. Prepare next and eslint-config-next 16.4.6 together. Current source has no next/og, ImageResponse, next/image, use cache or cacheComponents usage found by the focused source inspection; this does not establish production runtime exposure or absence of all attack paths.

Primary references:
- https://github.com/vercel/next.js/security/advisories/GHSA-vcvr-r3jv-pc5j
- https://github.com/vercel/next.js/security/advisories/GHSA-2464-fhr4-w9xw
- https://github.com/vercel/next.js/security/advisories/GHSA-673q-mjm6-r5xr
- https://github.com/vercel/next.js/releases/tag/v16.4.6

The image-optimization RCE advisory describes glibc Linux and sharp <0.35.5; the repository Dockerfile uses Alpine/musl. Version-range matching alone is not proof of exploitability. The candidate nevertheless updates sharp to 0.35.5 through Next's declared dependency.

## Changes

- Pin next and eslint-config-next to 16.4.6 and regenerate the npm v3 lockfile.
- Remove the Next PostCSS override at 8.5.10. Git history identifies its introduction in c836fe84a0de7d63011a9c0beab78f41ec497022 (audit-fix commit); no continuing requirement was found in the searched docs. The candidate uses upstream PostCSS 8.5.23.
- Keep React and React DOM at 19.2.4.
- Add a frontend job to TruthOS CI: clean install, lint, types, build, final Docker image build and standalone smoke.
- Add Dockerfile-specific ignores for host node_modules, .next, tsbuildinfo, Git and environment files. Without these ignores, a local Docker build reproduced Next 16.3.6 mixed with SWC 16.4.6 after COPY, failing with Missing field additionalRoots. With ignores, the rebuilt image uses Next 16.4.6 and succeeds.
- Add a standalone smoke script that runs inside the final image with --network none, verifies four routes, student branding, Hermes role and linked static assets. This is an HTTP/SSR smoke test; it does not exercise browser hydration or live backend writes.

## Observed verification

- npm ci --no-audit --no-fund: passed for the final lockfile.
- npm run lint: passed, including the smoke script.
- npx --no-install tsc --noEmit: passed.
- npm run build: passed on Mac mini Node v25.9.0; public API variables set to http://127.0.0.1:9 and Mixpanel token empty.
- Production Dockerfile build: passed after excluding host artifacts.
- Final Alpine standalone runtime: Node v20.20.2, Next 16.4.6.
- Offline final-image smoke: / (13 assets), /chat (14), /history (12), /soul-map (13) all passed with HTTP 200 and expected branding.
- sharp 0.35.5 native PNG conversion: passed (90-byte output for a synthetic 1x1 image).
- PR #57's four source files and deploy-railway.yml: unchanged against baseline.
- GitHub Actions execution of the new job: not performed; no remote writes authorized.
- Live backend chat, persistence and browser interaction: not performed; no production data accessed for testing.

## Audit and remaining gates

npm audit --omit=dev on the intermediate 16.3.6 tree reported 30 affected package entries (2 critical, 16 high, 11 moderate, 1 low). The final 16.4.6 tree reported 19 (1 critical, 8 high, 9 moderate, 1 low), with no next entry. These are package-tree reports, not counts of confirmed exploitable production vulnerabilities.

The remaining critical proxy-addr@2.0.7 is reached via shadcn@4.7.0 -> @modelcontextprotocol/sdk@1.29.0 -> express@5.2.1. Runtime-root resolution in the final standalone image could not resolve shadcn, proxy-addr, @modelcontextprotocol/sdk or source-map-js; this bounded observation does not prove absence from every nested or bundled path. The CLI is still declared as a production dependency and remains part of the install/build supply chain. Do not use npm audit fix --force or downgrade shadcn to the audit tool's suggested 1.0.0 without a separate review.

Before merge:
1. Review this exact diff and decide whether to supersede PR #56 with the tested candidate.
2. Run the new frontend CI on the final proposed integration SHA and review the existing backend jobs.
3. Triage or explicitly accept remaining dependency risk, especially shadcn's CLI tree; browser-test critical student flows against a non-production backend.
4. Verify that master has not advanced beyond the reviewed baseline; revalidate if it has.
5. Preserve the user's no-production-deployment boundary: deploy-railway.yml automatically deploys after a successful master-push CI, so merge must not be treated as deployment-free. No deployment settings were changed here.

Recovery: all edits are local to the isolated checkout. Preserve or discard only the reviewed task-owned paths after checking for concurrent changes. Do not reset another checkout or production system.

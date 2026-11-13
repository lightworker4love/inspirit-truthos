# TruthOS security acceptance — 2026-11-13

## Authorized release follow-up

The user subsequently authorized PR merge, production deployment and the remaining setuptools fix. setuptools is now pinned to 83.0.0 for truth-api and Hermes images. The Unicode MANIFEST.in exclusion regression passes on native Mac Python 3.11 and the Linux test container; all four browser/backend tests pass again.

The previous production workflow failed with Unauthorized while treating the existing Railway secret as an account token. The release workflow now verifies whether the existing credential is project-scoped or account/workspace-scoped, checks access to the exact project, records safe pre-deployment IDs, and exports only the appropriate CLI variable. A preflight_only input skips every deployment step. No credential value is printed or changed. Actual release steps wait for successful deployments matching DEPLOY_SHA rather than treating detached upload acceptance as completion.

Release gates: updated candidate CI must pass, Railway auth-only preflight must pass, then merge the reviewed candidate and observe master CI plus the automatic production workflow. Confirm service health and the deployed commit. The baseline IDs retained in workflow logs identify recovery targets; no unrelated environment, service, database or access-control change is included.

## Scope and baseline

Repository: lightworker4love/inspirit-truthos.
Baseline: master 7120e25018d54b5873ff5364fe1c17a9c7e149b6, including PR #57.
Candidate branch: security/next-acceptance-20261113.
This records local preparation and acceptance. The GitHub Actions run for the exact candidate SHA supplies remote CI evidence. No merge or production deployment is included.

## Remediation

- next and eslint-config-next are pinned together at 16.4.6, with matching SWC and sharp >=0.35.5.
- The obsolete Next PostCSS 8.5.10 override is removed.
- shadcn CLI is removed completely, including its vulnerable Express/MCP/registry/ts-morph dependency chain. It was only consumed through a CSS import. The original shadcn@4.7.0 stylesheet is preserved unchanged after an MIT notice in app/shadcn-tailwind.css. The npm tarball SHA-512 integrity was verified before extracting it; the provenance and license are in the file. Component generation is no longer supplied by an installed CLI; future generator use requires a separately reviewed tool invocation.
- Nonbreaking transitive updates resolve the other production advisories.
- The remaining development-only minimatch advisory GHSA-g3hv-75wg-m249 is addressed by a narrowly scoped @typescript-eslint/typescript-estree -> minimatch@11.0.8 override. Upstream typescript-estree@8.72.2 still requests minimatch ^10.2.2. This override crosses that transitive major and is covered by lint/types/build checks. It supports Node 20 or >=22; CI uses Node 22 and the final Docker image uses Node 20.20.2. Revisit the override when upstream adopts a fixed dependency.
- Both production-only and complete frontend npm audit reports have zero advisories at verification time. No audit suppression, force downgrade, or audit fix --force was used.

## Isolation and test coverage

- docker-compose.security-test.yml owns a separate project, has no host data mounts or credentials, and uses tmpfs for its test SQLite database.
- API, Hermes and frontend containers remain on an internal-only Docker network. A fixed-upstream gateway exposes only test ports bound to host loopback; it has no general-purpose proxy endpoint.
- CORS reads one explicit TRUTHOS_WEB_ORIGIN for this test environment. The production default remains https://truthos-web-production.up.railway.app; no wildcard was added.
- Test frontend Docker build arguments point only to 127.0.0.1 test endpoints and disable Mixpanel. Browser routing blocks and reports any non-loopback request.
- Actual Chromium tests pass on desktop and Pixel 7 viewports: missing-user redirect, student entry, Hermes greeting, real POST /chat, persisted soul-map readback, /soul-map and /history rendering, branding, overflow, no page errors, exact-origin CORS acceptance/rejection, and malformed payload 422.
- Test backends use existing deterministic Hermes/SQLite behavior. No paid model/gateway was configured or exercised. This is not a validation of production model quality or production identity/access controls.
- A direct socket probe from the API container confirmed external egress is blocked (ENETUNREACH).

## Local observations

- Clean npm ci: passed.
- npm audit (all dependencies): zero vulnerabilities.
- npm audit --omit=dev: zero vulnerabilities.
- ESLint and TypeScript checks: passed.
- Docker test images: built; all service health checks passed.
- Playwright: 4 tests passed (desktop 2, mobile 2), using the real test backend and synthetic users.
- Standalone/offline asset verification remains part of CI, along with the production Docker build.
- CI YAML, deployment isolation conditions and git diff --check: passed.

## Remote CI and deployment boundary

The user explicitly requested GitHub CI execution. Prepare a local commit and push only the candidate branch, then manually dispatch TruthOS CI on that branch. The workflow runs frontend audit/lint/types/build, offline standalone smoke, Chromium and real backend tests, plus the existing Python/full-stack jobs. Browser artifacts are retained for seven days.

The deployment workflow filters workflow_run to master and additionally requires a push-triggered upstream CI (or an explicit deployment workflow dispatch). A non-master TruthOS CI workflow_dispatch does not satisfy those gates. Do not dispatch Deploy to Railway. Do not merge PR #56.

Review the actual Actions conclusion for the exact commit before claiming remote acceptance. A passing audit is a point-in-time package database result, not proof of absence of every security defect or an authorization/penetration audit of the whole system.

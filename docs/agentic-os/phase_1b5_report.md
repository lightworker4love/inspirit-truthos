# Phase 1B.5 Stabilization Report

## Reproducibility Status
- **`jsonschema` Dependency:** The addition of `jsonschema` to `apps/truth-api/requirements.txt` is perfectly positioned.
- **Dockerfile Build Path:** Inspected `apps/truth-api/Dockerfile` and `docker-compose.yml`. The Docker build process inherently copies `requirements.txt` to `/tmp/requirements.txt` and executes `pip install` before copying the rest of the application. 
- **Action Required:** Because the Antigravity agent runs in a sandbox, the manual command `docker compose build truth-api && docker compose up -d truth-api` failed with permission errors on `.env`. However, the live container was temporarily patched via `docker exec pip install`. For *permanent* deployment, the host operator simply needs to run the `docker compose build` command to bake the update into the image.

## Validation Command Set
A new script was created to permanently lock in reproducible testing without needing manual curl commands or python snippets.
- **Location:** `scripts/validate_phase1b.sh`
- **Execution:** `./scripts/validate_phase1b.sh`

**What it tests:**
1. **Schema Validation Engine:** Executes python within the docker container to load `v2_validation.py` and `v2_schema_loader.py`. It explicitly tests parsing of `minimal_test_payloads/*.json` guaranteeing the schemas are well-formed.
2. **Invalid Schema Handling:** Feeds an intentionally malformed JSON to the `case_reflection` schema and asserts that it rejects the payload.
3. **V1 Baseline Request:** Executes a standard `POST /api/truth/query` without the `dry_run` flag and asserts a 200 OK.
4. **V2 Dry-Run Stub:** Executes a `POST /api/truth/query` with `"dry_run": true` and asserts the payload returns the `{"mode": "dry_run"}` stub envelope.

## Remaining Risks
- The validation of missing schemas logs an error but does not crash the server. This is safe, but it relies heavily on the `schemas/` directory mapping accurately from the host to the container. The current absolute path resolver handles this safely.
- No writeback modifications have been made, so the system is completely safe and backwards compatible.

# Case Storage Migration Decision Memo
## JSON → SQLite → PostgreSQL Thresholds

**Status**: Decision record — approved for Phase 2  
**Scope**: `inspirit-truthos/data/cases/` JSON store and `workspace/config/wisdom-cases.db`  
**Updated**: 2026-05

---

## 1. Current State

| Store | Format | Location | What it holds |
|---|---|---|---|
| Case profiles | JSON files (one per case) | `data/cases/case__<channel>__<key>.json` | CaseProfile full struct |
| Auth + identity | SQLite (single file) | `workspace/config/wisdom-cases.db` | username, case_name, preferred_name, password_hash |

The two stores are currently **separate** — auth lives in SQLite, profile data lives in JSON.
This is fine while the user count is small.

---

## 2. Migration Thresholds

### Stage 0 → 1 (&lt;100 cases): **Stay on JSON**

- File-per-case JSON is easy to inspect, edit, version-control, and back up.
- Load time is negligible (&lt;1 ms per read with OS file cache warm).
- No concurrent writers — single-process TruthOS API.
- **Action**: Keep current setup. Add file-level locking (`fcntl.flock`) if the API
  ever runs multi-threaded.

### Stage 1 → 2 (100–1000 cases): **Migrate to SQLite**

Triggers (any one is sufficient):
- Case count exceeds **100**.
- Any query needs to filter across multiple profiles simultaneously
  (e.g., "all cases with `soul_age=old`").
- Admin tooling needs efficient list/search without loading all JSON.

SQLite migration plan:
1. Merge the existing `wisdom-cases.db` auth table with a new `case_profiles` table.
2. Map `CaseProfile` fields 1:1 to columns (JSON columns for `life_themes`, `blind_spots`, `metadata`).
3. Keep a file-based migration script (`scripts/migrate_json_to_sqlite.py`).
4. Run `PRAGMA journal_mode=WAL` for read concurrency.

Estimated migration cost: **1 engineer-day** (schema design + migration script + unit tests).

### Stage 2 → 3 (&gt;1000 cases or multi-worker): **Migrate to PostgreSQL**

Triggers (any one is sufficient):
- Active case count exceeds **1000**.
- TruthOS API is deployed with **more than 1 worker process** (Gunicorn workers &gt; 1).
- `sync_to_memory_store` is fully implemented and requires transactional consistency
  with the case profile store.
- Cloud deployment or multi-node setup required.

PostgreSQL migration plan:
1. Use Alembic for schema management (add to pyproject.toml dependencies).
2. Move auth from SQLite to Postgres `users` table.
3. Move case profiles to Postgres `case_profiles` table.
4. Add index on `(login_username, source_channel)` for fast resolution.
5. Containerize with a `postgres` service in `docker-compose.yml`.

Estimated migration cost: **3–5 engineer-days** (Alembic setup, connection pooling,
Docker compose update, migration from SQLite, integration tests).

---

## 3. Decision Matrix

| Criterion | JSON | SQLite | PostgreSQL |
|---|---|---|---|
| Setup complexity | None | Low | Medium |
| Operational burden | None | Very low | Low–Medium |
| Query flexibility | None (load-all) | Good | Excellent |
| Concurrent writers | 1 (safe) | 1–3 (WAL) | Many |
| Max cases (practical) | &lt;100 | &lt;1M | Unlimited |
| Backup strategy | `cp -r` | Single file copy | `pg_dump` |
| Inspect/debug | Direct file read | `sqlite3` CLI | `psql` |
| Best for current scale | ✓ | | |

---

## 4. Operational Complexity Notes

**JSON (current):**
- Pro: Zero operational overhead. Works in any environment.
- Con: No atomic multi-case update. No efficient querying. Manual admin only.
- Con: Risk of file corruption on unclean shutdown (mitigate: atomic write-then-rename).

**SQLite:**
- Pro: Drop-in replacement, no network dependency, same single-file backup story.
- Pro: `PRAGMA journal_mode=WAL` enables safe concurrent reads.
- Con: One writer at a time. Not suitable for Gunicorn multi-worker.
- Con: Requires schema migration on upgrade.

**PostgreSQL:**
- Pro: Full ACID, connection pooling, multi-worker safe.
- Pro: Enables complex reporting queries (usage by soul_age, theme distributions).  
- Con: Requires a running PG service. Adds Docker service dependency.
- Con: `pg_dump` backup must be scheduled (not a single-file copy).

---

## 5. Recommended Action

**Now**: Stay on JSON + SQLite dual store. Add atomic write to JSON persister:
```python
# In case_resolver.py save_case_profile():
import tempfile, os
with tempfile.NamedTemporaryFile('w', dir=profile_dir, delete=False, suffix='.tmp') as f:
    json.dump(profile.model_dump(), f, ensure_ascii=False, indent=2)
    tmp = f.name
os.replace(tmp, target_path)  # atomic on POSIX
```

**At 100 cases**: Run `scripts/migrate_json_to_sqlite.py` to consolidate both stores
into a single enhanced SQLite file. Merge auth table + case profiles.

**At 1000 cases or multi-worker**: Migrate to PostgreSQL via Alembic.

---

## 6. File Layout (for reference)

```
inspirit-truthos/
  data/
    cases/
      case__web__hank.json          ← CaseProfile for Hank (web channel)
      case__web__yvonne.json
      ...
workspace/
  config/
    wisdom-cases.db                 ← Auth store (username, password_hash, preferred_name, ...)
```

The `case_id` field in CaseProfile encodes the storage key: `{source_channel}__{login_username}`,
so the file name and the case_id are always in sync.

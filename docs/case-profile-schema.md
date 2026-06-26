# Case Profile Schema

## Current Schema

`CaseProfile` is the lightweight case-memory record stored in JSON during Phase 1.x.

Current fields:

- `schema_version: int = 1`
- `case_id: str`
- `login_username: str | None`
- `preferred_name: str | None`
- `display_name: str | None`
- `aliases: list[str]`
- `source_channel: str | None`
- `memory_namespace: str`
- `soul_age: str | None`
- `life_themes: list[str]`
- `blind_spots: list[str]`
- `last_session_insight: str | None`
- `first_seen_at: datetime | None`
- `last_seen_at: datetime | None`
- `metadata: dict[str, Any]`

## Versioning

- `schema_version = 1` is now explicit on every new profile.
- Existing JSON records without `schema_version` are still readable because the field defaults to `1`.
- Phase 1.5 only writes back these mutable blueprint fields:
  - `last_session_insight`
  - `life_themes`
  - `blind_spots`

Identity fields are preserved during blueprint updates.

`soul_age` policy in Phase 1.5:

- advisory only
- guarded by eligibility thresholds
- experimental
- not definitive truth and not a public-facing conclusion

## Migration Strategy

Short term:

- continue reading JSON case files from `data/cases`
- default missing `schema_version` to `1`
- keep migrations additive and backwards compatible

Medium term:

- add a migration runner that upgrades JSON records in place or exports them
- introduce schema-specific transform functions, for example `v1 -> v2`
- keep case identity resolution independent from storage engine choice

## JSON Store -> SQLite/Postgres Path

Recommended path:

1. JSON store remains the bootstrap source of truth for Phase 1.x.
2. Add a SQLite projection for indexed lookup, audit, and write coordination.
3. Move to Postgres when multi-writer coordination, observability, and relational joins become necessary.
4. Keep `memory_namespace` stable so mem0/Qdrant sync does not need case ID remapping.

## Guardrails

- never infer or persist `soul_age` without explicit eligibility
- never present `soul_age` as a strong external-facing narrative
- never let schema migration change `case_id` or `memory_namespace`
- never let blueprint writeback overwrite `preferred_name`

# hermes-truthos-bridge

Drop-in integration package connecting Hermes Agent to TruthOS.

The importable Python package is `packages.hermes_truthos_bridge`.
This directory preserves the Sprint 009 package name used in the deployment brief.

## Install

```bash
pip install httpx
```

## Usage (async Hermes)

```python
from packages.hermes_truthos_bridge import TruthOSHook

hook = TruthOSHook(base_url="http://localhost:8000")

truth_ctx = await hook.on_message(user_id, session_id, user_message)
hermes_response = await your_existing_handler(user_message)
enriched = hook.enrich_response(hermes_response, truth_ctx)
```

## Fire-and-forget hook

```python
import asyncio
from packages.hermes_truthos_bridge import TruthOSHook

truthos_hook = TruthOSHook(base_url="http://localhost:8000")

async def _fire_truthos(user_id, session_id, message):
    await truthos_hook.on_message(user_id, session_id, message)

asyncio.ensure_future(_fire_truthos(user_id, session_id, user_message))
```

## Soul context at session start

```python
soul_ctx = await truthos_hook.get_soul_context(user_id)
if soul_ctx:
    system_prompt_additions = f"""
[Soul Context]
Evolution Stage: {soul_ctx['evolution_stage']}
Active Patterns: {", ".join(soul_ctx['active_patterns'])}
Active Lessons: {len(soul_ctx['active_lessons'])} in progress
"""
```

## Safety guarantee

- TruthOS timeout = 3 seconds
- `TRUTHOS_BASE_URL` can override the default `http://localhost:8000`
- All exceptions are caught; Hermes continues if TruthOS is down
- Fire-and-enrich pattern keeps TruthOS additive, not blocking

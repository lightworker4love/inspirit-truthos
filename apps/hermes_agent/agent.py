from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional

from packages.hermes_truthos_bridge import TruthOSHook


logger = logging.getLogger("hermes.agent")
hook = TruthOSHook(base_url=os.getenv("TRUTHOS_BASE_URL", "http://localhost:8000"))


async def handle_message(
    user_id: str,
    session_id: str,
    message: str,
    context: Optional[dict] = None,
) -> dict:
    truth_task = asyncio.ensure_future(
        hook.on_message(user_id, session_id, message, context)
    )
    hermes_response = f"[Hermes response to: {message}]"
    truth_ctx = None
    try:
        truth_ctx = await asyncio.wait_for(asyncio.shield(truth_task), timeout=2.0)
    except asyncio.TimeoutError:
        logger.warning(
            "truth_layer_degraded | session_id=%s error=%s",
            session_id,
            "timeout",
        )
        logger.info("TruthOS still processing; returning base response")
        truth_ctx = {"_truth_degraded": True, "_truth_degraded_reason": "timeout"}
    return hook.enrich_response(hermes_response, truth_ctx)


async def start_session(user_id: str) -> dict:
    soul_ctx = await hook.get_soul_context(user_id)
    if soul_ctx:
        logger.info(
            "Session start | user=%s | stage=%s | patterns=%s",
            user_id,
            soul_ctx.get("evolution_stage"),
            len(soul_ctx.get("active_patterns", [])),
        )
    return soul_ctx or {}

from __future__ import annotations

import asyncio
from typing import Optional

from .hermes_hook import TruthOSHook


truthos_hook = TruthOSHook()


async def fire_truthos_for_message(
    user_id: str,
    session_id: str,
    user_message: str,
    context: Optional[dict] = None,
) -> None:
    await truthos_hook.on_message(user_id, session_id, user_message, context)


def schedule_truthos_for_message(
    user_id: str,
    session_id: str,
    user_message: str,
    context: Optional[dict] = None,
) -> None:
    asyncio.ensure_future(
        fire_truthos_for_message(user_id, session_id, user_message, context)
    )

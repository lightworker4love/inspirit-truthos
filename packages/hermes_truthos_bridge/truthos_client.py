from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional

import httpx


logger = logging.getLogger("hermes.truthos")

TRUTHOS_BASE_URL = os.getenv("TRUTHOS_BASE_URL", "http://localhost:8000")
TRUTHOS_TIMEOUT = 3.0


class TruthOSClient:
    """Async TruthOS client that never raises into Hermes."""

    def __init__(self, base_url: str = TRUTHOS_BASE_URL, timeout: float = TRUTHOS_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def query(
        self,
        user_message: str,
        user_id: str,
        session_id: str,
        context: Optional[dict] = None,
    ) -> Optional[dict]:
        payload = {
            "message": user_message,
            "query": user_message,
            "userid": user_id,
            "sessionid": session_id,
            "user_id": user_id,
            "session_id": session_id,
            "context": context or {},
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/truth/query", json=payload)
            if response.status_code == 200:
                result = response.json()
                hard_case = bool(
                    result.get("hard_case_flag") or result.get("is_hard_case")
                )
                logger.info("TruthOS query ok | user=%s | hard_case=%s", user_id, hard_case)
                return result
            logger.warning("TruthOS returned %s for user=%s", response.status_code, user_id)
            return None
        except httpx.TimeoutException:
            logger.warning("TruthOS timeout for user=%s; continuing without truth layer", user_id)
            return None
        except Exception as exc:
            logger.error("TruthOS unavailable: %s; Hermes continues unaffected", exc)
            return None

    async def get_soul_map(self, user_id: str) -> Optional[dict]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/soul-map/{user_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

    def query_sync(
        self,
        user_message: str,
        user_id: str,
        session_id: str,
        context: Optional[dict] = None,
    ) -> Optional[dict]:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.query(user_message, user_id, session_id, context))

        if loop.is_running():
            asyncio.ensure_future(self.query(user_message, user_id, session_id, context))
            return None
        return loop.run_until_complete(self.query(user_message, user_id, session_id, context))


truthos = TruthOSClient()

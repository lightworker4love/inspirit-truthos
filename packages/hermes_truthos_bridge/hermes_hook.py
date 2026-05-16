from __future__ import annotations

import asyncio
import logging
from typing import Optional

from .truthos_client import TruthOSClient


logger = logging.getLogger("hermes.hook")


class TruthOSHook:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.client = TruthOSClient(base_url=base_url)

    async def on_message(
        self,
        user_id: str,
        session_id: str,
        message: str,
        context: Optional[dict] = None,
    ) -> Optional[dict]:
        return await self.client.query(
            user_message=message,
            user_id=user_id,
            session_id=session_id,
            context=context,
        )

    def fire_and_forget(
        self,
        user_id: str,
        session_id: str,
        message: str,
        context: Optional[dict] = None,
    ) -> None:
        asyncio.ensure_future(self.on_message(user_id, session_id, message, context))

    def enrich_response(self, hermes_response: str, truth_context: Optional[dict]) -> dict:
        result = {
            "response": hermes_response,
            "truth_layer": None,
            "soul_map_updated": False,
            "guidance_overlay": None,
        }

        if not truth_context:
            return result

        truth_map = truth_context.get("truth_map", {})
        truth_claim = truth_map.get("truth_claim", {}) if isinstance(truth_map, dict) else {}
        result["truth_layer"] = {
            "verified": truth_map.get("verified_truth", bool(truth_claim)),
            "score": truth_map.get("truth_score", 0.0),
            "properties": truth_map.get("truth_properties", []),
            "map": truth_map,
        }
        result["soul_map_updated"] = bool(
            truth_context.get("soul_map_updated")
            or truth_context.get("writeback", {}).get("soul_map_changes")
        )
        result["is_hard_case"] = bool(
            truth_context.get("is_hard_case") or truth_context.get("hard_case_flag")
        )

        relevant = truth_context.get("relevant_principles") or truth_context.get("principles") or []
        if relevant:
            result["guidance_overlay"] = truth_context.get("guidance") or truth_context.get(
                "coach_question"
            )

        return result

    async def get_soul_context(self, user_id: str) -> Optional[dict]:
        soul_map = await self.client.get_soul_map(user_id)
        if not soul_map:
            return None

        blind_spots = soul_map.get("blind_spots") or soul_map.get("top_blind_spots") or []
        return {
            "evolution_stage": soul_map.get("evolution_stage", "awakening"),
            "active_patterns": [
                pattern.get("pattern")
                or pattern.get("description")
                or pattern.get("label")
                or pattern.get("id")
                for pattern in soul_map.get("recurring_patterns", [])[:3]
            ],
            "active_blind_spots": [
                blind_spot.get("title")
                for blind_spot in blind_spots
                if (blind_spot.get("resolution_status") or blind_spot.get("resolutionstatus") or "active")
                == "active"
            ][:2],
            "active_lessons": soul_map.get("active_lessons", [])[:3],
        }

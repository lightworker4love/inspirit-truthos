from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.case_models import CaseContext


class PromptBuilder:
    """
    Minimal prompt builder for case-context injection.

    Phase 1.5 keeps this intentionally small: it only serialises verified case
    context so downstream model prompts can address the user correctly without
    fabricating additional identity or blueprint fields.
    """

    def build_case_context_message(self, case_ctx: "CaseContext") -> dict[str, str]:
        lines: list[str] = [
            "## Current Case Context",
            f"Address as: {case_ctx.address_as}",
            f"Case ID: {case_ctx.case_id}",
        ]

        if case_ctx.source_channel:
            lines.append(f"Source channel: {case_ctx.source_channel}")
        if case_ctx.last_session_insight:
            lines.append(f"Last session insight: {case_ctx.last_session_insight}")
        if case_ctx.has_life_themes and case_ctx.life_themes_summary:
            lines.append(f"Life themes: {case_ctx.life_themes_summary}")
        if case_ctx.has_blind_spots and case_ctx.blind_spots_summary:
            lines.append(f"Blind spots: {case_ctx.blind_spots_summary}")

        lines.append(
            "Instruction: use the verified address_as value in replies; never let a workspace default override it."
        )
        return {
            "role": "system",
            "name": "case_context",
            "content": "\n".join(lines),
        }

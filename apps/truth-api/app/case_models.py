"""
Case Profile data models for the iN SPiRiT platform.

Every authenticated login identity corresponds to a CaseProfile.
These models are intentionally forward-compatible: spiritual/soul-age fields
are present but nullable, to be populated by future analysis services.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Core domain models
# ---------------------------------------------------------------------------

class CaseProfile(BaseModel):
    """
    Represents a single individual (case) in the in spirit platform.

    The `memory_namespace` drives mem0 / vector-store isolation.
    All spiritual fields (soul_age, life_themes, blind_spots) are nullable
    and must never be fabricated — only set when evidence exists.
    """

    schema_version: int = Field(1, description="CaseProfile schema version for future migrations")
    case_id: str = Field(..., description="Stable, globally unique case identifier, e.g. 'case:web:hank'")
    login_username: str | None = Field(None, description="Raw login username from auth layer")
    preferred_name: str | None = Field(None, description="How the AI should address this person (highest priority)")
    display_name: str | None = Field(None, description="Display / case name from admin panel")
    aliases: list[str] = Field(default_factory=list, description="Alternative usernames or names for this person")
    source_channel: str | None = Field(None, description="Entry channel, e.g. 'web', 'line', 'api'")
    memory_namespace: str = Field(..., description="Namespace for mem0/vector memory isolation, e.g. 'cases/web/hank'")

    # --- Spiritual / life blueprint fields (Phase 2) ---
    soul_age: str | None = Field(
        None,
        description=(
            "Advisory-only soul age classification (experimental, guarded, non-definitive)"
        ),
    )
    life_themes: list[str] = Field(default_factory=list, description="Core life themes extracted from sessions")
    blind_spots: list[str] = Field(default_factory=list, description="Recurring blind spots observed across sessions")
    last_session_insight: str | None = Field(None, description="Key insight from most recent session")

    # --- Timestamps ---
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None

    # --- Extensible metadata ---
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def effective_name(self) -> str:
        """
        Name resolution priority (highest → lowest):
        1. preferred_name (explicitly set in case profile)
        2. login_username
        3. display_name
        4. fallback
        """
        return self.preferred_name or self.login_username or self.display_name or "你"

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class CaseContext(BaseModel):
    """
    Distilled runtime context passed to PromptBuilder / reasoning layer.
    This is what the model actually sees — keep it compact and truthful.
    """

    case_id: str
    address_as: str = Field(..., description="The name to use when addressing this person in responses")
    source_channel: str | None = None
    memory_namespace: str
    has_life_themes: bool = False
    life_themes_summary: str | None = None
    has_blind_spots: bool = False
    blind_spots_summary: str | None = None
    last_session_insight: str | None = None
    is_new_case: bool = Field(False, description="True if this case was just created (no prior history)")

    @classmethod
    def from_profile(cls, profile: CaseProfile, *, is_new: bool = False) -> "CaseContext":
        life_themes_summary = (
            "、".join(profile.life_themes) if profile.life_themes else None
        )
        blind_spots_summary = (
            "、".join(profile.blind_spots) if profile.blind_spots else None
        )
        return cls(
            case_id=profile.case_id,
            address_as=profile.effective_name,
            source_channel=profile.source_channel,
            memory_namespace=profile.memory_namespace,
            has_life_themes=bool(profile.life_themes),
            life_themes_summary=life_themes_summary,
            has_blind_spots=bool(profile.blind_spots),
            blind_spots_summary=blind_spots_summary,
            last_session_insight=profile.last_session_insight,
            is_new_case=is_new,
        )


class CaseResolutionInput(BaseModel):
    """
    Input to CaseResolver — collects all available identity signals from the request.
    """

    login_username: str | None = Field(None, description="Username from HTTP Basic Auth or session")
    preferred_name: str | None = Field(None, description="Explicit preferred name from request or session metadata")
    display_name: str | None = Field(None, description="Case/display name from wisdom proxy or admin panel")
    source_channel: str | None = Field(None, description="e.g. 'web', 'api', 'line'")
    external_user_id: str | None = Field(None, description="Platform-specific user ID (e.g. lpm_kernel user_id)")
    session_id: str | None = None
    workspace_default_name: str | None = Field(
        None,
        description="Fallback name from USER.md or workspace defaults — lowest priority",
    )

    def stable_key(self) -> str:
        """
        Derive a stable, lowercased key used as the base for case_id and namespace.
        Prefers login_username, falls back to external_user_id.
        """
        raw = (
            self.login_username
            or self.external_user_id
            or "anonymous"
        )
        # Normalise: lowercase, strip whitespace, replace spaces with hyphens
        return raw.strip().lower().replace(" ", "-")

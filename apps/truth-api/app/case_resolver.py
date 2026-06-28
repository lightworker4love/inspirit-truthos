"""
CaseResolver — resolves a login identity to a CaseProfile at request time.

Responsibilities:
  1. Accept a CaseResolutionInput (all available identity signals).
  2. Derive a stable case_id and memory_namespace.
  3. Load an existing CaseProfile from the lightweight store (JSON files).
  4. If not found, create a minimal CaseProfile.
  5. Apply name resolution priority rules.
  6. Update last_seen_at and persist.
  7. Return a CaseContext ready for PromptBuilder / reasoning.

Name resolution priority (highest → lowest):
  a. preferred_name from request / session metadata
  b. preferred_name already set in the stored CaseProfile
  c. login_username
  d. display_name (case admin panel name)
  e. workspace_default_name (USER.md fallback — lowest, never overrides above)
  f. Generic fallback "你"

Storage:
  Phase 1 uses lightweight JSON files per case under CASE_STORE_DIR.
  Each file is named by case_id (colon → double-underscore for filesystem safety).
  Phase 2 should migrate to a proper DB or vector-store sidecar.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from app.case_models import CaseContext, CaseProfile, CaseResolutionInput

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Storage configuration
# ---------------------------------------------------------------------------

# Default store: alongside this file's package root, under data/cases/
_DEFAULT_STORE = Path(__file__).resolve().parent.parent.parent.parent / "data" / "cases"
CASE_STORE_DIR = Path(os.getenv("CASE_STORE_DIR", str(_DEFAULT_STORE)))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _case_id(channel: str, key: str) -> str:
    """Build a canonical case_id. Example: 'case:web:hank'"""
    return f"case:{channel}:{key}"


def _memory_namespace(channel: str, key: str) -> str:
    """Build the mem0 / vector-store namespace. Example: 'cases/web/hank'"""
    return f"cases/{channel}/{key}"


def _profile_path(case_id: str) -> Path:
    """Map case_id to a filesystem path (colons → double underscore)."""
    safe_name = case_id.replace(":", "__") + ".json"
    return CASE_STORE_DIR / safe_name


def _load_profile(case_id: str) -> CaseProfile | None:
    path = _profile_path(case_id)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return CaseProfile(**data)
    except Exception as exc:
        logger.warning("Failed to load case profile %s: %s", case_id, exc)
        return None


def _save_profile(profile: CaseProfile) -> None:
    CASE_STORE_DIR.mkdir(parents=True, exist_ok=True)
    path = _profile_path(profile.case_id)
    try:
        path.write_text(
            profile.model_dump_json(indent=2),
            encoding="utf-8",
        )
    except Exception as exc:
        logger.error("Failed to save case profile %s: %s", profile.case_id, exc)


def load_case_profile(case_id: str) -> CaseProfile | None:
    """Public wrapper used by post-response blueprint updates and tests."""
    return _load_profile(case_id)


def save_case_profile(profile: CaseProfile) -> None:
    """Public wrapper used by post-response blueprint updates and tests."""
    _save_profile(profile)


def _resolve_preferred_name(
    *,
    request_preferred_name: str | None,
    stored_preferred_name: str | None,
    login_username: str | None,
    display_name: str | None,
    workspace_default_name: str | None,
) -> str | None:
    """
    Apply name resolution priority rules.
    Returns the first non-empty value found down the chain.
    workspace_default_name (USER.md) is the lowest priority.
    """
    for candidate in (
        request_preferred_name,
        stored_preferred_name,
        login_username,
        display_name,
        workspace_default_name,
    ):
        if candidate and candidate.strip():
            return candidate.strip()
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class CaseResolver:
    """
    Resolves a login identity to a CaseProfile and returns a CaseContext.

    Usage::

        resolver = CaseResolver()
        ctx = resolver.resolve(CaseResolutionInput(
            login_username="Hank",
            source_channel="web",
        ))
        # ctx.address_as == "Hank"
    """

    def resolve(self, inp: CaseResolutionInput) -> tuple[CaseContext, bool]:
        """
        Resolve a request to a CaseContext.

        Returns (CaseContext, is_new_case) where is_new_case is True if
        this is the first time we've seen this identity.
        """
        channel = (inp.source_channel or "web").lower().strip()
        key = inp.stable_key()
        case_id = _case_id(channel, key)
        namespace = _memory_namespace(channel, key)

        logger.debug(
            "CaseResolver.resolve: channel=%s key=%s case_id=%s",
            channel, key, case_id,
        )

        stored = _load_profile(case_id)
        is_new = stored is None

        if is_new:
            profile = self._create_minimal_profile(
                case_id=case_id,
                namespace=namespace,
                inp=inp,
            )
            logger.info("CaseResolver: created new case profile %s", case_id)
        else:
            profile = self._update_existing_profile(stored, inp)
            logger.debug("CaseResolver: loaded existing case profile %s", case_id)

        _save_profile(profile)
        ctx = CaseContext.from_profile(profile, is_new=is_new)

        logger.info(
            "CaseResolver: resolved %s → address_as=%r (channel=%s, new=%s)",
            case_id, ctx.address_as, channel, is_new,
        )
        return ctx, is_new

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _create_minimal_profile(
        self,
        *,
        case_id: str,
        namespace: str,
        inp: CaseResolutionInput,
    ) -> CaseProfile:
        now = datetime.now(tz=timezone.utc)
        preferred = _resolve_preferred_name(
            request_preferred_name=inp.preferred_name,
            stored_preferred_name=None,
            login_username=inp.login_username,
            display_name=inp.display_name,
            workspace_default_name=inp.workspace_default_name,
        )
        return CaseProfile(
            case_id=case_id,
            login_username=inp.login_username,
            preferred_name=preferred,
            display_name=inp.display_name,
            aliases=[],
            source_channel=inp.source_channel,
            memory_namespace=namespace,
            first_seen_at=now,
            last_seen_at=now,
        )

    def _update_existing_profile(
        self,
        stored: CaseProfile,
        inp: CaseResolutionInput,
    ) -> CaseProfile:
        """
        Merge incoming request signals with the stored profile.
        Only update preferred_name if a higher-priority signal is present in the request.
        Never downgrade to workspace_default_name if a better name is already stored.
        """
        # Merge preferred name: request > stored > login_username > display_name
        # workspace_default_name only if absolutely nothing else exists
        new_preferred = _resolve_preferred_name(
            request_preferred_name=inp.preferred_name,
            stored_preferred_name=stored.preferred_name,
            login_username=inp.login_username,
            display_name=inp.display_name or stored.display_name,
            workspace_default_name=inp.workspace_default_name,
        )

        return stored.model_copy(
            update={
                "login_username": inp.login_username or stored.login_username,
                "preferred_name": new_preferred,
                "display_name": inp.display_name or stored.display_name,
                "source_channel": inp.source_channel or stored.source_channel,
                "last_seen_at": datetime.now(tz=timezone.utc),
            }
        )


# ---------------------------------------------------------------------------
# Module-level singleton (import and reuse across requests)
# ---------------------------------------------------------------------------

_default_resolver: CaseResolver | None = None


def get_case_resolver() -> CaseResolver:
    """Return the module-level CaseResolver singleton."""
    global _default_resolver
    if _default_resolver is None:
        _default_resolver = CaseResolver()
    return _default_resolver


def resolve_case(inp: CaseResolutionInput) -> CaseContext:
    """Convenience wrapper — resolves and returns CaseContext only."""
    ctx, _ = get_case_resolver().resolve(inp)
    return ctx

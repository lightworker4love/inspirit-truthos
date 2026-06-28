"""
memory_types.py
Phase 1/2 scaffolding — typed data contracts for the memory integration layer.

These types define the interface between chat_routes <-> memory_service <->
memory_clients.  They carry no business logic.  All fields are typed and
validated so that downstream callers cannot accidentally pass unsanitized
client-supplied values into wire calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional


# Canonical scope values.  Matches MEMORY_ALLOWED_SCOPES env contract.
MemoryScopeValue = Literal["default", "none", "session", "experiment"]


@dataclass(frozen=True)
class MemoryReadRequest:
    """Inputs required to retrieve memory context before prompt assembly."""

    user_id: str        # MUST come from auth context, never from client payload
    thread_id: str
    query: str          # typically the user's current message
    scope: MemoryScopeValue
    top_k: int = 5
    max_chars: int = 2400


@dataclass
class MemoryReadResult:
    """Result returned by memory_service.retrieve()."""

    memories: list[str] = field(default_factory=list)
    scope_used: Optional[str] = None  # actual scope applied
    skipped: bool = False             # True when feature disabled or scope=none
    error: Optional[str] = None       # non-fatal: service raised but flag is fail-open


@dataclass(frozen=True)
class MemoryWriteRequest:
    """Inputs required to persist a memory event after response generation.

    Note on frozen=True + metadata dict: frozen prevents reassigning the
    `metadata` attribute itself, but the dict's contents remain mutable (a
    Python dataclass limitation).  Callers must not mutate `metadata` after
    constructing this object; memory_service.store() only reads it.
    """

    user_id: str        # MUST come from auth context
    thread_id: str
    user_message: str
    assistant_reply: str
    scope: MemoryScopeValue
    metadata: dict = field(default_factory=dict)


@dataclass
class MemoryWriteResult:
    """Result returned by memory_service.store()."""

    stored: bool = False
    skipped: bool = False   # True when feature disabled, scope=none, or min_chars
    error: Optional[str] = None

from pydantic import BaseModel, Field
from typing import Literal, Optional


MemoryScope = Literal["default", "none", "session", "experiment"]


class ChatRequest(BaseModel):
    threadId: str = Field(min_length=1)
    message: str = Field(min_length=1)
    mode: Optional[str] = None
    # memory_scope governs how long-term memory is read/written for this turn.
    # - "default": follow global MEMORY_READ/WRITE_ENABLED flags.
    # - "none": skip memory read and write entirely for this turn.
    # - "session": read/write limited to session-scoped memory (if enabled).
    # - "experiment": opt-in experimental memory path (disabled by default).
    # Clients may request a scope; the server enforces allowed values via
    # memory_policy.resolve_scope() and ignores disallowed values silently.
    memory_scope: Optional[MemoryScope] = None


class ChatResponse(BaseModel):
    threadId: str
    resolvedModelId: str
    reply: str
    # memory_resolved is informational only — present when memory was active.
    # None when memory is globally disabled or scope is "none".
    memory_resolved: Optional[str] = None  # actual scope used, or None

from __future__ import annotations

from pydantic import BaseModel, Field


class TruthQueryRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    session_id: str | None = None
    message: str = Field(..., min_length=1)
    mode: str = Field(default="mentor")
    depth: str = Field(default="standard")
    language: str = Field(default="en")
    dry_run: bool = False

    # --- Case identity fields (optional; resolved into CaseContext by the route handler) ---
    # These are passed from the proxy / frontend when known; all are optional
    # so that existing callers without case context continue to work unchanged.
    login_username: str | None = Field(None, description="Login username from auth layer")
    preferred_name: str | None = Field(None, description="Explicitly requested preferred name")
    display_name: str | None = Field(None, description="Case/display name from admin panel")
    source_channel: str | None = Field(None, description="Entry channel, e.g. 'web', 'api'")


class TruthDimensionItem(BaseModel):
    code: str
    name_zh: str
    name_en: str
    description: str


class TruthDimensionsResponse(BaseModel):
    dimensions: list[TruthDimensionItem]


class CorePrincipleItem(BaseModel):
    dimension_code: str
    code: str
    title: str
    axiom: str
    explanation: str | None = None


class CorePrinciplesResponse(BaseModel):
    principles: list[CorePrincipleItem]


class SessionMemoryItem(BaseModel):
    dimension: str
    principle: str | None = None
    snippet: str | None = None
    at: str


class SessionMemoryResponse(BaseModel):
    user_id: str
    history: list[SessionMemoryItem]


class TruthQueryResponse(BaseModel):
    mirror: str | None
    truth_view: str
    coach_question: str
    action: str
    dimension: str
    principles: list[str]
    retrieval_mode: str
    case_id: str | None = None
    session_id: str | None = None
    dimensions_triggered: list[str] = Field(default_factory=list)
    matched_puzzles_count: int = 0
    embedding_mode: str


class BridgeQueryRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    session_id: str | None = None
    message: str = Field(..., min_length=1)
    mode: str = Field(default="mentor")

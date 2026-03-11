from __future__ import annotations

from pydantic import BaseModel, Field


class TruthQueryRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    session_id: str | None = None
    message: str = Field(..., min_length=1)
    mode: str = Field(default="mentor")
    depth: str = Field(default="standard")
    language: str = Field(default="en")

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TruthQueryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(..., alias="userid", min_length=1)
    session_id: str | None = Field(default=None, alias="sessionid")
    message: str = Field(..., min_length=1)
    mode: str = Field(default="mentor")
    depth: str = Field(default="standard")
    language: str = Field(default="en")

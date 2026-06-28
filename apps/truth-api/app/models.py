from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TruthQueryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(..., alias="userid", min_length=1)
    session_id: str | None = Field(default=None, alias="sessionid")
    message: str = Field(..., min_length=1)
    mode: str = Field(default="mentor")
    depth: str = Field(default="standard")
    language: str = Field(default="en")

    @model_validator(mode="before")
    @classmethod
    def accept_query_as_message(cls, values: Any) -> Any:
        if isinstance(values, dict) and "message" not in values and "query" in values:
            values = dict(values)
            values["message"] = values["query"]
        return values

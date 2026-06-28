from typing import Optional, Literal, List
from pydantic import BaseModel, Field


class CreateThreadRequest(BaseModel):
    mode: str = Field(min_length=1, max_length=64)
    title: Optional[str] = Field(default=None, max_length=255)


class CreateThreadResponse(BaseModel):
    threadId: str
    mode: str
    resolvedModelId: str


class ThreadEntry(BaseModel):
    id: str
    speaker: Literal["user", "assistant", "system", "admin_note"]
    content: str
    createdAt: str


class ThreadResponse(BaseModel):
    threadId: str
    mode: str
    resolvedModelId: str
    title: Optional[str] = None
    entries: List[ThreadEntry]

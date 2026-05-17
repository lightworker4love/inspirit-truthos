from __future__ import annotations

from typing import Optional
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel

from .agent import handle_message, start_session


app = FastAPI(title="Hermes Agent API")


class ChatRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    message: str
    context: Optional[dict] = None


@app.post("/chat")
async def chat(req: ChatRequest) -> dict:
    session_id = req.session_id or str(uuid4())
    result = await handle_message(
        user_id=req.user_id,
        session_id=session_id,
        message=req.message,
        context=req.context,
    )
    return {"session_id": session_id, **result}


@app.get("/session/start/{user_id}")
async def session_start(user_id: str) -> dict:
    soul_ctx = await start_session(user_id)
    return {"user_id": user_id, "soul_context": soul_ctx}


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "hermes-agent"}

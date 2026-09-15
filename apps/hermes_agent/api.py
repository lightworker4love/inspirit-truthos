from __future__ import annotations

from typing import Optional
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .agent import handle_message, start_session


TRUTHOS_WEB_ORIGIN = "https://truthos-web-production.up.railway.app"

app = FastAPI(title="Hermes Agent API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[TRUTHOS_WEB_ORIGIN],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


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

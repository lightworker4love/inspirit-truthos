import json

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

# Gateway timeout — oMLX on slow hardware can take 90s+ per turn.
_GATEWAY_TIMEOUT = httpx.Timeout(connect=10.0, read=180.0, write=10.0, pool=10.0)


def chat(payload: dict):
    """Send a chat completion through the OpenClaw gateway.

    Uses SSE streaming (stream:true) because the gateway's non-streaming
    path has reliability issues with slow local models.  The full response
    is reassembled from the SSE text_delta chunks before returning.
    """
    url = f"{settings.openclaw_gateway_base_url}{settings.openclaw_gateway_chat_path}"
    headers = {
        "Authorization": f"Bearer {settings.openclaw_gateway_token}",
        "Content-Type": "application/json",
    }

    # Force streaming — gateway handles this reliably even for slow models.
    stream_payload = {**payload, "stream": True}

    try:
        with httpx.Client(timeout=_GATEWAY_TIMEOUT) as client:
            with client.stream("POST", url, headers=headers, json=stream_payload) as resp:
                if resp.status_code >= 400:
                    resp.read()
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"OpenClaw upstream error: {resp.text}",
                    )
                content = _consume_sse(resp)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Upstream OpenClaw unavailable: {exc}",
        ) from exc

    return {"raw": {"streaming": True, "model": payload.get("model")}, "content": content}


def _consume_sse(resp: httpx.Response) -> str:
    """Read an SSE stream and reassemble the assistant content."""
    parts: list[str] = []
    for line in resp.iter_lines():
        if not line.startswith("data: "):
            continue
        data_str = line[len("data: "):]
        if data_str.strip() == "[DONE]":
            break
        try:
            chunk = json.loads(data_str)
        except json.JSONDecodeError:
            continue
        delta = (chunk.get("choices") or [{}])[0].get("delta") or {}
        text = delta.get("content")
        if text:
            parts.append(text)
    return "".join(parts)

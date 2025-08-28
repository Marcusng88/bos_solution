"""
SSE endpoints for ROI update status
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json
from datetime import datetime, timezone

router = APIRouter()

_subscribers = set()


async def _event_stream():
    queue: asyncio.Queue[str] = asyncio.Queue()
    _subscribers.add(queue)
    try:
        while True:
            data = await queue.get()
            yield f"data: {data}\n\n"
    finally:
        _subscribers.discard(queue)


def publish_status(event: str, payload: dict):
    data = json.dumps({"event": event, "payload": payload, "ts": datetime.now(timezone.utc).isoformat()})
    for q in list(_subscribers):
        try:
            q.put_nowait(data)
        except Exception:
            pass


@router.get("/stream", tags=["roi-updates"])
async def stream_updates():
    return StreamingResponse(_event_stream(), media_type="text/event-stream")



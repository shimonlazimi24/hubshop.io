import asyncio
import logging
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError

from backend.auth.jwt import decode_token
from backend.tiktok.rate_limiter import get_redis

logger = logging.getLogger(__name__)

router = APIRouter()


def _validate_ws_token(token: str) -> uuid.UUID | None:
    """Validate JWT from WebSocket query param. Returns user_id or None."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        return uuid.UUID(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None


@router.websocket("/ws/{workspace_id}")
async def commerce_websocket(
    websocket: WebSocket,
    workspace_id: uuid.UUID,
) -> None:
    """WebSocket endpoint for real-time commerce updates.

    Authenticates via JWT token in query parameter.
    Subscribes to Redis pub/sub channel for the workspace.
    """
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    user_id = _validate_ws_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await websocket.accept()

    channel = f"commerce:ws:{workspace_id}"
    r = await get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(channel)

    try:
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message and message["type"] == "message":
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                await websocket.send_text(data)

            # Small yield to prevent busy loop
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for workspace %s", workspace_id)
    except Exception:
        logger.exception("WebSocket error for workspace %s", workspace_id)
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()

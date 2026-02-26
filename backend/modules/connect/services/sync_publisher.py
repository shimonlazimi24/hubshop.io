"""Publish sync progress events to Redis for WebSocket consumption."""

from __future__ import annotations

import json
import uuid

from backend.tiktok.rate_limiter import get_redis


async def publish_sync_event(
    workspace_id: uuid.UUID,
    event_type: str,
    platform: str,
    sync_type: str,
    items_synced: int = 0,
    items_total: int | None = None,
    error: str | None = None,
) -> None:
    """Publish a sync event to the workspace's connect WebSocket channel."""
    channel = f"connect:sync:{workspace_id}"
    payload = {
        "type": event_type,
        "platform": platform,
        "sync_type": sync_type,
        "items_synced": items_synced,
        "items_total": items_total,
    }
    if error:
        payload["error"] = error

    r = await get_redis()
    await r.publish(channel, json.dumps(payload))

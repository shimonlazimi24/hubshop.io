import json
import uuid

from fastapi import APIRouter, Header, HTTPException, Request, status

from backend.db.engine import async_session_factory
from backend.db.models.platform import Platform
from backend.db.models.webhook import WebhookEvent, WebhookStatus
from backend.modules.webhooks.verification import (
    verify_developer_webhook,
    verify_shop_webhook,
)
from backend.tiktok.rate_limiter import get_redis

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


async def _deduplicate(idempotency_key: str) -> bool:
    """Check and set idempotency key in Redis. Returns True if this is a new event."""
    r = await get_redis()
    was_set = await r.set(f"webhook:dedup:{idempotency_key}", "1", nx=True, ex=86400)
    return bool(was_set)


async def _store_event(
    platform: Platform,
    event_type: str,
    idempotency_key: str,
    payload: dict,
) -> uuid.UUID:
    """Store webhook event in the database."""
    async with async_session_factory() as session:
        event = WebhookEvent(
            platform=platform,
            event_type=event_type,
            idempotency_key=idempotency_key,
            payload=payload,
            status=WebhookStatus.RECEIVED,
        )
        session.add(event)
        await session.commit()
        return event.id


@router.post("/shop")
async def shop_webhook(
    request: Request,
    authorization: str = Header(...),
) -> dict:
    """Receive and verify TikTok Shop webhooks."""
    body = await request.body()

    if not verify_shop_webhook(body, authorization):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    payload = json.loads(body)
    event_type = str(payload.get("type", "unknown"))
    idempotency_key = f"shop:{payload.get('event_id', uuid.uuid4().hex)}"

    is_new = await _deduplicate(idempotency_key)
    if not is_new:
        return {"status": "duplicate"}

    event_id = await _store_event(Platform.SHOP, event_type, idempotency_key, payload)

    # Enqueue Celery task for async processing
    from backend.workers.webhook_processor import process_webhook

    process_webhook.delay(str(event_id))

    return {"status": "received", "event_id": str(event_id)}


@router.post("/developer")
async def developer_webhook(
    request: Request,
    tiktok_signature: str = Header(..., alias="TikTok-Signature"),
) -> dict:
    """Receive and verify TikTok Developer webhooks."""
    body = await request.body()

    if not verify_developer_webhook(body, tiktok_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    payload = json.loads(body)
    event_type = payload.get("event", "unknown")
    idempotency_key = f"developer:{payload.get('event_id', uuid.uuid4().hex)}"

    is_new = await _deduplicate(idempotency_key)
    if not is_new:
        return {"status": "duplicate"}

    event_id = await _store_event(Platform.DEVELOPER, event_type, idempotency_key, payload)

    from backend.workers.webhook_processor import process_webhook

    process_webhook.delay(str(event_id))

    return {"status": "received", "event_id": str(event_id)}


@router.post("/marketing")
async def marketing_webhook(request: Request) -> dict:
    """Receive TikTok Marketing webhooks (verification varies by subscription)."""
    body = await request.body()
    payload = json.loads(body)

    event_type = payload.get("type", "unknown")
    idempotency_key = f"marketing:{payload.get('event_id', uuid.uuid4().hex)}"

    is_new = await _deduplicate(idempotency_key)
    if not is_new:
        return {"status": "duplicate"}

    event_id = await _store_event(Platform.MARKETING, event_type, idempotency_key, payload)

    from backend.workers.webhook_processor import process_webhook

    process_webhook.delay(str(event_id))

    return {"status": "received", "event_id": str(event_id)}

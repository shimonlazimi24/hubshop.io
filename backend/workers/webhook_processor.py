import logging
import uuid

from sqlalchemy import select

from backend.db.engine import async_session_factory
from backend.db.models.webhook import WebhookEvent, WebhookStatus
from backend.tiktok.rate_limiter import get_redis
from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)

# Redis key TTL for webhook idempotency (24 hours)
_IDEMPOTENCY_TTL_SECONDS = 24 * 60 * 60


async def _is_already_processed(event_id: str) -> bool:
    """Check if a webhook event was already processed via Redis idempotency key."""
    r = await get_redis()
    return await r.exists(f"webhook_processed:{event_id}") > 0


async def _mark_processed(event_id: str) -> None:
    """Mark a webhook event as processed by setting a Redis key with 24h TTL."""
    r = await get_redis()
    await r.set(f"webhook_processed:{event_id}", "1", ex=_IDEMPOTENCY_TTL_SECONDS)


async def _process_webhook(event_id: str) -> None:
    """Process a single webhook event by routing to the appropriate domain handler."""
    # Idempotency check: skip if already processed (e.g. Celery requeue)
    if await _is_already_processed(event_id):
        logger.info("Webhook %s already processed, skipping", event_id)
        return

    async with async_session_factory() as session:
        result = await session.execute(
            select(WebhookEvent).where(WebhookEvent.id == uuid.UUID(event_id))
        )
        event = result.scalar_one_or_none()
        if not event:
            logger.error("Webhook event %s not found", event_id)
            return

        event.status = WebhookStatus.PROCESSING
        await session.commit()

        try:
            # Route to domain handler based on platform and event type
            handler = _get_handler(event.platform.value, event.event_type)
            if handler:
                await handler(event.payload, session)
            else:
                logger.info(
                    "No handler for %s:%s, storing only",
                    event.platform.value,
                    event.event_type,
                )

            event.status = WebhookStatus.PROCESSED
            await session.commit()

            # Mark as processed in Redis to prevent duplicate processing
            await _mark_processed(event_id)

            logger.info(
                "Processed webhook %s (%s:%s)",
                event_id,
                event.platform.value,
                event.event_type,
            )

        except Exception as exc:
            event.status = WebhookStatus.FAILED
            event.error_message = str(exc)[:1000]
            await session.commit()
            logger.exception("Failed to process webhook %s", event_id)
            raise


def _get_handler(platform: str, event_type: str):  # type: ignore[no-untyped-def]
    """Get the appropriate domain handler for a webhook event.

    Returns None if no handler is registered (event is stored but not processed).
    """
    from backend.modules.commerce.webhook_handlers import COMMERCE_WEBHOOK_HANDLERS

    _handlers: dict[str, dict[str, object]] = {
        "shop": COMMERCE_WEBHOOK_HANDLERS,
        "developer": {
            # Phase 4: video.publish, etc.
        },
        "marketing": {
            # Phase 3: campaign.status_change, etc.
        },
    }
    platform_handlers = _handlers.get(platform, {})
    return platform_handlers.get(event_type)


@celery_app.task(
    bind=True,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    name="backend.workers.webhook_processor.process_webhook",
)
def process_webhook(self, event_id: str) -> None:  # type: ignore[no-untyped-def]
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_process_webhook(event_id))
    except Exception as exc:
        logger.exception("Webhook processing failed for %s", event_id)
        self.retry(exc=exc)
    finally:
        loop.close()

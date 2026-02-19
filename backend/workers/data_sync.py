import asyncio
import logging

from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):  # type: ignore[no-untyped-def]
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _sync_shop_orders() -> None:
    """Poll TikTok Shop API for recent orders as webhook reconciliation.

    This ensures no orders are missed if webhooks are delayed or dropped.
    Implemented in Phase 2.
    """
    logger.info("Shop order sync - placeholder (Phase 2)")


@celery_app.task(name="backend.workers.data_sync.sync_shop_orders")
def sync_shop_orders() -> None:
    _run_async(_sync_shop_orders())

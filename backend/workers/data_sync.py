import asyncio
import logging
import time
from datetime import UTC, datetime, timezone

from sqlalchemy import select

from backend.db.engine import async_session_factory
from backend.db.models.commerce import Shop, SyncCursor
from backend.modules.commerce.services.order_service import OrderService
from backend.modules.commerce.services.product_service import ProductService
from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)

# Overlap window to catch late-arriving orders (5 minutes)
_OVERLAP_SECONDS = 5 * 60
# Maximum lookback for first-time sync (48 hours)
_MAX_LOOKBACK_SECONDS = 48 * 3600


def _run_async(coro):  # type: ignore[no-untyped-def]
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _get_or_create_cursor(
    session, shop_id, sync_type: str  # type: ignore[no-untyped-def]
) -> SyncCursor:
    """Get or create a SyncCursor for a shop and sync type."""
    result = await session.execute(
        select(SyncCursor).where(
            SyncCursor.shop_id == shop_id,
            SyncCursor.sync_type == sync_type,
        )
    )
    cursor = result.scalar_one_or_none()
    if not cursor:
        cursor = SyncCursor(
            shop_id=shop_id,
            sync_type=sync_type,
        )
        session.add(cursor)
        await session.flush()
    return cursor


async def _sync_shop_orders() -> None:
    """Poll TikTok Shop API for recent orders across all active shops."""
    async with async_session_factory() as session:
        result = await session.execute(select(Shop))
        shops = result.scalars().all()

        for shop in shops:
            try:
                await _sync_single_shop_orders(session, shop)
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception(
                    "Failed to sync orders for shop %s", shop.id
                )


async def _sync_single_shop_orders(session, shop: Shop) -> int:  # type: ignore[no-untyped-def]
    """Sync orders for a single shop. Returns synced count."""
    cursor = await _get_or_create_cursor(session, shop.id, "orders")

    now = datetime.now(tz=UTC)
    now_ts = int(now.timestamp())

    if cursor.last_sync_at:
        from_ts = int(cursor.last_sync_at.timestamp()) - _OVERLAP_SECONDS
    else:
        from_ts = now_ts - _MAX_LOOKBACK_SECONDS

    order_service = OrderService(session)
    synced = await order_service.sync_orders(
        shop,
        create_time_from=from_ts,
        create_time_to=now_ts,
    )

    cursor.last_sync_at = now
    shop.last_order_sync_at = now

    logger.info("Synced %d orders for shop %s", synced, shop.shop_name)
    return synced


async def _sync_shop_products() -> None:
    """Poll TikTok Shop API for products across all active shops."""
    async with async_session_factory() as session:
        result = await session.execute(select(Shop))
        shops = result.scalars().all()

        for shop in shops:
            try:
                await _sync_single_shop_products(session, shop)
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception(
                    "Failed to sync products for shop %s", shop.id
                )


async def _sync_single_shop_products(session, shop: Shop) -> int:  # type: ignore[no-untyped-def]
    """Sync products for a single shop. Returns synced count."""
    cursor = await _get_or_create_cursor(session, shop.id, "products")
    now = datetime.now(tz=UTC)

    product_service = ProductService(session)
    synced = await product_service.sync_products(shop)

    cursor.last_sync_at = now
    shop.last_product_sync_at = now

    logger.info("Synced %d products for shop %s", synced, shop.shop_name)
    return synced


@celery_app.task(name="backend.workers.data_sync.sync_shop_orders")
def sync_shop_orders() -> None:
    _run_async(_sync_shop_orders())


@celery_app.task(name="backend.workers.data_sync.sync_shop_products")
def sync_shop_products() -> None:
    _run_async(_sync_shop_products())


@celery_app.task(name="backend.workers.data_sync.sync_single_shop_orders")
def sync_single_shop_orders(shop_id: str) -> None:
    """On-demand sync for a specific shop's orders."""

    async def _sync() -> None:
        async with async_session_factory() as session:
            result = await session.execute(
                select(Shop).where(Shop.id == shop_id)
            )
            shop = result.scalar_one_or_none()
            if shop:
                await _sync_single_shop_orders(session, shop)
                await session.commit()

    _run_async(_sync())


@celery_app.task(name="backend.workers.data_sync.sync_single_shop_products")
def sync_single_shop_products(shop_id: str) -> None:
    """On-demand sync for a specific shop's products."""

    async def _sync() -> None:
        async with async_session_factory() as session:
            result = await session.execute(
                select(Shop).where(Shop.id == shop_id)
            )
            shop = result.scalar_one_or_none()
            if shop:
                await _sync_single_shop_products(session, shop)
                await session.commit()

    _run_async(_sync())

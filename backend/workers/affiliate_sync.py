"""Celery workers for affiliate data synchronization (E5).

Tasks:
- sync_affiliate_creators: daily discovery refresh
- sync_affiliate_orders: every 2h order sync
- sync_sample_requests: every 30min sample request sync
"""

import asyncio
import logging

from sqlalchemy import select

from backend.db.engine import async_session_factory
from backend.db.models.commerce import Shop
from backend.modules.commerce.services.affiliate_service import AffiliateService
from backend.modules.commerce.services.shop_service import ShopService
from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):  # type: ignore[no-untyped-def]
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _sync_affiliate_creators() -> None:
    """Sync affiliate creator data for all shops."""
    async with async_session_factory() as session:
        result = await session.execute(select(Shop))
        shops = result.scalars().all()

        for shop in shops:
            try:
                shop_service = ShopService(session)
                gateway = await shop_service.build_gateway_for_shop(shop)
                resp = await gateway.get("/affiliate/202309/seller/creators")
                creators = resp.get("data", {}).get("creators", [])
                logger.info(
                    "Synced %d creators for shop %s",
                    len(creators),
                    shop.id,
                )
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("Failed to sync creators for shop %s", shop.id)


async def _sync_affiliate_orders() -> None:
    """Sync affiliate orders for all shops."""
    async with async_session_factory() as session:
        result = await session.execute(select(Shop))
        shops = result.scalars().all()

        for shop in shops:
            try:
                service = AffiliateService(session)
                synced = await service.sync_affiliate_orders(shop)
                logger.info(
                    "Synced %d affiliate orders for shop %s",
                    synced,
                    shop.id,
                )
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("Failed to sync affiliate orders for shop %s", shop.id)


async def _sync_sample_requests() -> None:
    """Sync sample requests for all shops."""
    async with async_session_factory() as session:
        result = await session.execute(select(Shop))
        shops = result.scalars().all()

        for shop in shops:
            try:
                shop_service = ShopService(session)
                gateway = await shop_service.build_gateway_for_shop(shop)
                resp = await gateway.get("/affiliate/202309/seller/samples")
                samples = resp.get("data", {}).get("sample_requests", [])
                logger.info(
                    "Synced %d sample requests for shop %s",
                    len(samples),
                    shop.id,
                )
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("Failed to sync sample requests for shop %s", shop.id)


@celery_app.task(name="backend.workers.affiliate_sync.sync_affiliate_creators")
def sync_affiliate_creators() -> None:
    """Daily affiliate creator sync."""
    _run_async(_sync_affiliate_creators())


@celery_app.task(name="backend.workers.affiliate_sync.sync_affiliate_orders")
def sync_affiliate_orders() -> None:
    """Bi-hourly affiliate order sync."""
    _run_async(_sync_affiliate_orders())


@celery_app.task(name="backend.workers.affiliate_sync.sync_sample_requests")
def sync_sample_requests() -> None:
    """Half-hourly sample request sync."""
    _run_async(_sync_sample_requests())

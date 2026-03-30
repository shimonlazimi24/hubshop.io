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


@celery_app.task(name="backend.workers.promotion_sync.sync_all_promotions")
def sync_all_promotions() -> dict[str, int]:
    """Sync promotion statuses from TikTok for all shops."""
    return _run_async(_sync_all_promotions())


async def _sync_all_promotions() -> dict[str, int]:
    from sqlalchemy import select

    from backend.db.engine import async_session_factory
    from backend.db.models.commerce import Shop
    from backend.modules.commerce.services.promotion_service import PromotionService

    total = 0
    async with async_session_factory() as session:
        result = await session.execute(select(Shop))
        shops = list(result.scalars().all())

        service = PromotionService(session)
        for shop in shops:
            try:
                count = await service.sync_promotions(shop)
                total += count
            except Exception:
                logger.exception("Failed to sync promotions for shop %s", shop.id)

        await session.commit()

    logger.info("Synced %d promotions", total)
    return {"synced": total}


@celery_app.task(name="backend.workers.promotion_sync.sync_all_coupons")
def sync_all_coupons() -> dict[str, int]:
    """Sync coupons from TikTok for all shops."""
    return _run_async(_sync_all_coupons())


async def _sync_all_coupons() -> dict[str, int]:
    from sqlalchemy import select

    from backend.db.engine import async_session_factory
    from backend.db.models.commerce import Shop
    from backend.modules.commerce.services.coupon_service import CouponService

    total = 0
    async with async_session_factory() as session:
        result = await session.execute(select(Shop))
        shops = list(result.scalars().all())

        service = CouponService(session)
        for shop in shops:
            try:
                count = await service.sync_coupons(shop)
                total += count
            except Exception:
                logger.exception("Failed to sync coupons for shop %s", shop.id)

        await session.commit()

    logger.info("Synced %d coupons", total)
    return {"synced": total}

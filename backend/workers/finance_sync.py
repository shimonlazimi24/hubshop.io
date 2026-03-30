"""Finance sync Celery workers — daily statements and unsettled transactions."""

import asyncio
import logging

from sqlalchemy import select

from backend.db.engine import async_session_factory
from backend.db.models.commerce import Shop
from backend.modules.commerce.services.finance_service import FinanceService
from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):  # type: ignore[no-untyped-def]
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _sync_daily_statements() -> None:
    """Sync settlement statements for all shops."""
    async with async_session_factory() as session:
        result = await session.execute(select(Shop))
        shops = result.scalars().all()

        for shop in shops:
            try:
                service = FinanceService(session)
                synced = await service.sync_settlements(shop)
                await session.commit()
                logger.info("Synced %d settlements for shop %s", synced, shop.shop_name)
            except Exception:
                await session.rollback()
                logger.exception("Failed to sync settlements for shop %s", shop.id)


async def _sync_unsettled_transactions() -> None:
    """Sync transactions for all shops."""
    async with async_session_factory() as session:
        result = await session.execute(select(Shop))
        shops = result.scalars().all()

        for shop in shops:
            try:
                service = FinanceService(session)
                synced = await service.sync_transactions(shop)
                await session.commit()
                logger.info(
                    "Synced %d transactions for shop %s", synced, shop.shop_name
                )
            except Exception:
                await session.rollback()
                logger.exception("Failed to sync transactions for shop %s", shop.id)


@celery_app.task(name="backend.workers.finance_sync.sync_daily_statements")
def sync_daily_statements() -> None:
    _run_async(_sync_daily_statements())


@celery_app.task(name="backend.workers.finance_sync.sync_unsettled_transactions")
def sync_unsettled_transactions() -> None:
    _run_async(_sync_unsettled_transactions())

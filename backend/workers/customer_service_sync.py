"""Celery tasks for customer service and engagement data sync."""

import asyncio
import logging
from datetime import date

from sqlalchemy import select

from backend.db.engine import async_session_factory
from backend.db.models.commerce import Shop
from backend.db.models.customer_service import CsPerformanceSnapshot
from backend.modules.commerce.services.customer_service import CustomerServiceService
from backend.modules.commerce.services.shop_service import ShopService
from backend.modules.customer_engagement.services.engagement_service import (
    EngagementService,
)
from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):  # type: ignore[no-untyped-def]
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _sync_cs_conversations() -> None:
    """Sync customer service conversations for all shops."""
    async with async_session_factory() as session:
        result = await session.execute(select(Shop))
        shops = result.scalars().all()

        for shop in shops:
            try:
                shop_service = ShopService(session)
                gateway = await shop_service.build_gateway_for_shop(shop)
                resp = await gateway.get(
                    "/customer_service/202309/conversations",
                    params={"page_size": "50"},
                )
                conversations = resp.get("data", {}).get("conversations", [])
                logger.info(
                    "Synced %d CS conversations for shop %s",
                    len(conversations),
                    shop.shop_name,
                )
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("Failed CS conversation sync for shop %s", shop.id)


async def _snapshot_cs_performance() -> None:
    """Snapshot CS performance metrics for all shops."""
    async with async_session_factory() as session:
        result = await session.execute(select(Shop))
        shops = result.scalars().all()

        for shop in shops:
            try:
                cs_service = CustomerServiceService(session)
                perf = await cs_service.get_cs_performance(shop)

                snapshot = CsPerformanceSnapshot(
                    workspace_id=shop.workspace_id,
                    shop_id=shop.id,
                    date=date.today(),
                    response_rate_24h=perf.get("response_rate_24h"),
                    resolution_rate=perf.get("resolution_rate"),
                    satisfaction_score=perf.get("satisfaction_score"),
                    total_conversations=perf.get("total_conversations"),
                    avg_response_time_seconds=perf.get("avg_response_time_seconds"),
                )
                session.add(snapshot)
                await session.commit()
                logger.info("Snapshotted CS performance for shop %s", shop.shop_name)
            except Exception:
                await session.rollback()
                logger.exception("Failed CS performance snapshot for shop %s", shop.id)


async def _sync_engagement_templates() -> None:
    """Sync engagement templates for all shops."""
    async with async_session_factory() as session:
        result = await session.execute(select(Shop))
        shops = result.scalars().all()

        for shop in shops:
            try:
                engagement_service = EngagementService(session)
                templates = await engagement_service.get_templates(shop)
                template_list = templates.get("templates", [])
                logger.info(
                    "Synced %d engagement templates for shop %s",
                    len(template_list),
                    shop.shop_name,
                )
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("Failed engagement template sync for shop %s", shop.id)


@celery_app.task(name="backend.workers.customer_service_sync.sync_cs_conversations")
def sync_cs_conversations() -> None:
    """Sync CS conversations. Runs every 15 minutes."""
    _run_async(_sync_cs_conversations())


@celery_app.task(name="backend.workers.customer_service_sync.snapshot_cs_performance")
def snapshot_cs_performance() -> None:
    """Snapshot CS performance metrics. Runs daily at 02:05."""
    _run_async(_snapshot_cs_performance())


@celery_app.task(name="backend.workers.customer_service_sync.sync_engagement_templates")
def sync_engagement_templates() -> None:
    """Sync engagement templates. Runs daily at 03:15."""
    _run_async(_sync_engagement_templates())

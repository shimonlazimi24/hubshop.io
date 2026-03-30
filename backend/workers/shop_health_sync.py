import asyncio
import logging
from datetime import date

from sqlalchemy import select

from backend.db.engine import async_session_factory
from backend.db.models.commerce import Shop
from backend.db.models.organization import Workspace
from backend.modules.shop_health.services.alert_service import AlertService
from backend.modules.shop_health.services.analytics_service import (
    UnifiedAnalyticsService,
)
from backend.modules.shop_health.services.sps_service import SpsEstimationService
from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):  # type: ignore[no-untyped-def]
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _calculate_daily_sps() -> None:
    """Calculate and save daily SPS snapshots for all shops."""
    async with async_session_factory() as session:
        result = await session.execute(select(Workspace))
        workspaces = result.scalars().all()

        for workspace in workspaces:
            shop_result = await session.execute(
                select(Shop).where(Shop.workspace_id == workspace.id)
            )
            shops = shop_result.scalars().all()

            for shop in shops:
                try:
                    service = SpsEstimationService(session)
                    await service.save_daily_snapshot(workspace.id, shop.id)
                    await session.commit()
                    logger.info(
                        "SPS snapshot saved for shop %s in workspace %s",
                        shop.id,
                        workspace.id,
                    )
                except Exception:
                    await session.rollback()
                    logger.exception(
                        "Failed SPS snapshot for shop %s in workspace %s",
                        shop.id,
                        workspace.id,
                    )


async def _calculate_daily_unified_metrics() -> None:
    """Calculate and save daily unified metrics for all shops."""
    today = date.today()

    async with async_session_factory() as session:
        result = await session.execute(select(Workspace))
        workspaces = result.scalars().all()

        for workspace in workspaces:
            shop_result = await session.execute(
                select(Shop).where(Shop.workspace_id == workspace.id)
            )
            shops = shop_result.scalars().all()

            for shop in shops:
                try:
                    service = UnifiedAnalyticsService(session)
                    await service.calculate_daily_metrics(workspace.id, shop.id, today)
                    await session.commit()
                    logger.info(
                        "Daily metrics saved for shop %s in workspace %s",
                        shop.id,
                        workspace.id,
                    )
                except Exception:
                    await session.rollback()
                    logger.exception(
                        "Failed daily metrics for shop %s in workspace %s",
                        shop.id,
                        workspace.id,
                    )


async def _check_health_alerts() -> None:
    """Evaluate health alerts for all shops based on current metrics."""
    async with async_session_factory() as session:
        result = await session.execute(select(Workspace))
        workspaces = result.scalars().all()

        for workspace in workspaces:
            shop_result = await session.execute(
                select(Shop).where(Shop.workspace_id == workspace.id)
            )
            shops = shop_result.scalars().all()

            for shop in shops:
                try:
                    sps_service = SpsEstimationService(session)
                    metrics = await sps_service.calculate_estimated_sps(
                        workspace.id, shop.id
                    )

                    alert_metrics = {
                        "estimated_score": float(metrics["estimated_score"]),
                        "otdr": float(metrics["otdr"]),
                    }

                    alert_service = AlertService(session)
                    alerts = await alert_service.evaluate_and_create_alerts(
                        workspace.id, shop.id, alert_metrics
                    )
                    await session.commit()

                    if alerts:
                        logger.warning(
                            "%d alerts triggered for shop %s in workspace %s",
                            len(alerts),
                            shop.id,
                            workspace.id,
                        )
                except Exception:
                    await session.rollback()
                    logger.exception(
                        "Failed alert check for shop %s in workspace %s",
                        shop.id,
                        workspace.id,
                    )


@celery_app.task(name="backend.workers.shop_health_sync.calculate_daily_sps")
def calculate_daily_sps() -> None:
    _run_async(_calculate_daily_sps())


@celery_app.task(
    name="backend.workers.shop_health_sync.calculate_daily_unified_metrics"
)
def calculate_daily_unified_metrics() -> None:
    _run_async(_calculate_daily_unified_metrics())


@celery_app.task(name="backend.workers.shop_health_sync.check_health_alerts")
def check_health_alerts() -> None:
    _run_async(_check_health_alerts())

import asyncio
import logging
from datetime import UTC

from sqlalchemy import select

from backend.db.engine import async_session_factory
from backend.db.models.analytics import ScheduledReport
from backend.db.models.organization import Workspace
from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):  # type: ignore[no-untyped-def]
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _take_daily_kpi_snapshots() -> None:
    """Take daily KPI snapshots for all workspaces."""
    from backend.modules.analytics.services.kpi_service import KpiService

    async with async_session_factory() as session:
        result = await session.execute(select(Workspace))
        workspaces = result.scalars().all()

        for workspace in workspaces:
            try:
                service = KpiService(session)
                await service.take_snapshot(workspace.id)
                await session.commit()
                logger.info("Took KPI snapshot for workspace %s", workspace.id)
            except Exception:
                await session.rollback()
                logger.exception("Failed KPI snapshot for workspace %s", workspace.id)


async def _run_scheduled_reports() -> None:
    """Run any scheduled reports that are due."""
    from datetime import datetime

    from backend.modules.analytics.services.report_service import ReportService

    async with async_session_factory() as session:
        now = datetime.now(tz=UTC)
        result = await session.execute(
            select(ScheduledReport).where(
                ScheduledReport.is_active.is_(True),
                ScheduledReport.next_run_at <= now,
            )
        )
        reports = result.scalars().all()

        for report in reports:
            try:
                service = ReportService(session)
                await service.generate_report(report)
                await session.commit()
                logger.info("Generated scheduled report %s", report.id)
            except Exception:
                await session.rollback()
                logger.exception("Failed to generate report %s", report.id)


@celery_app.task(name="backend.workers.analytics_sync.take_daily_kpi_snapshots")
def take_daily_kpi_snapshots() -> None:
    _run_async(_take_daily_kpi_snapshots())


@celery_app.task(name="backend.workers.analytics_sync.run_scheduled_reports")
def run_scheduled_reports() -> None:
    _run_async(_run_scheduled_reports())

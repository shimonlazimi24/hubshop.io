import logging
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.analytics import ScheduledReport
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class ReportService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_reports(
        self,
        workspace_id: uuid.UUID,
        *,
        is_active: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[ScheduledReport]:
        query = select(ScheduledReport).where(
            ScheduledReport.workspace_id == workspace_id
        )
        count_query = select(func.count(ScheduledReport.id)).where(
            ScheduledReport.workspace_id == workspace_id
        )

        if is_active is not None:
            query = query.where(ScheduledReport.is_active == is_active)
            count_query = count_query.where(ScheduledReport.is_active == is_active)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(ScheduledReport.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    async def get_report(self, report_id: uuid.UUID) -> ScheduledReport | None:
        result = await self._session.execute(
            select(ScheduledReport).where(ScheduledReport.id == report_id)
        )
        return result.scalar_one_or_none()

    async def create_report(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        *,
        name: str,
        description: str | None = None,
        modules: list[str],
        metrics: dict | None = None,
        frequency: str = "WEEKLY",
        format: str = "CSV",
    ) -> ScheduledReport:
        now = datetime.now(tz=UTC)
        next_run = self._calculate_next_run(frequency, now)

        report = ScheduledReport(
            workspace_id=workspace_id,
            created_by=user_id,
            name=name,
            description=description,
            modules=modules,
            metrics=metrics or {},
            frequency=frequency,
            format=format,
            is_active=True,
            next_run_at=next_run,
        )
        self._session.add(report)
        await self._session.flush()
        return report

    async def update_report(
        self,
        report: ScheduledReport,
        *,
        name: str | None = None,
        description: str | None = None,
        modules: list[str] | None = None,
        frequency: str | None = None,
        format: str | None = None,
        is_active: bool | None = None,
    ) -> ScheduledReport:
        if name is not None:
            report.name = name
        if description is not None:
            report.description = description
        if modules is not None:
            report.modules = modules
        if frequency is not None:
            report.frequency = frequency
            report.next_run_at = self._calculate_next_run(
                frequency, datetime.now(tz=UTC)
            )
        if format is not None:
            report.format = format
        if is_active is not None:
            report.is_active = is_active
        return report

    async def delete_report(self, report_id: uuid.UUID) -> bool:
        result = await self._session.execute(
            select(ScheduledReport).where(ScheduledReport.id == report_id)
        )
        report = result.scalar_one_or_none()
        if not report:
            return False
        await self._session.delete(report)
        return True

    async def generate_report(self, report: ScheduledReport) -> dict:
        """Generate report data and update last_run_at."""
        from backend.modules.analytics.services.kpi_service import KpiService

        kpi_service = KpiService(self._session)
        overview = await kpi_service.get_overview(report.workspace_id)

        now = datetime.now(tz=UTC)
        report.last_run_at = now
        report.next_run_at = self._calculate_next_run(report.frequency, now)
        report.last_result_json = {
            "generated_at": now.isoformat(),
            "data": overview,
        }

        return report.last_result_json

    @staticmethod
    def _calculate_next_run(frequency: str, from_time: datetime) -> datetime:
        if frequency == "DAILY":
            return from_time + timedelta(days=1)
        elif frequency == "WEEKLY":
            return from_time + timedelta(weeks=1)
        elif frequency == "MONTHLY":
            return from_time + timedelta(days=30)
        return from_time + timedelta(weeks=1)

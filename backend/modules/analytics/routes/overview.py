import uuid

from fastapi import APIRouter

from backend.dependencies import CurrentUser, DBSession
from backend.modules.analytics.services.export_service import ExportService
from backend.modules.analytics.services.kpi_service import KpiService
from backend.modules.analytics.services.unified_analytics_service import (
    UnifiedAnalyticsService,
)

router = APIRouter()


@router.get("/overview")
async def get_overview(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    days: int = 30,
) -> dict:
    """Unified KPIs across all platforms."""
    service = UnifiedAnalyticsService(db)
    return await service.get_overview_kpis(workspace_id, days=days)


@router.get("/kpi")
async def get_kpi_overview(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Cross-module KPI overview."""
    service = KpiService(db)
    return await service.get_overview(workspace_id)


@router.get("/timeseries")
async def get_timeseries(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    days: int = 30,
) -> list[dict]:
    """KPI timeseries from daily snapshots."""
    service = KpiService(db)
    return await service.get_timeseries(workspace_id, days=days)


@router.get("/drill-down/{module}")
async def get_drill_down(
    module: str,
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Detailed KPIs for a specific module."""
    service = KpiService(db)
    return await service.get_drill_down(workspace_id, module)


@router.get("/revenue-vs-spend")
async def get_revenue_vs_spend(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    days: int = 30,
) -> list[dict]:
    """Commerce revenue timeseries."""
    service = UnifiedAnalyticsService(db)
    return await service.get_revenue_vs_spend(workspace_id, days=days)


@router.get("/content-performance")
async def get_content_performance(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    """Video performance metrics."""
    service = UnifiedAnalyticsService(db)
    return await service.get_content_performance(workspace_id)


@router.get("/platform-health")
async def get_platform_health(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    """Connected accounts status."""
    service = UnifiedAnalyticsService(db)
    return await service.get_platform_health(workspace_id)


@router.get("/top-performers")
async def get_top_performers(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    limit: int = 5,
) -> dict:
    """Top products, videos, and campaigns."""
    service = UnifiedAnalyticsService(db)
    return await service.get_top_performers(workspace_id, limit=limit)


@router.post("/export")
async def export_data(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    dataset: str = "overview",
    format: str = "json",
    days: int = 30,
) -> dict:
    """Export data as CSV or JSON."""
    service = ExportService(db)
    return await service.export_data(
        workspace_id, dataset=dataset, format=format, days=days
    )

import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import (
    OrderStatusDistributionResponse,
    RevenueSummaryResponse,
    RevenueTimeseriesPoint,
    TopProductResponse,
)
from backend.modules.commerce.services.analytics_service import CommerceAnalyticsService

router = APIRouter()


@router.get(
    "/analytics/summary",
    response_model=RevenueSummaryResponse,
)
async def get_summary(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    days: int = 30,
) -> RevenueSummaryResponse:
    now = datetime.now(tz=UTC)
    period_start = now - timedelta(days=days)
    service = CommerceAnalyticsService(db)
    data = await service.get_revenue_summary(
        workspace_id, period_start=period_start, period_end=now
    )
    return RevenueSummaryResponse(**data)


@router.get(
    "/analytics/revenue",
    response_model=list[RevenueTimeseriesPoint],
)
async def get_revenue(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    days: int = 30,
) -> list[RevenueTimeseriesPoint]:
    now = datetime.now(tz=UTC)
    period_start = now - timedelta(days=days)
    service = CommerceAnalyticsService(db)
    data = await service.get_revenue_timeseries(
        workspace_id, period_start=period_start, period_end=now
    )
    return [RevenueTimeseriesPoint(**d) for d in data]


@router.get(
    "/analytics/top-products",
    response_model=list[TopProductResponse],
)
async def get_top_products(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    limit: int = 10,
) -> list[TopProductResponse]:
    service = CommerceAnalyticsService(db)
    data = await service.get_top_products(workspace_id, limit=limit)
    return [TopProductResponse(**d) for d in data]


@router.get(
    "/analytics/order-distribution",
    response_model=list[OrderStatusDistributionResponse],
)
async def get_order_distribution(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[OrderStatusDistributionResponse]:
    service = CommerceAnalyticsService(db)
    data = await service.get_order_status_distribution(workspace_id)
    return [OrderStatusDistributionResponse(**d) for d in data]

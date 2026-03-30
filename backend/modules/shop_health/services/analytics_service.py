import logging
import uuid
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import Campaign
from backend.db.models.commerce import Order, OrderStatus, Promotion, ReturnRequest
from backend.db.models.shop_health import UnifiedDailyMetrics

logger = logging.getLogger(__name__)


class UnifiedAnalyticsService:
    """Aggregate daily commerce metrics across orders, returns, promotions, and campaigns."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def calculate_daily_metrics(
        self,
        workspace_id: uuid.UUID,
        shop_id: uuid.UUID,
        target_date: date,
    ) -> UnifiedDailyMetrics:
        """Calculate and persist unified daily metrics for a given date."""
        # 1. Total GMV (sum of completed order amounts for the day)
        total_gmv = (
            await self._session.execute(
                select(func.coalesce(func.sum(Order.total_amount), "0.00")).where(
                    Order.workspace_id == workspace_id,
                    Order.shop_id == shop_id,
                    func.date(Order.created_at) == target_date,
                )
            )
        ).scalar_one()

        # 2. Order count
        order_count = (
            await self._session.execute(
                select(func.count(Order.id)).where(
                    Order.workspace_id == workspace_id,
                    Order.shop_id == shop_id,
                    func.date(Order.created_at) == target_date,
                )
            )
        ).scalar_one()

        # 3. Return count
        return_count = (
            await self._session.execute(
                select(func.count(ReturnRequest.id)).where(
                    ReturnRequest.workspace_id == workspace_id,
                    func.date(ReturnRequest.created_at) == target_date,
                )
            )
        ).scalar_one()

        # 4. Cancellation count
        cancellation_count = (
            await self._session.execute(
                select(func.count(Order.id)).where(
                    Order.workspace_id == workspace_id,
                    Order.shop_id == shop_id,
                    Order.status == OrderStatus.CANCELLED,
                    func.date(Order.created_at) == target_date,
                )
            )
        ).scalar_one()

        # 5. Active promotions
        active_promotions = (
            await self._session.execute(
                select(func.count(Promotion.id)).where(
                    Promotion.workspace_id == workspace_id,
                    Promotion.shop_id == shop_id,
                    Promotion.status == "ACTIVE",
                )
            )
        ).scalar_one()

        # 6. Active campaigns
        active_campaigns = (
            await self._session.execute(
                select(func.count(Campaign.id)).where(
                    Campaign.workspace_id == workspace_id,
                    Campaign.operation_status == "ENABLE",
                )
            )
        ).scalar_one()

        # Compute avg_order_value
        gmv_str = str(total_gmv)
        avg_order_value = None
        if order_count > 0:
            avg = float(gmv_str) / order_count
            avg_order_value = f"{avg:.2f}"

        metrics = UnifiedDailyMetrics(
            workspace_id=workspace_id,
            shop_id=shop_id,
            date=target_date,
            total_gmv=gmv_str,
            order_count=order_count,
            return_count=return_count,
            cancellation_count=cancellation_count,
            avg_order_value=avg_order_value,
            active_promotions=active_promotions,
            active_campaigns=active_campaigns,
        )
        self._session.add(metrics)
        return metrics

    async def get_metrics_history(
        self,
        workspace_id: uuid.UUID,
        shop_id: uuid.UUID | None = None,
        days: int = 30,
    ) -> list[UnifiedDailyMetrics]:
        """Get daily metrics for trend analysis."""
        cutoff = date.today() - timedelta(days=days)

        stmt = select(UnifiedDailyMetrics).where(
            UnifiedDailyMetrics.workspace_id == workspace_id,
            UnifiedDailyMetrics.date >= cutoff,
        )
        if shop_id is not None:
            stmt = stmt.where(UnifiedDailyMetrics.shop_id == shop_id)

        stmt = stmt.order_by(UnifiedDailyMetrics.date.asc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

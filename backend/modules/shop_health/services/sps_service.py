import logging
import uuid
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.commerce import Order, OrderStatus, Package, ReturnRequest
from backend.db.models.shop_health import SpsSnapshot

logger = logging.getLogger(__name__)


class SpsEstimationService:
    """Estimate TikTok Shop Performance Score (SPS) from cross-module data."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def calculate_estimated_sps(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> dict:
        """Calculate estimated SPS from cross-module data (30-day window).

        Returns dict with all 6 metrics + estimated score.
        """
        cutoff = date.today() - timedelta(days=30)

        # 1. Count total orders in the last 30 days
        total_orders = (
            await self._session.execute(
                select(func.count(Order.id)).where(
                    Order.workspace_id == workspace_id,
                    Order.shop_id == shop_id,
                    Order.created_at >= cutoff,
                )
            )
        ).scalar_one()

        # 2. Count seller-fault cancellations
        cancellations = (
            await self._session.execute(
                select(func.count(Order.id)).where(
                    Order.workspace_id == workspace_id,
                    Order.shop_id == shop_id,
                    Order.created_at >= cutoff,
                    Order.status == OrderStatus.CANCELLED,
                )
            )
        ).scalar_one()

        # 3. Count non-buyer-fault returns
        returns = (
            await self._session.execute(
                select(func.count(ReturnRequest.id)).where(
                    ReturnRequest.workspace_id == workspace_id,
                    ReturnRequest.created_at >= cutoff,
                )
            )
        ).scalar_one()

        # 4. Count total shipped packages
        total_shipped = (
            await self._session.execute(
                select(func.count(Package.id)).where(
                    Package.created_at >= cutoff,
                )
            )
        ).scalar_one()

        # 5. Count on-time shipped packages (those that reached SHIPPED or beyond)
        on_time_shipped = (
            await self._session.execute(
                select(func.count(Package.id)).where(
                    Package.created_at >= cutoff,
                    Package.status.in_(["shipped", "in_transit", "delivered"]),
                )
            )
        ).scalar_one()

        # Calculate rates
        if total_orders > 0:
            cancellation_rate = cancellations / total_orders
            return_rate = returns / total_orders
        else:
            cancellation_rate = 0.0
            return_rate = 0.0

        if total_shipped > 0:
            otdr = on_time_shipped / total_shipped
        else:
            otdr = 1.0  # No shipments = no late ones

        # Estimate score: 5.0 - (cancellation_rate * 5 + return_rate * 5 + (1 - otdr) * 5) / 3
        penalty = (cancellation_rate * 5 + return_rate * 5 + (1 - otdr) * 5) / 3
        estimated_score = max(0.0, min(5.0, 5.0 - penalty))

        return {
            "estimated_score": f"{estimated_score:.1f}",
            "return_rate": f"{return_rate * 100:.1f}",
            "cancellation_rate": f"{cancellation_rate * 100:.1f}",
            "otdr": f"{otdr * 100:.1f}",
            "total_orders": total_orders,
            "total_shipped": total_shipped,
        }

    async def save_daily_snapshot(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> SpsSnapshot:
        """Calculate and persist daily SPS snapshot."""
        metrics = await self.calculate_estimated_sps(workspace_id, shop_id)

        snapshot = SpsSnapshot(
            workspace_id=workspace_id,
            shop_id=shop_id,
            date=date.today(),
            estimated_score=metrics["estimated_score"],
            return_rate=metrics["return_rate"],
            cancellation_rate=metrics["cancellation_rate"],
            otdr=metrics["otdr"],
        )
        self._session.add(snapshot)
        return snapshot

    async def get_sps_history(
        self,
        workspace_id: uuid.UUID,
        shop_id: uuid.UUID | None = None,
        days: int = 30,
    ) -> list[SpsSnapshot]:
        """Get SPS snapshots for trend analysis."""
        cutoff = date.today() - timedelta(days=days)

        stmt = select(SpsSnapshot).where(
            SpsSnapshot.workspace_id == workspace_id,
            SpsSnapshot.date >= cutoff,
        )
        if shop_id is not None:
            stmt = stmt.where(SpsSnapshot.shop_id == shop_id)

        stmt = stmt.order_by(SpsSnapshot.date.asc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

import uuid
from datetime import datetime

from sqlalchemy import case, cast, func, select, String
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.commerce import (
    Order,
    OrderLineItem,
    OrderStatus,
    Product,
    ReturnRequest,
)

_COMPLETED_STATUSES = {OrderStatus.COMPLETED, OrderStatus.DELIVERED}


class CommerceAnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_revenue_summary(
        self,
        workspace_id: uuid.UUID,
        *,
        period_start: datetime,
        period_end: datetime,
    ) -> dict:
        """Aggregate revenue, order count, AOV, and return rate."""
        # Total revenue and order count
        order_query = select(
            func.count(Order.id).label("total_orders"),
            func.sum(cast(Order.total_amount, String)).label("raw_total"),
        ).where(
            Order.workspace_id == workspace_id,
            Order.status.in_([s.value for s in _COMPLETED_STATUSES]),
            Order.created_at >= period_start,
            Order.created_at <= period_end,
        )
        result = await self._session.execute(order_query)
        row = result.one()
        total_orders = row.total_orders or 0

        # Sum amounts manually since they're stored as strings
        amount_query = select(Order.total_amount).where(
            Order.workspace_id == workspace_id,
            Order.status.in_([s.value for s in _COMPLETED_STATUSES]),
            Order.created_at >= period_start,
            Order.created_at <= period_end,
        )
        amounts_result = await self._session.execute(amount_query)
        total_revenue = sum(
            float(a) for (a,) in amounts_result.all() if a
        )

        aov = total_revenue / total_orders if total_orders > 0 else 0.0

        # Return rate
        return_count_result = await self._session.execute(
            select(func.count(ReturnRequest.id)).where(
                ReturnRequest.workspace_id == workspace_id,
                ReturnRequest.created_at >= period_start,
                ReturnRequest.created_at <= period_end,
            )
        )
        return_count = return_count_result.scalar_one() or 0

        all_orders_result = await self._session.execute(
            select(func.count(Order.id)).where(
                Order.workspace_id == workspace_id,
                Order.created_at >= period_start,
                Order.created_at <= period_end,
            )
        )
        all_orders = all_orders_result.scalar_one() or 0
        return_rate = return_count / all_orders if all_orders > 0 else 0.0

        return {
            "total_revenue": f"{total_revenue:.2f}",
            "total_orders": total_orders,
            "average_order_value": f"{aov:.2f}",
            "return_rate": round(return_rate, 4),
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
        }

    async def get_revenue_timeseries(
        self,
        workspace_id: uuid.UUID,
        *,
        period_start: datetime,
        period_end: datetime,
    ) -> list[dict]:
        """Daily revenue and order count timeseries."""
        query = select(
            func.date_trunc("day", Order.created_at).label("day"),
            func.count(Order.id).label("order_count"),
        ).where(
            Order.workspace_id == workspace_id,
            Order.status.in_([s.value for s in _COMPLETED_STATUSES]),
            Order.created_at >= period_start,
            Order.created_at <= period_end,
        ).group_by("day").order_by("day")

        result = await self._session.execute(query)
        rows = result.all()

        # Get revenue per day by fetching amounts
        timeseries: list[dict] = []
        for row in rows:
            day_str = row.day.strftime("%Y-%m-%d") if row.day else ""
            day_start = row.day
            day_end = row.day.replace(hour=23, minute=59, second=59) if row.day else None

            day_amounts = await self._session.execute(
                select(Order.total_amount).where(
                    Order.workspace_id == workspace_id,
                    Order.status.in_([s.value for s in _COMPLETED_STATUSES]),
                    Order.created_at >= day_start,
                    Order.created_at <= day_end,
                )
            )
            day_revenue = sum(
                float(a) for (a,) in day_amounts.all() if a
            )

            timeseries.append(
                {
                    "date": day_str,
                    "revenue": f"{day_revenue:.2f}",
                    "order_count": row.order_count,
                }
            )

        return timeseries

    async def get_top_products(
        self,
        workspace_id: uuid.UUID,
        *,
        limit: int = 10,
    ) -> list[dict]:
        """Top products by total revenue from line items."""
        query = (
            select(
                OrderLineItem.product_name,
                func.sum(OrderLineItem.quantity).label("total_quantity"),
            )
            .join(Order, OrderLineItem.order_id == Order.id)
            .where(
                Order.workspace_id == workspace_id,
                Order.status.in_([s.value for s in _COMPLETED_STATUSES]),
            )
            .group_by(OrderLineItem.product_name)
            .order_by(func.sum(OrderLineItem.quantity).desc())
            .limit(limit)
        )
        result = await self._session.execute(query)
        rows = result.all()

        top: list[dict] = []
        for row in rows:
            # Compute revenue for this product
            rev_result = await self._session.execute(
                select(func.sum(cast(OrderLineItem.total_price, String)))
                .join(Order, OrderLineItem.order_id == Order.id)
                .where(
                    Order.workspace_id == workspace_id,
                    Order.status.in_([s.value for s in _COMPLETED_STATUSES]),
                    OrderLineItem.product_name == row.product_name,
                )
            )
            raw_rev = rev_result.scalar_one_or_none()

            # Fetch associated product for image
            prod_result = await self._session.execute(
                select(Product)
                .where(
                    Product.workspace_id == workspace_id,
                    Product.title == row.product_name,
                )
                .limit(1)
            )
            product = prod_result.scalar_one_or_none()

            total_prices = await self._session.execute(
                select(OrderLineItem.total_price)
                .join(Order, OrderLineItem.order_id == Order.id)
                .where(
                    Order.workspace_id == workspace_id,
                    Order.status.in_([s.value for s in _COMPLETED_STATUSES]),
                    OrderLineItem.product_name == row.product_name,
                )
            )
            total_revenue = sum(
                float(p) for (p,) in total_prices.all() if p
            )

            top.append(
                {
                    "product_id": str(product.id) if product else "",
                    "title": row.product_name,
                    "total_revenue": f"{total_revenue:.2f}",
                    "total_quantity": row.total_quantity or 0,
                    "main_image_url": product.main_image_url if product else None,
                }
            )

        return top

    async def get_order_status_distribution(
        self, workspace_id: uuid.UUID
    ) -> list[dict]:
        """Count of orders by status."""
        query = (
            select(
                Order.status,
                func.count(Order.id).label("count"),
            )
            .where(Order.workspace_id == workspace_id)
            .group_by(Order.status)
        )
        result = await self._session.execute(query)
        rows = result.all()

        total = sum(r.count for r in rows)
        return [
            {
                "status": r.status.value if hasattr(r.status, "value") else str(r.status),
                "count": r.count,
                "percentage": round(r.count / total * 100, 1) if total > 0 else 0.0,
            }
            for r in rows
        ]

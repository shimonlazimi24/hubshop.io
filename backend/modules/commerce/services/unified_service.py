"""Thin aggregation layer for cross-platform commerce data."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.modules.commerce.schemas import (
    OrderSummaryResponse,
    PaginatedResponse,
)
from backend.modules.commerce.services.order_service import OrderService


class UnifiedCommerceService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_orders(
        self,
        workspace_id: uuid.UUID,
        *,
        platform: str | None = None,
        shop_id: uuid.UUID | None = None,
        status_filter: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[OrderSummaryResponse]:
        items: list[OrderSummaryResponse] = []
        aggregate_total = 0

        if platform is None or platform == "shop":
            order_service = OrderService(self._session)
            result = await order_service.list_orders(
                workspace_id,
                shop_id=shop_id,
                status=status_filter,
                date_from=date_from,
                date_to=date_to,
                page=page,
                page_size=page_size,
            )
            for o in result.items:
                resp = OrderSummaryResponse.model_validate(o)
                resp.source_platform = "shop"
                items.append(resp)
            aggregate_total += result.total

            if platform == "shop":
                return PaginatedResponse(
                    items=items,
                    total=result.total,
                    page=result.page,
                    page_size=result.page_size,
                    total_pages=result.total_pages,
                )

        total_pages = max(1, (aggregate_total + page_size - 1) // page_size)
        return PaginatedResponse(
            items=items,
            total=aggregate_total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

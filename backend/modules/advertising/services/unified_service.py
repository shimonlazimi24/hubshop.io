"""Thin aggregation layer for cross-platform advertising data."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.modules.advertising.schemas import CampaignSummaryResponse
from backend.modules.advertising.services.campaign_service import CampaignService
from backend.modules.commerce.schemas import PaginatedResponse


class UnifiedAdvertisingService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_campaigns(
        self,
        workspace_id: uuid.UUID,
        *,
        platform: str | None = None,
        ad_account_id: uuid.UUID | None = None,
        objective: str | None = None,
        status_filter: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[CampaignSummaryResponse]:
        items: list[CampaignSummaryResponse] = []
        aggregate_total = 0

        if platform is None or platform == "marketing":
            campaign_service = CampaignService(self._session)
            result = await campaign_service.list_campaigns(
                workspace_id,
                ad_account_id=ad_account_id,
                objective=objective,
                status_filter=status_filter,
                search=search,
                page=page,
                page_size=page_size,
            )
            for c in result.items:
                resp = CampaignSummaryResponse.model_validate(c)
                resp.source_platform = "marketing"
                items.append(resp)
            aggregate_total += result.total

            if platform == "marketing":
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

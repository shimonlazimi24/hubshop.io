"""Tests for UnifiedAdvertisingService — cross-platform campaign aggregation."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.advertising.services.unified_service import (
    UnifiedAdvertisingService,
)


class TestListCampaignsUnified:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_returns_marketing_campaigns_when_platform_is_marketing(
        self, mock_session: AsyncMock, workspace_id: uuid.UUID
    ) -> None:
        mock_campaign = SimpleNamespace(
            id=str(uuid.uuid4()),
            platform_campaign_id="camp_1",
            campaign_name="Marketing Campaign",
            objective_type="TRAFFIC",
            budget_mode="BUDGET_MODE_DAY",
            budget="100",
            operation_status="ENABLE",
            secondary_status=None,
            source_platform="marketing",
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        mock_result = SimpleNamespace(
            items=[mock_campaign], total=1, page=1, page_size=20, total_pages=1
        )

        with patch(
            "backend.modules.advertising.services.unified_service.CampaignService"
        ) as MockCampaignService:
            mock_svc = AsyncMock()
            mock_svc.list_campaigns.return_value = mock_result
            MockCampaignService.return_value = mock_svc

            service = UnifiedAdvertisingService(mock_session)
            result = await service.list_campaigns(workspace_id, platform="marketing")

        assert len(result.items) == 1
        assert result.items[0].source_platform == "marketing"

    @pytest.mark.asyncio
    async def test_returns_all_when_platform_is_none(
        self, mock_session: AsyncMock, workspace_id: uuid.UUID
    ) -> None:
        mock_campaign = SimpleNamespace(
            id=str(uuid.uuid4()),
            platform_campaign_id="camp_1",
            campaign_name="Marketing Campaign",
            objective_type="TRAFFIC",
            budget_mode="BUDGET_MODE_DAY",
            budget="100",
            operation_status="ENABLE",
            secondary_status=None,
            source_platform="marketing",
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        mock_result = SimpleNamespace(
            items=[mock_campaign], total=1, page=1, page_size=20, total_pages=1
        )

        with patch(
            "backend.modules.advertising.services.unified_service.CampaignService"
        ) as MockCampaignService:
            mock_svc = AsyncMock()
            mock_svc.list_campaigns.return_value = mock_result
            MockCampaignService.return_value = mock_svc

            service = UnifiedAdvertisingService(mock_session)
            result = await service.list_campaigns(workspace_id, platform=None)

        assert len(result.items) >= 1
        assert all(
            item.source_platform in ("marketing", "shop") for item in result.items
        )

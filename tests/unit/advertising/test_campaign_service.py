"""Tests for CampaignService - upsert from API, list with filters, status updates."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.db.models.advertising import Campaign
from backend.modules.advertising.services.campaign_service import CampaignService


class TestUpsertCampaignFromApi:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def sample_ad_account(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            advertiser_id="111222333",
            advertiser_name="Test Advertiser",
            connected_account_id=uuid.uuid4(),
        )

    @pytest.fixture
    def sample_campaign_data(self) -> dict:
        return {
            "campaign_id": "camp_12345",
            "campaign_name": "Test Campaign",
            "objective_type": "TRAFFIC",
            "budget_mode": "BUDGET_MODE_DAY",
            "budget": 100.0,
            "operation_status": "ENABLE",
            "secondary_status": "CAMPAIGN_STATUS_ENABLE",
        }

    @pytest.mark.asyncio
    async def test_creates_new_campaign(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        sample_campaign_data: dict,
    ) -> None:
        service = CampaignService(mock_session)
        campaign = await service.upsert_campaign_from_api(
            ad_account=sample_ad_account, campaign_data=sample_campaign_data
        )

        assert mock_session.add.called
        added = mock_session.add.call_args_list[0][0][0]
        assert isinstance(added, Campaign)
        assert added.platform_campaign_id == "camp_12345"
        assert added.campaign_name == "Test Campaign"
        assert added.objective_type == "TRAFFIC"
        assert added.budget == "100.0"
        assert added.operation_status == "ENABLE"

    @pytest.mark.asyncio
    async def test_updates_existing_campaign(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        sample_campaign_data: dict,
    ) -> None:
        existing = SimpleNamespace(
            id=uuid.uuid4(),
            platform_campaign_id="camp_12345",
            campaign_name="Old Name",
            objective_type="CONVERSIONS",
            budget_mode="BUDGET_MODE_TOTAL",
            budget="50.0",
            operation_status="DISABLE",
            secondary_status=None,
            detail_json=None,
        )
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = existing
        mock_session.execute.return_value = result_mock

        service = CampaignService(mock_session)
        await service.upsert_campaign_from_api(
            ad_account=sample_ad_account, campaign_data=sample_campaign_data
        )

        assert existing.campaign_name == "Test Campaign"
        assert existing.objective_type == "TRAFFIC"
        assert existing.budget == "100.0"
        assert existing.operation_status == "ENABLE"
        # Should not add new object when updating
        assert not mock_session.add.called

    @pytest.mark.asyncio
    async def test_handles_missing_budget(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
    ) -> None:
        data = {
            "campaign_id": "camp_no_budget",
            "campaign_name": "No Budget Campaign",
            "objective_type": "REACH",
            "budget_mode": "BUDGET_MODE_INFINITE",
            "operation_status": "ENABLE",
        }
        service = CampaignService(mock_session)
        await service.upsert_campaign_from_api(
            ad_account=sample_ad_account, campaign_data=data
        )
        added = mock_session.add.call_args_list[0][0][0]
        assert added.budget is None
        assert added.budget_mode == "BUDGET_MODE_INFINITE"

    @pytest.mark.asyncio
    async def test_stores_detail_json(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        sample_campaign_data: dict,
    ) -> None:
        service = CampaignService(mock_session)
        await service.upsert_campaign_from_api(
            ad_account=sample_ad_account, campaign_data=sample_campaign_data
        )
        added = mock_session.add.call_args_list[0][0][0]
        assert added.detail_json == sample_campaign_data


class TestListCampaigns:
    @pytest.mark.asyncio
    async def test_list_returns_paginated_result(self) -> None:
        session = AsyncMock()
        # count query returns 2
        count_result = MagicMock()
        count_result.scalar_one.return_value = 2
        # items query returns 2 campaigns
        items_result = MagicMock()
        camp1 = SimpleNamespace(id=uuid.uuid4(), campaign_name="Camp 1")
        camp2 = SimpleNamespace(id=uuid.uuid4(), campaign_name="Camp 2")
        items_result.scalars.return_value.all.return_value = [camp1, camp2]

        session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = CampaignService(session)
        result = await service.list_campaigns(uuid.uuid4(), page=1, page_size=20)

        assert result.total == 2
        assert len(result.items) == 2
        assert result.page == 1

    @pytest.mark.asyncio
    async def test_list_empty(self) -> None:
        session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = CampaignService(session)
        result = await service.list_campaigns(uuid.uuid4())

        assert result.total == 0
        assert result.items == []
        assert result.total_pages == 0


class TestGetCampaign:
    @pytest.mark.asyncio
    async def test_returns_campaign(self) -> None:
        campaign = SimpleNamespace(id=uuid.uuid4(), campaign_name="Found")
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = campaign
        session.execute.return_value = result

        service = CampaignService(session)
        found = await service.get_campaign(campaign.id)
        assert found is not None
        assert found.campaign_name == "Found"

    @pytest.mark.asyncio
    async def test_returns_none_for_missing(self) -> None:
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result

        service = CampaignService(session)
        found = await service.get_campaign(uuid.uuid4())
        assert found is None

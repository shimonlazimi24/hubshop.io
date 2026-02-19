"""Integration tests for advertising sync pipeline with mocked TikTok API."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.db.models.advertising import AdGroup, Campaign
from backend.modules.advertising.services.ad_group_service import AdGroupService
from backend.modules.advertising.services.ad_service import AdService
from backend.modules.advertising.services.campaign_service import CampaignService


class TestCampaignSync:
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
            connected_account_id=uuid.uuid4(),
            last_sync_at=None,
        )

    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.ad_account_service.AdAccountService.build_gateway_for_ad_account"
    )
    async def test_sync_campaigns_paginates(
        self,
        mock_build_gw: AsyncMock,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
    ) -> None:
        """Test that sync_campaigns handles multi-page responses."""
        gateway = AsyncMock()
        mock_build_gw.return_value = gateway

        # Page 1: 2 campaigns, page 2: 1 campaign
        gateway.get = AsyncMock(
            side_effect=[
                {
                    "data": {
                        "list": [
                            {
                                "campaign_id": "c1",
                                "campaign_name": "Camp 1",
                                "operation_status": "ENABLE",
                            },
                            {
                                "campaign_id": "c2",
                                "campaign_name": "Camp 2",
                                "operation_status": "DISABLE",
                            },
                        ],
                        "page_info": {"total_page": 2},
                    }
                },
                {
                    "data": {
                        "list": [
                            {
                                "campaign_id": "c3",
                                "campaign_name": "Camp 3",
                                "operation_status": "ENABLE",
                            },
                        ],
                        "page_info": {"total_page": 2},
                    }
                },
            ]
        )

        service = CampaignService(mock_session)
        synced = await service.sync_campaigns(sample_ad_account)

        assert synced == 3
        assert gateway.get.call_count == 2
        # 3 new campaigns should be added
        assert mock_session.add.call_count == 3

    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.ad_account_service.AdAccountService.build_gateway_for_ad_account"
    )
    async def test_sync_campaigns_empty(
        self,
        mock_build_gw: AsyncMock,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
    ) -> None:
        """Test sync with no campaigns."""
        gateway = AsyncMock()
        mock_build_gw.return_value = gateway
        gateway.get = AsyncMock(
            return_value={"data": {"list": [], "page_info": {"total_page": 1}}}
        )

        service = CampaignService(mock_session)
        synced = await service.sync_campaigns(sample_ad_account)

        assert synced == 0


class TestAdGroupSync:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def sample_ad_account(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            advertiser_id="111222333",
            connected_account_id=uuid.uuid4(),
        )

    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.ad_account_service.AdAccountService.build_gateway_for_ad_account"
    )
    async def test_sync_ad_groups_resolves_campaigns(
        self,
        mock_build_gw: AsyncMock,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
    ) -> None:
        """Test that sync resolves campaign FKs from local data."""
        gateway = AsyncMock()
        mock_build_gw.return_value = gateway

        campaign = SimpleNamespace(
            id=uuid.uuid4(),
            platform_campaign_id="c1",
        )

        # First execute call: campaign query
        campaign_result = MagicMock()
        campaign_result.scalars.return_value.all.return_value = [campaign]

        # Second execute call (get): API response
        gateway.get = AsyncMock(
            return_value={
                "data": {
                    "list": [
                        {
                            "adgroup_id": "ag1",
                            "adgroup_name": "Ad Group 1",
                            "campaign_id": "c1",
                            "operation_status": "ENABLE",
                        }
                    ],
                    "page_info": {"total_page": 1},
                }
            }
        )

        # Third execute: upsert lookup (not found)
        upsert_result = MagicMock()
        upsert_result.scalar_one_or_none.return_value = None

        mock_session.execute = AsyncMock(
            side_effect=[campaign_result, upsert_result]
        )

        service = AdGroupService(mock_session)
        synced = await service.sync_ad_groups(sample_ad_account)

        assert synced == 1
        assert mock_session.add.called

    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.ad_account_service.AdAccountService.build_gateway_for_ad_account"
    )
    async def test_sync_ad_groups_skips_unknown_campaign(
        self,
        mock_build_gw: AsyncMock,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
    ) -> None:
        """Test that ad groups with unknown campaign IDs are skipped."""
        gateway = AsyncMock()
        mock_build_gw.return_value = gateway

        # No campaigns locally
        campaign_result = MagicMock()
        campaign_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(return_value=campaign_result)

        gateway.get = AsyncMock(
            return_value={
                "data": {
                    "list": [
                        {
                            "adgroup_id": "ag1",
                            "adgroup_name": "Orphan Group",
                            "campaign_id": "unknown_campaign",
                            "operation_status": "ENABLE",
                        }
                    ],
                    "page_info": {"total_page": 1},
                }
            }
        )

        service = AdGroupService(mock_session)
        synced = await service.sync_ad_groups(sample_ad_account)

        assert synced == 0
        assert not mock_session.add.called


class TestAdSync:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def sample_ad_account(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            advertiser_id="111222333",
            connected_account_id=uuid.uuid4(),
        )

    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.ad_account_service.AdAccountService.build_gateway_for_ad_account"
    )
    async def test_sync_ads_resolves_ad_groups(
        self,
        mock_build_gw: AsyncMock,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
    ) -> None:
        gateway = AsyncMock()
        mock_build_gw.return_value = gateway

        ad_group = SimpleNamespace(
            id=uuid.uuid4(),
            platform_adgroup_id="ag1",
        )

        # Ad group lookup
        adgroup_result = MagicMock()
        adgroup_result.scalars.return_value.all.return_value = [ad_group]

        # Upsert lookup (not found)
        upsert_result = MagicMock()
        upsert_result.scalar_one_or_none.return_value = None

        mock_session.execute = AsyncMock(
            side_effect=[adgroup_result, upsert_result]
        )

        gateway.get = AsyncMock(
            return_value={
                "data": {
                    "list": [
                        {
                            "ad_id": "ad1",
                            "ad_name": "Test Ad",
                            "adgroup_id": "ag1",
                            "ad_format": "SINGLE_VIDEO",
                            "operation_status": "ENABLE",
                        }
                    ],
                    "page_info": {"total_page": 1},
                }
            }
        )

        service = AdService(mock_session)
        synced = await service.sync_ads(sample_ad_account)

        assert synced == 1
        assert mock_session.add.called
        added = mock_session.add.call_args_list[0][0][0]
        assert added.platform_ad_id == "ad1"
        assert added.ad_format == "SINGLE_VIDEO"

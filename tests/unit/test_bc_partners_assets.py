from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.advertising.services.business_center_service import (
    BusinessCenterService,
)


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_ad_account() -> MagicMock:
    account = MagicMock()
    account.advertiser_id = "adv_123"
    return account


class TestListPartners:
    @pytest.mark.asyncio
    async def test_returns_partners(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"bc_id": "partner_001", "relationship_type": "PARTNER"},
                    {"bc_id": "partner_002", "relationship_type": "PARTNER"},
                ]
            }
        }
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.list_partners(
                ad_account=mock_ad_account, bc_id="bc_001"
            )
            assert len(result["list"]) == 2
            assert result["list"][0]["bc_id"] == "partner_001"
            mock_gateway.get.assert_called_once_with(
                "/bc/partner/get/",
                params={"bc_id": "bc_001", "page": "1", "page_size": "20"},
            )


class TestAddPartner:
    @pytest.mark.asyncio
    async def test_add_partner_default_relationship(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"success": True}}
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.add_partner(
                ad_account=mock_ad_account,
                bc_id="bc_001",
                partner_bc_id="partner_001",
            )
            assert result["success"] is True
            mock_gateway.post.assert_called_once_with(
                "/bc/partner/add/",
                json_body={
                    "bc_id": "bc_001",
                    "partner_bc_id": "partner_001",
                    "relationship_type": "PARTNER",
                },
            )


class TestDeletePartner:
    @pytest.mark.asyncio
    async def test_delete_partner(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"success": True}}
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.delete_partner(
                ad_account=mock_ad_account,
                bc_id="bc_001",
                partner_bc_id="partner_001",
            )
            assert result["success"] is True
            mock_gateway.post.assert_called_once_with(
                "/bc/partner/delete/",
                json_body={
                    "bc_id": "bc_001",
                    "partner_bc_id": "partner_001",
                },
            )


class TestListAssets:
    @pytest.mark.asyncio
    async def test_returns_assets_no_filter(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"asset_id": "a1", "asset_type": "AD_ACCOUNT"},
                ]
            }
        }
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.list_assets(
                ad_account=mock_ad_account, bc_id="bc_001"
            )
            assert len(result["list"]) == 1
            mock_gateway.get.assert_called_once_with(
                "/bc/asset/get/",
                params={"bc_id": "bc_001", "page": "1", "page_size": "20"},
            )

    @pytest.mark.asyncio
    async def test_returns_assets_with_type_filter(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"list": []}}
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            await service.list_assets(
                ad_account=mock_ad_account,
                bc_id="bc_001",
                asset_type="PIXEL",
            )
            mock_gateway.get.assert_called_once_with(
                "/bc/asset/get/",
                params={
                    "bc_id": "bc_001",
                    "asset_type": "PIXEL",
                    "page": "1",
                    "page_size": "20",
                },
            )


class TestAssignAsset:
    @pytest.mark.asyncio
    async def test_assign_asset(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"success": True}}
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.assign_asset(
                ad_account=mock_ad_account,
                bc_id="bc_001",
                asset_ids=["a1", "a2"],
                member_ids=["m1"],
            )
            assert result["success"] is True
            mock_gateway.post.assert_called_once_with(
                "/bc/asset/assign/",
                json_body={
                    "bc_id": "bc_001",
                    "asset_ids": ["a1", "a2"],
                    "member_ids": ["m1"],
                },
            )


class TestUnassignAsset:
    @pytest.mark.asyncio
    async def test_unassign_asset(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"success": True}}
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.unassign_asset(
                ad_account=mock_ad_account,
                bc_id="bc_001",
                asset_ids=["a1"],
                member_ids=["m1", "m2"],
            )
            assert result["success"] is True
            mock_gateway.post.assert_called_once_with(
                "/bc/asset/unassign/",
                json_body={
                    "bc_id": "bc_001",
                    "asset_ids": ["a1"],
                    "member_ids": ["m1", "m2"],
                },
            )


class TestCreateAdAccountInBC:
    @pytest.mark.asyncio
    async def test_create_without_industry(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"advertiser_id": "new_adv_001"}}
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.create_ad_account_in_bc(
                ad_account=mock_ad_account,
                bc_id="bc_001",
                advertiser_name="Test Advertiser",
                timezone="America/New_York",
                currency="USD",
            )
            assert result["advertiser_id"] == "new_adv_001"
            mock_gateway.post.assert_called_once_with(
                "/bc/asset/ad_account/create/",
                json_body={
                    "bc_id": "bc_001",
                    "advertiser_name": "Test Advertiser",
                    "timezone": "America/New_York",
                    "currency": "USD",
                },
            )

    @pytest.mark.asyncio
    async def test_create_with_industry(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"advertiser_id": "new_adv_002"}}
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.create_ad_account_in_bc(
                ad_account=mock_ad_account,
                bc_id="bc_001",
                advertiser_name="Test Advertiser",
                timezone="UTC",
                currency="EUR",
                industry_id="ind_42",
            )
            assert result["advertiser_id"] == "new_adv_002"
            mock_gateway.post.assert_called_once_with(
                "/bc/asset/ad_account/create/",
                json_body={
                    "bc_id": "bc_001",
                    "advertiser_name": "Test Advertiser",
                    "timezone": "UTC",
                    "currency": "EUR",
                    "industry_id": "ind_42",
                },
            )


class TestGetPartnerAssets:
    @pytest.mark.asyncio
    async def test_get_partner_assets(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        mock_ad_account: MagicMock,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"list": [{"asset_id": "a1", "asset_type": "AD_ACCOUNT"}]}
        }
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.get_partner_assets(
                ad_account=mock_ad_account,
                bc_id="bc_001",
                partner_bc_id="partner_001",
            )
            assert len(result["list"]) == 1
            mock_gateway.get.assert_called_once_with(
                "/bc/partner/asset/get/",
                params={
                    "bc_id": "bc_001",
                    "partner_bc_id": "partner_001",
                },
            )

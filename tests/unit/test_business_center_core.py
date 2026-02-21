import pytest
from unittest.mock import AsyncMock, MagicMock, patch

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


class TestListBusinessCenters:
    @pytest.mark.asyncio
    async def test_returns_list(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"bc_id": "bc_001", "bc_name": "My BC"},
                    {"bc_id": "bc_002", "bc_name": "Other BC"},
                ]
            }
        }
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.list_business_centers(ad_account=mock_ad_account)
            assert len(result["list"]) == 2
            assert result["list"][0]["bc_id"] == "bc_001"
            mock_gateway.get.assert_called_once_with(
                "/bc/get/",
                params={"page": "1", "page_size": "20"},
            )

    @pytest.mark.asyncio
    async def test_empty_list(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.get.return_value = {"data": {"list": []}}
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.list_business_centers(ad_account=mock_ad_account)
            assert result["list"] == []

    @pytest.mark.asyncio
    async def test_missing_data_key(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.get.return_value = {}
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.list_business_centers(ad_account=mock_ad_account)
            assert result == {}


class TestGetActivityLog:
    @pytest.mark.asyncio
    async def test_returns_activity_log(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"action": "MEMBER_INVITE", "actor": "user@test.com"},
                ]
            }
        }
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.get_activity_log(
                ad_account=mock_ad_account, bc_id="bc_001"
            )
            assert len(result["list"]) == 1
            assert result["list"][0]["action"] == "MEMBER_INVITE"
            mock_gateway.get.assert_called_once_with(
                "/bc/activity_log/get/",
                params={"bc_id": "bc_001", "page": "1", "page_size": "20"},
            )


class TestListMembers:
    @pytest.mark.asyncio
    async def test_returns_members(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"member_id": "m1", "email": "a@test.com", "role": "ADMIN"},
                    {"member_id": "m2", "email": "b@test.com", "role": "ANALYST"},
                ]
            }
        }
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.list_members(
                ad_account=mock_ad_account, bc_id="bc_001"
            )
            assert len(result["list"]) == 2
            assert result["list"][0]["role"] == "ADMIN"
            mock_gateway.get.assert_called_once_with(
                "/bc/member/get/",
                params={"bc_id": "bc_001", "page": "1", "page_size": "20"},
            )

    @pytest.mark.asyncio
    async def test_custom_pagination(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.get.return_value = {"data": {"list": []}}
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            await service.list_members(
                ad_account=mock_ad_account, bc_id="bc_001", page=3, page_size=50
            )
            mock_gateway.get.assert_called_once_with(
                "/bc/member/get/",
                params={"bc_id": "bc_001", "page": "3", "page_size": "50"},
            )


class TestInviteMember:
    @pytest.mark.asyncio
    async def test_invite_single_email(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"success": True}}
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.invite_member(
                ad_account=mock_ad_account,
                bc_id="bc_001",
                emails=["new@test.com"],
                role="ANALYST",
            )
            assert result["success"] is True
            mock_gateway.post.assert_called_once_with(
                "/bc/member/invite/",
                json_body={
                    "bc_id": "bc_001",
                    "member_emails": ["new@test.com"],
                    "role": "ANALYST",
                },
            )

    @pytest.mark.asyncio
    async def test_invite_multiple_emails(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"success": True}}
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            await service.invite_member(
                ad_account=mock_ad_account,
                bc_id="bc_001",
                emails=["a@test.com", "b@test.com"],
                role="ADMIN",
            )
            mock_gateway.post.assert_called_once_with(
                "/bc/member/invite/",
                json_body={
                    "bc_id": "bc_001",
                    "member_emails": ["a@test.com", "b@test.com"],
                    "role": "ADMIN",
                },
            )


class TestUpdateMember:
    @pytest.mark.asyncio
    async def test_update_member_role(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"success": True}}
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.update_member(
                ad_account=mock_ad_account,
                bc_id="bc_001",
                member_id="m1",
                role="ADMIN",
            )
            assert result["success"] is True
            mock_gateway.post.assert_called_once_with(
                "/bc/member/update/",
                json_body={
                    "bc_id": "bc_001",
                    "member_id": "m1",
                    "role": "ADMIN",
                },
            )


class TestDeleteMember:
    @pytest.mark.asyncio
    async def test_delete_member(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {"success": True}}
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.delete_member(
                ad_account=mock_ad_account,
                bc_id="bc_001",
                member_id="m1",
            )
            assert result["success"] is True
            mock_gateway.post.assert_called_once_with(
                "/bc/member/delete/",
                json_body={
                    "bc_id": "bc_001",
                    "member_id": "m1",
                },
            )

    @pytest.mark.asyncio
    async def test_delete_member_missing_data(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock, mock_ad_account: MagicMock
    ) -> None:
        mock_gateway.post.return_value = {}
        with patch.object(
            BusinessCenterService, "_get_gateway", return_value=mock_gateway
        ):
            service = BusinessCenterService(mock_session)
            result = await service.delete_member(
                ad_account=mock_ad_account,
                bc_id="bc_001",
                member_id="m1",
            )
            assert result == {}

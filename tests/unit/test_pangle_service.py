from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.advertising.services.pangle_service import PangleService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


class TestGetBlockList:
    @pytest.mark.asyncio
    async def test_get_block_list_returns_data(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"block_list": ["app1", "app2"], "total": 2}
        }
        with patch.object(PangleService, "_get_gateway", return_value=mock_gateway):
            service = PangleService(mock_session)
            result = await service.get_block_list(
                ad_account=MagicMock(advertiser_id="adv1")
            )
        assert result["block_list"] == ["app1", "app2"]
        assert result["total"] == 2
        mock_gateway.get.assert_called_once_with(
            "/pangle/block_list/get/",
            params={
                "advertiser_id": "adv1",
                "page": "1",
                "page_size": "20",
            },
        )

    @pytest.mark.asyncio
    async def test_get_block_list_custom_pagination(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {"data": {"block_list": ["app5"], "total": 1}}
        with patch.object(PangleService, "_get_gateway", return_value=mock_gateway):
            service = PangleService(mock_session)
            result = await service.get_block_list(
                ad_account=MagicMock(advertiser_id="adv1"),
                page=3,
                page_size=10,
            )
        assert result["block_list"] == ["app5"]
        mock_gateway.get.assert_called_once_with(
            "/pangle/block_list/get/",
            params={
                "advertiser_id": "adv1",
                "page": "3",
                "page_size": "10",
            },
        )

    @pytest.mark.asyncio
    async def test_get_block_list_missing_data_key(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {}
        with patch.object(PangleService, "_get_gateway", return_value=mock_gateway):
            service = PangleService(mock_session)
            result = await service.get_block_list(
                ad_account=MagicMock(advertiser_id="adv1")
            )
        assert result == {}


class TestUpdateBlockList:
    @pytest.mark.asyncio
    async def test_update_block_list_add(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(PangleService, "_get_gateway", return_value=mock_gateway):
            service = PangleService(mock_session)
            result = await service.update_block_list(
                ad_account=MagicMock(advertiser_id="adv1"),
                block_list=["app3", "app4"],
                action="ADD",
            )
        mock_gateway.post.assert_called_once()
        call_body = mock_gateway.post.call_args[1]["json_body"]
        assert call_body["advertiser_id"] == "adv1"
        assert call_body["block_list"] == ["app3", "app4"]
        assert call_body["action"] == "ADD"
        assert result == {}

    @pytest.mark.asyncio
    async def test_update_block_list_remove(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(PangleService, "_get_gateway", return_value=mock_gateway):
            service = PangleService(mock_session)
            result = await service.update_block_list(
                ad_account=MagicMock(advertiser_id="adv1"),
                block_list=["app1"],
                action="REMOVE",
            )
        call_body = mock_gateway.post.call_args[1]["json_body"]
        assert call_body["action"] == "REMOVE"
        assert call_body["block_list"] == ["app1"]
        assert result == {}

    @pytest.mark.asyncio
    async def test_update_block_list_missing_data_key(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {}
        with patch.object(PangleService, "_get_gateway", return_value=mock_gateway):
            service = PangleService(mock_session)
            result = await service.update_block_list(
                ad_account=MagicMock(advertiser_id="adv1"),
                block_list=["app1"],
                action="ADD",
            )
        assert result == {}


class TestGetAudiencePackages:
    @pytest.mark.asyncio
    async def test_get_audience_packages_returns_data(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "audience_packages": [
                    {"id": "pkg1", "name": "Gamers"},
                    {"id": "pkg2", "name": "Shoppers"},
                ],
                "total": 2,
            }
        }
        with patch.object(PangleService, "_get_gateway", return_value=mock_gateway):
            service = PangleService(mock_session)
            result = await service.get_audience_packages(
                ad_account=MagicMock(advertiser_id="adv1")
            )
        assert len(result["audience_packages"]) == 2
        assert result["audience_packages"][0]["name"] == "Gamers"
        mock_gateway.get.assert_called_once_with(
            "/pangle/audience_package/get/",
            params={
                "advertiser_id": "adv1",
                "page": "1",
                "page_size": "20",
            },
        )

    @pytest.mark.asyncio
    async def test_get_audience_packages_missing_data_key(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {}
        with patch.object(PangleService, "_get_gateway", return_value=mock_gateway):
            service = PangleService(mock_session)
            result = await service.get_audience_packages(
                ad_account=MagicMock(advertiser_id="adv1")
            )
        assert result == {}

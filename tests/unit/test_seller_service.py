from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.commerce.services.seller_service import SellerService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


class TestGetActiveShops:
    @pytest.mark.asyncio
    async def test_get_active_shops_returns_list(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "shops": [
                    {"id": "s1", "name": "US Shop", "region": "US"},
                    {"id": "s2", "name": "UK Shop", "region": "GB"},
                ]
            }
        }
        with patch.object(SellerService, "_get_gateway", return_value=mock_gateway):
            service = SellerService(mock_session)
            result = await service.get_active_shops(shop_id=MagicMock())
            assert len(result) == 2
            assert result[0]["name"] == "US Shop"
            assert result[1]["region"] == "GB"
            mock_gateway.get.assert_called_once_with("/seller/202309/shops")

    @pytest.mark.asyncio
    async def test_get_active_shops_empty(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {"data": {"shops": []}}
        with patch.object(SellerService, "_get_gateway", return_value=mock_gateway):
            service = SellerService(mock_session)
            result = await service.get_active_shops(shop_id=MagicMock())
            assert result == []

    @pytest.mark.asyncio
    async def test_get_active_shops_missing_data_key(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {}
        with patch.object(SellerService, "_get_gateway", return_value=mock_gateway):
            service = SellerService(mock_session)
            result = await service.get_active_shops(shop_id=MagicMock())
            assert result == []


class TestGetSellerPermissions:
    @pytest.mark.asyncio
    async def test_get_seller_permissions_returns_list(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "permissions": [
                    {"key": "PRODUCT_MANAGEMENT", "enabled": True},
                    {"key": "ORDER_MANAGEMENT", "enabled": True},
                    {"key": "FINANCE_MANAGEMENT", "enabled": False},
                ]
            }
        }
        with patch.object(SellerService, "_get_gateway", return_value=mock_gateway):
            service = SellerService(mock_session)
            result = await service.get_seller_permissions(shop_id=MagicMock())
            assert len(result) == 3
            assert result[0]["key"] == "PRODUCT_MANAGEMENT"
            assert result[2]["enabled"] is False
            mock_gateway.get.assert_called_once_with("/seller/202309/permissions")

    @pytest.mark.asyncio
    async def test_get_seller_permissions_empty(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {"data": {"permissions": []}}
        with patch.object(SellerService, "_get_gateway", return_value=mock_gateway):
            service = SellerService(mock_session)
            result = await service.get_seller_permissions(shop_id=MagicMock())
            assert result == []

    @pytest.mark.asyncio
    async def test_get_seller_permissions_missing_data_key(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {}
        with patch.object(SellerService, "_get_gateway", return_value=mock_gateway):
            service = SellerService(mock_session)
            result = await service.get_seller_permissions(shop_id=MagicMock())
            assert result == []


class TestGetGateway:
    @pytest.mark.asyncio
    async def test_get_gateway_shop_not_found(self, mock_session: AsyncMock) -> None:
        with patch(
            "backend.modules.commerce.services.seller_service.ShopService"
        ) as mock_shop_service_cls:
            mock_shop_service = AsyncMock()
            mock_shop_service.get_shop.return_value = None
            mock_shop_service_cls.return_value = mock_shop_service

            service = SellerService(mock_session)
            with pytest.raises(ValueError, match="not found"):
                await service._get_gateway(MagicMock())

    @pytest.mark.asyncio
    async def test_get_gateway_returns_gateway(self, mock_session: AsyncMock) -> None:
        with patch(
            "backend.modules.commerce.services.seller_service.ShopService"
        ) as mock_shop_service_cls:
            mock_shop = MagicMock()
            mock_gateway = AsyncMock()
            mock_shop_service = AsyncMock()
            mock_shop_service.get_shop.return_value = mock_shop
            mock_shop_service.build_gateway_for_shop.return_value = mock_gateway
            mock_shop_service_cls.return_value = mock_shop_service

            service = SellerService(mock_session)
            result = await service._get_gateway(MagicMock())
            assert result is mock_gateway

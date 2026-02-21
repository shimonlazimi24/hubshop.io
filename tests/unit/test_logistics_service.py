import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.modules.commerce.services.logistics_service import LogisticsService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


class TestGetWarehouses:
    @pytest.mark.asyncio
    async def test_get_warehouses_returns_list(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "warehouses": [
                    {"id": "wh_1", "name": "Main Warehouse"},
                    {"id": "wh_2", "name": "West Coast"},
                ]
            }
        }
        with patch.object(
            LogisticsService, "_get_gateway", return_value=mock_gateway
        ):
            service = LogisticsService(mock_session)
            result = await service.get_warehouses(shop_id=MagicMock())
            assert len(result) == 2
            assert result[0]["name"] == "Main Warehouse"
            assert result[1]["id"] == "wh_2"
            mock_gateway.get.assert_called_once_with(
                "/logistics/202309/warehouses"
            )

    @pytest.mark.asyncio
    async def test_get_warehouses_empty(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {"data": {"warehouses": []}}
        with patch.object(
            LogisticsService, "_get_gateway", return_value=mock_gateway
        ):
            service = LogisticsService(mock_session)
            result = await service.get_warehouses(shop_id=MagicMock())
            assert result == []

    @pytest.mark.asyncio
    async def test_get_warehouses_missing_data_key(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {}
        with patch.object(
            LogisticsService, "_get_gateway", return_value=mock_gateway
        ):
            service = LogisticsService(mock_session)
            result = await service.get_warehouses(shop_id=MagicMock())
            assert result == []


class TestGetDeliveryOptions:
    @pytest.mark.asyncio
    async def test_get_delivery_options_returns_list(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "delivery_options": [
                    {"id": "do_1", "name": "Standard"},
                    {"id": "do_2", "name": "Express"},
                ]
            }
        }
        with patch.object(
            LogisticsService, "_get_gateway", return_value=mock_gateway
        ):
            service = LogisticsService(mock_session)
            result = await service.get_delivery_options(
                shop_id=MagicMock(), warehouse_id="wh_1"
            )
            assert len(result) == 2
            assert result[0]["name"] == "Standard"
            mock_gateway.get.assert_called_once_with(
                "/logistics/202309/warehouses/wh_1/delivery_options"
            )

    @pytest.mark.asyncio
    async def test_get_delivery_options_empty(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {"data": {"delivery_options": []}}
        with patch.object(
            LogisticsService, "_get_gateway", return_value=mock_gateway
        ):
            service = LogisticsService(mock_session)
            result = await service.get_delivery_options(
                shop_id=MagicMock(), warehouse_id="wh_1"
            )
            assert result == []

    @pytest.mark.asyncio
    async def test_get_delivery_options_missing_data_key(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {}
        with patch.object(
            LogisticsService, "_get_gateway", return_value=mock_gateway
        ):
            service = LogisticsService(mock_session)
            result = await service.get_delivery_options(
                shop_id=MagicMock(), warehouse_id="wh_1"
            )
            assert result == []


class TestGetShippingProviders:
    @pytest.mark.asyncio
    async def test_get_shipping_providers_returns_list(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "shipping_providers": [
                    {"id": "sp_1", "name": "USPS"},
                    {"id": "sp_2", "name": "FedEx"},
                ]
            }
        }
        with patch.object(
            LogisticsService, "_get_gateway", return_value=mock_gateway
        ):
            service = LogisticsService(mock_session)
            result = await service.get_shipping_providers(shop_id=MagicMock())
            assert len(result) == 2
            assert result[0]["name"] == "USPS"
            assert result[1]["name"] == "FedEx"
            mock_gateway.get.assert_called_once_with(
                "/logistics/202309/shipping_providers"
            )

    @pytest.mark.asyncio
    async def test_get_shipping_providers_empty(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {"data": {"shipping_providers": []}}
        with patch.object(
            LogisticsService, "_get_gateway", return_value=mock_gateway
        ):
            service = LogisticsService(mock_session)
            result = await service.get_shipping_providers(shop_id=MagicMock())
            assert result == []

    @pytest.mark.asyncio
    async def test_get_shipping_providers_missing_data_key(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {}
        with patch.object(
            LogisticsService, "_get_gateway", return_value=mock_gateway
        ):
            service = LogisticsService(mock_session)
            result = await service.get_shipping_providers(shop_id=MagicMock())
            assert result == []


class TestGetShippingTemplates:
    @pytest.mark.asyncio
    async def test_get_shipping_templates_returns_list(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "shipping_templates": [
                    {"id": "t1", "name": "Domestic Standard"},
                    {"id": "t2", "name": "International Express"},
                ]
            }
        }
        with patch.object(
            LogisticsService, "_get_gateway", return_value=mock_gateway
        ):
            service = LogisticsService(mock_session)
            result = await service.get_shipping_templates(shop_id=MagicMock())
            assert len(result) == 2
            assert result[0]["name"] == "Domestic Standard"
            assert result[1]["id"] == "t2"
            mock_gateway.get.assert_called_once_with(
                "/logistics/202510/shipping_templates"
            )

    @pytest.mark.asyncio
    async def test_get_shipping_templates_empty(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {"data": {"shipping_templates": []}}
        with patch.object(
            LogisticsService, "_get_gateway", return_value=mock_gateway
        ):
            service = LogisticsService(mock_session)
            result = await service.get_shipping_templates(shop_id=MagicMock())
            assert result == []

    @pytest.mark.asyncio
    async def test_get_shipping_templates_missing_data_key(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.get.return_value = {}
        with patch.object(
            LogisticsService, "_get_gateway", return_value=mock_gateway
        ):
            service = LogisticsService(mock_session)
            result = await service.get_shipping_templates(shop_id=MagicMock())
            assert result == []


class TestGetGateway:
    @pytest.mark.asyncio
    async def test_get_gateway_shop_not_found(
        self, mock_session: AsyncMock
    ) -> None:
        with patch(
            "backend.modules.commerce.services.logistics_service.ShopService"
        ) as mock_shop_service_cls:
            mock_shop_service = AsyncMock()
            mock_shop_service.get_shop.return_value = None
            mock_shop_service_cls.return_value = mock_shop_service

            service = LogisticsService(mock_session)
            with pytest.raises(ValueError, match="not found"):
                await service._get_gateway(MagicMock())

    @pytest.mark.asyncio
    async def test_get_gateway_returns_gateway(
        self, mock_session: AsyncMock
    ) -> None:
        with patch(
            "backend.modules.commerce.services.logistics_service.ShopService"
        ) as mock_shop_service_cls:
            mock_shop = MagicMock()
            mock_gateway = AsyncMock()
            mock_shop_service = AsyncMock()
            mock_shop_service.get_shop.return_value = mock_shop
            mock_shop_service.build_gateway_for_shop.return_value = (
                mock_gateway
            )
            mock_shop_service_cls.return_value = mock_shop_service

            service = LogisticsService(mock_session)
            result = await service._get_gateway(MagicMock())
            assert result is mock_gateway

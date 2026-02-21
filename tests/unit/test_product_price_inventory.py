import uuid

import pytest
from unittest.mock import AsyncMock, patch

from backend.modules.commerce.services.product_service import ProductService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


class TestUpdatePrice:
    @pytest.mark.asyncio
    async def test_update_price(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(
            ProductService, "_get_gateway", return_value=mock_gateway
        ):
            service = ProductService(mock_session)
            await service.update_price_api(
                shop_id=uuid.uuid4(),
                product_id="prod_1",
                skus=[
                    {
                        "id": "sku_1",
                        "price": {"amount": "2999", "currency": "USD"},
                    }
                ],
            )
            mock_gateway.post.assert_called_once()
            assert "prices" in mock_gateway.post.call_args[0][0]

    @pytest.mark.asyncio
    async def test_update_price_sends_product_id(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(
            ProductService, "_get_gateway", return_value=mock_gateway
        ):
            service = ProductService(mock_session)
            await service.update_price_api(
                shop_id=uuid.uuid4(),
                product_id="prod_42",
                skus=[{"id": "sku_1", "price": {"amount": "1000"}}],
            )
            body = mock_gateway.post.call_args[1].get("json_body", {})
            assert body["product_id"] == "prod_42"
            assert len(body["skus"]) == 1

    @pytest.mark.asyncio
    async def test_update_price_returns_data(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"product_id": "prod_1", "updated_skus": ["sku_1"]}
        }
        with patch.object(
            ProductService, "_get_gateway", return_value=mock_gateway
        ):
            service = ProductService(mock_session)
            result = await service.update_price_api(
                shop_id=uuid.uuid4(),
                product_id="prod_1",
                skus=[{"id": "sku_1", "price": {"amount": "500"}}],
            )
            assert result["product_id"] == "prod_1"


class TestUpdateInventory:
    @pytest.mark.asyncio
    async def test_update_inventory(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(
            ProductService, "_get_gateway", return_value=mock_gateway
        ):
            service = ProductService(mock_session)
            await service.update_inventory_api(
                shop_id=uuid.uuid4(),
                product_id="prod_1",
                skus=[{"id": "sku_1", "inventory": [{"quantity": 50}]}],
            )
            mock_gateway.post.assert_called_once()
            assert "inventory" in mock_gateway.post.call_args[0][0]

    @pytest.mark.asyncio
    async def test_update_inventory_sends_product_id(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(
            ProductService, "_get_gateway", return_value=mock_gateway
        ):
            service = ProductService(mock_session)
            await service.update_inventory_api(
                shop_id=uuid.uuid4(),
                product_id="prod_99",
                skus=[{"id": "sku_1", "inventory": [{"quantity": 100}]}],
            )
            body = mock_gateway.post.call_args[1].get("json_body", {})
            assert body["product_id"] == "prod_99"

    @pytest.mark.asyncio
    async def test_update_inventory_returns_data(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"product_id": "prod_1", "updated_skus": ["sku_1"]}
        }
        with patch.object(
            ProductService, "_get_gateway", return_value=mock_gateway
        ):
            service = ProductService(mock_session)
            result = await service.update_inventory_api(
                shop_id=uuid.uuid4(),
                product_id="prod_1",
                skus=[{"id": "sku_1", "inventory": [{"quantity": 25}]}],
            )
            assert result["product_id"] == "prod_1"

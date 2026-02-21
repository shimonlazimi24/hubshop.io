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


class TestDeleteProducts:
    @pytest.mark.asyncio
    async def test_delete_products(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.delete.return_value = {"data": {}}
        with patch.object(
            ProductService, "_get_gateway", return_value=mock_gateway
        ):
            service = ProductService(mock_session)
            await service.delete_products(
                shop_id=uuid.uuid4(), product_ids=["p1", "p2"]
            )
            mock_gateway.delete.assert_called_once()
            body = mock_gateway.delete.call_args[1].get("json_body", {})
            assert body["product_ids"] == ["p1", "p2"]

    @pytest.mark.asyncio
    async def test_delete_products_calls_correct_endpoint(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.delete.return_value = {"data": {}}
        with patch.object(
            ProductService, "_get_gateway", return_value=mock_gateway
        ):
            service = ProductService(mock_session)
            await service.delete_products(
                shop_id=uuid.uuid4(), product_ids=["p1"]
            )
            endpoint = mock_gateway.delete.call_args[0][0]
            assert endpoint == "/product/202309/products"


class TestActivateProducts:
    @pytest.mark.asyncio
    async def test_activate_products(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(
            ProductService, "_get_gateway", return_value=mock_gateway
        ):
            service = ProductService(mock_session)
            await service.activate_products(
                shop_id=uuid.uuid4(), product_ids=["p1"]
            )
            mock_gateway.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_activate_products_sends_ids(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(
            ProductService, "_get_gateway", return_value=mock_gateway
        ):
            service = ProductService(mock_session)
            await service.activate_products(
                shop_id=uuid.uuid4(), product_ids=["p1", "p2", "p3"]
            )
            body = mock_gateway.post.call_args[1].get("json_body", {})
            assert body["product_ids"] == ["p1", "p2", "p3"]


class TestDeactivateProducts:
    @pytest.mark.asyncio
    async def test_deactivate_products(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(
            ProductService, "_get_gateway", return_value=mock_gateway
        ):
            service = ProductService(mock_session)
            await service.deactivate_products(
                shop_id=uuid.uuid4(), product_ids=["p1"]
            )
            mock_gateway.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_deactivate_products_endpoint(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(
            ProductService, "_get_gateway", return_value=mock_gateway
        ):
            service = ProductService(mock_session)
            await service.deactivate_products(
                shop_id=uuid.uuid4(), product_ids=["p1"]
            )
            endpoint = mock_gateway.post.call_args[0][0]
            assert endpoint == "/product/202309/products/deactivate"


class TestRecoverProducts:
    @pytest.mark.asyncio
    async def test_recover_products(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(
            ProductService, "_get_gateway", return_value=mock_gateway
        ):
            service = ProductService(mock_session)
            await service.recover_products(
                shop_id=uuid.uuid4(), product_ids=["p1"]
            )
            mock_gateway.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_recover_products_endpoint(
        self, mock_session: AsyncMock, mock_gateway: AsyncMock
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}
        with patch.object(
            ProductService, "_get_gateway", return_value=mock_gateway
        ):
            service = ProductService(mock_session)
            await service.recover_products(
                shop_id=uuid.uuid4(), product_ids=["p1"]
            )
            endpoint = mock_gateway.post.call_args[0][0]
            assert endpoint == "/product/202309/products/recover"

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.commerce.services.product_service import ProductService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


class TestEditProduct:
    @pytest.mark.asyncio
    async def test_edit_product_calls_put_with_correct_path(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.put.return_value = {"data": {"product_id": "prod-100"}}
        platform_id = "prod-100"
        shop_id = uuid.uuid4()

        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.edit_product(
                shop_id,
                platform_id,
                title="Updated Title",
                description="Updated description",
                category_id="cat-5",
                images=[{"url": "https://example.com/new.jpg"}],
                skus=[{"id": "sku-1", "price": {"sale_price": "29.99"}}],
            )

            assert result == {"product_id": "prod-100"}
            mock_gateway.put.assert_called_once_with(
                f"/product/202309/products/{platform_id}",
                json_body={
                    "title": "Updated Title",
                    "description": "Updated description",
                    "category_id": "cat-5",
                    "main_images": [{"uri": "https://example.com/new.jpg"}],
                    "skus": [{"id": "sku-1", "price": {"sale_price": "29.99"}}],
                },
            )

    @pytest.mark.asyncio
    async def test_edit_product_empty_images(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.put.return_value = {"data": {}}

        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.edit_product(
                uuid.uuid4(),
                "prod-200",
                title="Title",
                description="Desc",
                category_id="cat-1",
                images=[],
                skus=[],
            )

            assert result == {}
            call_args = mock_gateway.put.call_args
            sent_body = call_args[1]["json_body"]
            assert sent_body["main_images"] == []

    @pytest.mark.asyncio
    async def test_edit_product_returns_empty_on_missing_data(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.put.return_value = {}

        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.edit_product(
                uuid.uuid4(),
                "prod-300",
                title="T",
                description="D",
                category_id="c",
                images=[],
                skus=[],
            )

            assert result == {}


class TestPartialEditProduct:
    @pytest.mark.asyncio
    async def test_partial_edit_sends_only_non_none_fields(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.put.return_value = {"data": {"product_id": "prod-400"}}
        platform_id = "prod-400"

        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            result = await service.partial_edit_product(
                uuid.uuid4(),
                platform_id,
                title="New Title Only",
                description=None,
                images=None,
                skus=None,
            )

            assert result == {"product_id": "prod-400"}
            mock_gateway.put.assert_called_once_with(
                f"/product/202312/products/{platform_id}/partial_edit",
                json_body={"title": "New Title Only"},
            )

    @pytest.mark.asyncio
    async def test_partial_edit_sends_multiple_fields(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.put.return_value = {"data": {}}
        platform_id = "prod-500"
        new_skus = [{"id": "sku-new", "price": {"sale_price": "9.99"}}]

        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            await service.partial_edit_product(
                uuid.uuid4(),
                platform_id,
                title="Partial Title",
                description="Partial Desc",
                skus=new_skus,
            )

            call_args = mock_gateway.put.call_args
            sent_body = call_args[1]["json_body"]
            assert sent_body == {
                "title": "Partial Title",
                "description": "Partial Desc",
                "skus": new_skus,
            }

    @pytest.mark.asyncio
    async def test_partial_edit_all_none_sends_empty_body(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.put.return_value = {"data": {}}

        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            await service.partial_edit_product(
                uuid.uuid4(),
                "prod-600",
                title=None,
                description=None,
            )

            call_args = mock_gateway.put.call_args
            sent_body = call_args[1]["json_body"]
            assert sent_body == {}

    @pytest.mark.asyncio
    async def test_partial_edit_uses_correct_api_version(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        """Partial edit should use 202312 version endpoint."""
        mock_gateway.put.return_value = {"data": {}}
        platform_id = "prod-700"

        with patch.object(ProductService, "_get_gateway", return_value=mock_gateway):
            service = ProductService(mock_session)
            await service.partial_edit_product(
                uuid.uuid4(),
                platform_id,
                title="X",
            )

            call_path = mock_gateway.put.call_args[0][0]
            assert "/202312/" in call_path
            assert call_path.endswith("/partial_edit")

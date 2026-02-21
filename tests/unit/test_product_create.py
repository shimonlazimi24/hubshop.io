import uuid

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.modules.commerce.services.product_service import ProductService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def sample_images() -> list[dict]:
    return [
        {"url": "https://example.com/img1.jpg"},
        {"url": "https://example.com/img2.jpg"},
    ]


@pytest.fixture
def sample_skus() -> list[dict]:
    return [
        {
            "id": "sku-001",
            "seller_sku": "SELLER-001",
            "price": {"sale_price": "19.99", "currency": "USD"},
            "inventory": [{"quantity": 100}],
        }
    ]


class TestCreateProduct:
    @pytest.mark.asyncio
    async def test_create_product_calls_post_and_returns_data(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        sample_images: list[dict],
        sample_skus: list[dict],
    ) -> None:
        product_id = "prod-123"
        mock_gateway.post.return_value = {
            "data": {"product_id": product_id}
        }
        mock_gateway.get.return_value = {
            "data": {
                "id": product_id,
                "title": "Test Product",
                "status": "DRAFT",
                "skus": sample_skus,
            }
        }
        mock_shop = MagicMock()
        mock_shop.workspace_id = uuid.uuid4()

        with (
            patch.object(
                ProductService, "_get_gateway", return_value=mock_gateway
            ),
            patch(
                "backend.modules.commerce.services.product_service.ShopService"
            ) as mock_shop_svc_cls,
            patch.object(
                ProductService, "upsert_product_from_api", new_callable=AsyncMock
            ) as mock_upsert,
        ):
            mock_shop_svc = AsyncMock()
            mock_shop_svc.get_shop.return_value = mock_shop
            mock_shop_svc_cls.return_value = mock_shop_svc

            service = ProductService(mock_session)
            workspace_id = uuid.uuid4()
            shop_id = uuid.uuid4()
            result = await service.create_product(
                workspace_id,
                shop_id,
                title="Test Product",
                description="A test product description",
                category_id="cat-1",
                images=sample_images,
                skus=sample_skus,
            )

            assert result == {"product_id": product_id}
            mock_gateway.post.assert_called_once_with(
                "/product/202309/products",
                json_body={
                    "title": "Test Product",
                    "description": "A test product description",
                    "category_id": "cat-1",
                    "main_images": [
                        {"uri": "https://example.com/img1.jpg"},
                        {"uri": "https://example.com/img2.jpg"},
                    ],
                    "skus": sample_skus,
                },
            )
            mock_gateway.get.assert_called_once_with(
                f"/product/202309/products/{product_id}"
            )
            mock_upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_product_with_package_dimensions(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"product_id": "prod-456"}}
        mock_gateway.get.return_value = {
            "data": {
                "id": "prod-456",
                "title": "Boxed Item",
                "status": "DRAFT",
                "skus": [],
            }
        }
        mock_shop = MagicMock()

        dims = {"length": "10", "width": "5", "height": "3", "unit": "CM"}

        with (
            patch.object(
                ProductService, "_get_gateway", return_value=mock_gateway
            ),
            patch(
                "backend.modules.commerce.services.product_service.ShopService"
            ) as mock_shop_svc_cls,
            patch.object(
                ProductService, "upsert_product_from_api", new_callable=AsyncMock
            ),
        ):
            mock_shop_svc = AsyncMock()
            mock_shop_svc.get_shop.return_value = mock_shop
            mock_shop_svc_cls.return_value = mock_shop_svc

            service = ProductService(mock_session)
            await service.create_product(
                uuid.uuid4(),
                uuid.uuid4(),
                title="Boxed Item",
                description="A boxed item",
                category_id="cat-2",
                images=[],
                skus=[],
                package_dimensions=dims,
            )

            call_args = mock_gateway.post.call_args
            sent_body = call_args[1]["json_body"]
            assert sent_body["package_dimensions"] == dims

    @pytest.mark.asyncio
    async def test_create_product_no_persist_when_no_product_id(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        """If API returns no product_id, skip the detail fetch and persist."""
        mock_gateway.post.return_value = {"data": {}}

        with patch.object(
            ProductService, "_get_gateway", return_value=mock_gateway
        ):
            service = ProductService(mock_session)
            result = await service.create_product(
                uuid.uuid4(),
                uuid.uuid4(),
                title="No ID Product",
                description="desc",
                category_id="cat-1",
                images=[],
                skus=[],
            )

            assert result == {}
            mock_gateway.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_product_images_use_uri_fallback(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
    ) -> None:
        """Images with 'uri' key instead of 'url' should still work."""
        mock_gateway.post.return_value = {"data": {}}

        with patch.object(
            ProductService, "_get_gateway", return_value=mock_gateway
        ):
            service = ProductService(mock_session)
            await service.create_product(
                uuid.uuid4(),
                uuid.uuid4(),
                title="URI Product",
                description="desc",
                category_id="cat-1",
                images=[{"uri": "https://example.com/uri-img.jpg"}],
                skus=[],
            )

            call_args = mock_gateway.post.call_args
            sent_body = call_args[1]["json_body"]
            assert sent_body["main_images"] == [
                {"uri": "https://example.com/uri-img.jpg"}
            ]

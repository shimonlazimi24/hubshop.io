"""Integration test: full sync pipeline with mocked TikTok API."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.commerce.services.order_service import OrderService
from backend.modules.commerce.services.product_service import ProductService


class TestProductSyncPipeline:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        session.delete = MagicMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def sample_shop(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            connected_account_id=uuid.uuid4(),
            shop_id="12345",
            shop_cipher="cipher123",
            shop_name="Test Shop",
            region="US",
        )

    @pytest.mark.asyncio
    @patch("backend.modules.commerce.services.product_service.ShopService")
    async def test_sync_products_from_api(
        self,
        mock_shop_service_cls: AsyncMock,
        mock_session: AsyncMock,
        sample_shop: SimpleNamespace,
    ) -> None:
        """Test full product sync: API call → parse → upsert."""
        mock_gateway = AsyncMock()
        mock_shop_service = AsyncMock()
        mock_shop_service.build_gateway_for_shop.return_value = mock_gateway
        mock_shop_service_cls.return_value = mock_shop_service

        # Mock TikTok API response: 2 products, no next page
        mock_gateway.post.return_value = {
            "data": {
                "products": [
                    {
                        "id": "prod_001",
                        "title": "Widget A",
                        "status": "LIVE",
                        "main_images": [{"url": "https://img.com/a.jpg"}],
                        "skus": [
                            {
                                "id": "sku_001",
                                "seller_sku": "W-A-S",
                                "name": "Small",
                                "price": {"sale_price": "19.99", "currency": "USD"},
                                "inventory": [{"quantity": 10}],
                            }
                        ],
                    },
                    {
                        "id": "prod_002",
                        "title": "Widget B",
                        "status": "PENDING",
                        "skus": [],
                    },
                ],
                "next_page_token": "",
            }
        }

        service = ProductService(mock_session)
        count = await service.sync_products(sample_shop)

        assert count == 2
        # Gateway should have been called once (no next page)
        mock_gateway.post.assert_called_once()

    @pytest.mark.asyncio
    @patch("backend.modules.commerce.services.product_service.ShopService")
    async def test_sync_products_with_pagination(
        self,
        mock_shop_service_cls: AsyncMock,
        mock_session: AsyncMock,
        sample_shop: SimpleNamespace,
    ) -> None:
        """Test product sync handles cursor pagination."""
        mock_gateway = AsyncMock()
        mock_shop_service = AsyncMock()
        mock_shop_service.build_gateway_for_shop.return_value = mock_gateway
        mock_shop_service_cls.return_value = mock_shop_service

        # Two pages of results
        mock_gateway.post.side_effect = [
            {
                "data": {
                    "products": [
                        {"id": "p1", "title": "P1", "status": "LIVE", "skus": []},
                    ],
                    "next_page_token": "page2token",
                }
            },
            {
                "data": {
                    "products": [
                        {"id": "p2", "title": "P2", "status": "LIVE", "skus": []},
                    ],
                    "next_page_token": "",
                }
            },
        ]

        service = ProductService(mock_session)
        count = await service.sync_products(sample_shop)

        assert count == 2
        assert mock_gateway.post.call_count == 2


class TestOrderSyncPipeline:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        session.delete = MagicMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        result.scalars.return_value = scalars_mock
        session.execute.return_value = result
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def sample_shop(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            connected_account_id=uuid.uuid4(),
            shop_id="12345",
            shop_cipher="cipher123",
        )

    @pytest.mark.asyncio
    @patch("backend.modules.commerce.services.order_service.ShopService")
    async def test_sync_orders_from_api(
        self,
        mock_shop_service_cls: AsyncMock,
        mock_session: AsyncMock,
        sample_shop: SimpleNamespace,
    ) -> None:
        """Test order sync: list orders → fetch detail → upsert."""
        mock_gateway = AsyncMock()
        mock_shop_service = AsyncMock()
        mock_shop_service.build_gateway_for_shop.return_value = mock_gateway
        mock_shop_service_cls.return_value = mock_shop_service

        # List returns order IDs
        mock_gateway.post.return_value = {
            "data": {
                "orders": [{"id": "order_001"}],
                "next_page_token": "",
            }
        }

        # Detail fetch
        mock_gateway.get.return_value = {
            "data": {
                "id": "order_001",
                "status": "AWAITING_SHIPMENT",
                "payment": {"total_amount": "49.99", "currency": "USD"},
                "line_items": [
                    {
                        "sku_id": "sku_001",
                        "product_name": "Widget",
                        "quantity": 1,
                        "sale_price": "49.99",
                    }
                ],
                "packages": [],
                "fulfillment_type": "standard",
            }
        }

        service = OrderService(mock_session)
        count = await service.sync_orders(
            sample_shop,
            create_time_from=1700000000,
            create_time_to=1700086400,
        )

        assert count == 1
        mock_gateway.post.assert_called_once()
        mock_gateway.get.assert_called_once()

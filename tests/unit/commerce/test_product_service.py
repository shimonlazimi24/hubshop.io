"""Tests for ProductService - upsert from API, status mapping, SKU handling."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.db.models.commerce import Product, ProductStatus
from backend.modules.commerce.services.product_service import (
    _STATUS_MAP,
    ProductService,
)


class TestStatusMapping:
    def test_all_statuses_mapped(self) -> None:
        expected = {
            "DRAFT",
            "PENDING",
            "LIVE",
            "SELLER_DEACTIVATED",
            "PLATFORM_DEACTIVATED",
            "FROZEN",
            "DELETED",
        }
        assert set(_STATUS_MAP.keys()) == expected

    def test_maps_to_correct_enum(self) -> None:
        assert _STATUS_MAP["LIVE"] == ProductStatus.LIVE
        assert _STATUS_MAP["DELETED"] == ProductStatus.DELETED
        assert _STATUS_MAP["SELLER_DEACTIVATED"] == ProductStatus.SELLER_DEACTIVATED


class TestUpsertProductFromApi:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        # session.add is sync in SQLAlchemy, so use MagicMock
        session.add = MagicMock()
        # Default: no existing product found
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def sample_shop(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            shop_id="12345",
            shop_cipher="cipher123",
            shop_name="Test Shop",
            region="US",
        )

    @pytest.fixture
    def sample_api_payload(self) -> dict:
        return {
            "id": "prod_12345",
            "title": "Amazing Widget",
            "status": "LIVE",
            "main_images": [{"url": "https://example.com/img.jpg"}],
            "skus": [
                {
                    "id": "sku_001",
                    "seller_sku": "SELLER-001",
                    "name": "Size S",
                    "price": {"sale_price": "19.99", "currency": "USD"},
                    "inventory": [{"quantity": 25}],
                },
                {
                    "id": "sku_002",
                    "seller_sku": "SELLER-002",
                    "name": "Size M",
                    "price": {"sale_price": "19.99", "currency": "USD"},
                    "inventory": [{"quantity": 30}],
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_creates_new_product(
        self,
        mock_session: AsyncMock,
        sample_shop: SimpleNamespace,
        sample_api_payload: dict,
    ) -> None:
        service = ProductService(mock_session)
        product = await service.upsert_product_from_api(
            shop=sample_shop, product_data=sample_api_payload
        )

        assert mock_session.add.called
        # Product should have been added
        added_product = mock_session.add.call_args_list[0][0][0]
        assert isinstance(added_product, Product)
        assert added_product.platform_product_id == "prod_12345"
        assert added_product.title == "Amazing Widget"
        assert added_product.status == ProductStatus.LIVE
        assert added_product.inventory_total == 55  # 25 + 30
        assert added_product.sku_count == 2

    @pytest.mark.asyncio
    async def test_updates_existing_product(
        self,
        mock_session: AsyncMock,
        sample_shop: SimpleNamespace,
        sample_api_payload: dict,
    ) -> None:
        existing = SimpleNamespace(
            id=uuid.uuid4(),
            platform_product_id="prod_12345",
            title="Old Title",
            status=ProductStatus.DRAFT,
            main_image_url=None,
            price_amount=None,
            currency=None,
            inventory_total=0,
            sku_count=0,
            detail_json=None,
        )

        # Return existing for product query, None for SKU queries
        call_count = 0

        async def mock_execute(query):
            nonlocal call_count
            call_count += 1
            result = MagicMock()
            if call_count == 1:
                result.scalar_one_or_none.return_value = existing
            else:
                result.scalar_one_or_none.return_value = None
            return result

        mock_session.execute = mock_execute
        mock_session.flush = AsyncMock()

        service = ProductService(mock_session)
        product = await service.upsert_product_from_api(
            shop=sample_shop, product_data=sample_api_payload
        )

        assert existing.title == "Amazing Widget"
        assert existing.status == ProductStatus.LIVE
        assert existing.inventory_total == 55

    @pytest.mark.asyncio
    async def test_handles_missing_image(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        payload = {
            "id": "prod_no_img",
            "title": "No Image Product",
            "status": "DRAFT",
            "skus": [],
        }
        service = ProductService(mock_session)
        product = await service.upsert_product_from_api(
            shop=sample_shop, product_data=payload
        )
        added = mock_session.add.call_args_list[0][0][0]
        assert added.main_image_url is None

    @pytest.mark.asyncio
    async def test_handles_unknown_status(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        payload = {
            "id": "prod_unknown",
            "title": "Unknown Status",
            "status": "SOME_NEW_STATUS",
            "skus": [],
        }
        service = ProductService(mock_session)
        await service.upsert_product_from_api(shop=sample_shop, product_data=payload)
        added = mock_session.add.call_args_list[0][0][0]
        assert added.status == ProductStatus.DRAFT  # Falls back to DRAFT


class TestUpdateProductStatus:
    @pytest.mark.asyncio
    async def test_updates_status(self) -> None:
        existing = SimpleNamespace(
            id=uuid.uuid4(),
            platform_product_id="prod_123",
            status=ProductStatus.LIVE,
        )

        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = existing
        session.execute.return_value = result

        service = ProductService(session)
        updated = await service.update_product_status("prod_123", "FROZEN")
        assert updated is not None
        assert updated.status == ProductStatus.FROZEN

    @pytest.mark.asyncio
    async def test_returns_none_for_missing(self) -> None:
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result

        service = ProductService(session)
        updated = await service.update_product_status("nonexistent", "LIVE")
        assert updated is None


class TestUpdateInventory:
    @pytest.mark.asyncio
    async def test_updates_inventory(self) -> None:
        existing = SimpleNamespace(
            id=uuid.uuid4(),
            platform_product_id="prod_123",
            inventory_total=50,
        )

        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = existing
        session.execute.return_value = result

        service = ProductService(session)
        updated = await service.update_inventory("prod_123", 75)
        assert updated is not None
        assert updated.inventory_total == 75

"""Tests for commerce schemas with source_platform field."""

from datetime import datetime, timezone

from backend.modules.commerce.schemas import (
    OrderDetailResponse,
    OrderSummaryResponse,
    ProductSummaryResponse,
)


class TestOrderSummarySourcePlatform:
    def test_source_platform_defaults_to_shop(self) -> None:
        data = {
            "id": "abc",
            "platform_order_id": "ord_1",
            "status": "completed",
            "total_amount": "99.00",
            "currency": "USD",
            "item_count": 2,
            "created_at": datetime.now(tz=timezone.utc),
            "updated_at": datetime.now(tz=timezone.utc),
        }
        response = OrderSummaryResponse(**data)
        assert response.source_platform == "shop"

    def test_source_platform_can_be_set_to_affiliate(self) -> None:
        data = {
            "id": "abc",
            "platform_order_id": "ord_1",
            "status": "completed",
            "total_amount": "99.00",
            "currency": "USD",
            "item_count": 2,
            "source_platform": "affiliate",
            "created_at": datetime.now(tz=timezone.utc),
            "updated_at": datetime.now(tz=timezone.utc),
        }
        response = OrderSummaryResponse(**data)
        assert response.source_platform == "affiliate"


class TestOrderDetailSourcePlatform:
    def test_source_platform_defaults_to_shop(self) -> None:
        data = {
            "id": "abc",
            "platform_order_id": "ord_1",
            "status": "completed",
            "total_amount": "99.00",
            "currency": "USD",
            "item_count": 2,
            "created_at": datetime.now(tz=timezone.utc),
            "updated_at": datetime.now(tz=timezone.utc),
        }
        response = OrderDetailResponse(**data)
        assert response.source_platform == "shop"

    def test_source_platform_can_be_set_to_affiliate(self) -> None:
        data = {
            "id": "abc",
            "platform_order_id": "ord_1",
            "status": "completed",
            "total_amount": "99.00",
            "currency": "USD",
            "item_count": 2,
            "source_platform": "affiliate",
            "created_at": datetime.now(tz=timezone.utc),
            "updated_at": datetime.now(tz=timezone.utc),
        }
        response = OrderDetailResponse(**data)
        assert response.source_platform == "affiliate"


class TestProductSummarySourcePlatform:
    def test_source_platform_defaults_to_shop(self) -> None:
        data = {
            "id": "abc",
            "platform_product_id": "prod_1",
            "title": "Test Product",
            "status": "ACTIVE",
            "inventory_total": 100,
            "sku_count": 2,
            "created_at": datetime.now(tz=timezone.utc),
            "updated_at": datetime.now(tz=timezone.utc),
        }
        response = ProductSummaryResponse(**data)
        assert response.source_platform == "shop"

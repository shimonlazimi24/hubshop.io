"""Tests for commerce Pydantic schemas."""

import pytest

from backend.modules.commerce.schemas import (
    OrderDetailResponse,
    OrderLineItemResponse,
    OrderStatusDistributionResponse,
    OrderSummaryResponse,
    OrderTimelineEventResponse,
    PackageResponse,
    PaginatedResponse,
    ProductDetailResponse,
    ProductSkuResponse,
    ProductSummaryResponse,
    ReturnResponse,
    RevenueSummaryResponse,
    RevenueTimeseriesPoint,
    ShopResponse,
    TopProductResponse,
)


class TestShopResponse:
    def test_serialization(self) -> None:
        data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "shop_id": "12345",
            "shop_name": "Test Shop",
            "region": "US",
            "last_product_sync_at": None,
            "last_order_sync_at": None,
            "created_at": "2026-01-01T00:00:00Z",
        }
        shop = ShopResponse(**data)
        assert shop.shop_name == "Test Shop"
        assert shop.region == "US"
        assert shop.last_product_sync_at is None


class TestProductSummaryResponse:
    def test_serialization(self) -> None:
        data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "platform_product_id": "prod_123",
            "title": "Test Product",
            "status": "live",
            "main_image_url": "https://example.com/img.jpg",
            "price_amount": "29.99",
            "currency": "USD",
            "inventory_total": 100,
            "sku_count": 3,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-02T00:00:00Z",
        }
        product = ProductSummaryResponse(**data)
        assert product.title == "Test Product"
        assert product.inventory_total == 100

    def test_nullable_fields(self) -> None:
        data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "platform_product_id": "prod_123",
            "title": "Test",
            "status": "draft",
            "main_image_url": None,
            "price_amount": None,
            "currency": None,
            "inventory_total": 0,
            "sku_count": 0,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
        product = ProductSummaryResponse(**data)
        assert product.main_image_url is None
        assert product.price_amount is None


class TestProductDetailResponse:
    def test_with_skus(self) -> None:
        data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "platform_product_id": "prod_123",
            "title": "Test Product",
            "status": "live",
            "main_image_url": None,
            "price_amount": "19.99",
            "currency": "USD",
            "inventory_total": 50,
            "sku_count": 2,
            "skus": [
                {
                    "id": "sku-1",
                    "platform_sku_id": "sku_001",
                    "seller_sku": "SELLER-001",
                    "price_amount": "19.99",
                    "inventory_quantity": 25,
                    "sku_name": "Size S",
                },
                {
                    "id": "sku-2",
                    "platform_sku_id": "sku_002",
                    "seller_sku": None,
                    "price_amount": "19.99",
                    "inventory_quantity": 25,
                    "sku_name": "Size M",
                },
            ],
            "detail_json": {"raw": "data"},
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-02T00:00:00Z",
        }
        product = ProductDetailResponse(**data)
        assert len(product.skus) == 2
        assert product.skus[0].seller_sku == "SELLER-001"
        assert product.skus[1].seller_sku is None
        assert product.detail_json == {"raw": "data"}


class TestOrderSummaryResponse:
    def test_serialization(self) -> None:
        data = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "platform_order_id": "order_123",
            "status": "awaiting_shipment",
            "total_amount": "99.99",
            "currency": "USD",
            "item_count": 2,
            "fulfillment_type": "standard",
            "rts_sla": "2026-01-05T00:00:00Z",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
        order = OrderSummaryResponse(**data)
        assert order.total_amount == "99.99"
        assert order.item_count == 2


class TestOrderDetailResponse:
    def test_with_line_items_and_packages(self) -> None:
        data = {
            "id": "order-uuid",
            "platform_order_id": "order_123",
            "status": "in_transit",
            "total_amount": "149.99",
            "currency": "USD",
            "item_count": 1,
            "fulfillment_type": None,
            "rts_sla": None,
            "line_items": [
                {
                    "id": "li-1",
                    "platform_sku_id": "sku_001",
                    "product_name": "Cool Widget",
                    "quantity": 2,
                    "unit_price": "49.99",
                    "total_price": "99.98",
                }
            ],
            "packages": [
                {
                    "id": "pkg-1",
                    "platform_package_id": "PKG001",
                    "status": "shipped",
                    "tracking_number": "TRACK123",
                    "shipping_provider": "USPS",
                    "created_at": "2026-01-02T00:00:00Z",
                    "updated_at": "2026-01-02T00:00:00Z",
                }
            ],
            "detail_json": None,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-02T00:00:00Z",
        }
        order = OrderDetailResponse(**data)
        assert len(order.line_items) == 1
        assert order.line_items[0].product_name == "Cool Widget"
        assert len(order.packages) == 1
        assert order.packages[0].tracking_number == "TRACK123"


class TestTimelineEventResponse:
    def test_serialization(self) -> None:
        data = {
            "id": "evt-1",
            "from_status": "awaiting_shipment",
            "to_status": "in_transit",
            "source": "webhook",
            "occurred_at": "2026-01-02T10:30:00Z",
        }
        event = OrderTimelineEventResponse(**data)
        assert event.from_status == "awaiting_shipment"
        assert event.source == "webhook"

    def test_null_from_status(self) -> None:
        data = {
            "id": "evt-1",
            "from_status": None,
            "to_status": "unpaid",
            "source": "sync",
            "occurred_at": "2026-01-01T00:00:00Z",
        }
        event = OrderTimelineEventResponse(**data)
        assert event.from_status is None


class TestReturnResponse:
    def test_serialization(self) -> None:
        data = {
            "id": "ret-1",
            "platform_return_id": "RET001",
            "order_id": "order-uuid",
            "return_type": "return_and_refund",
            "status": "pending",
            "reason": "Defective product",
            "refund_amount": "29.99",
            "created_at": "2026-01-03T00:00:00Z",
            "updated_at": "2026-01-03T00:00:00Z",
        }
        ret = ReturnResponse(**data)
        assert ret.return_type == "return_and_refund"
        assert ret.reason == "Defective product"


class TestAnalyticsResponses:
    def test_revenue_summary(self) -> None:
        data = {
            "total_revenue": "15000.00",
            "total_orders": 150,
            "average_order_value": "100.00",
            "return_rate": 0.05,
            "period_start": "2026-01-01T00:00:00Z",
            "period_end": "2026-01-31T00:00:00Z",
        }
        summary = RevenueSummaryResponse(**data)
        assert summary.total_orders == 150
        assert summary.return_rate == 0.05

    def test_timeseries_point(self) -> None:
        point = RevenueTimeseriesPoint(
            date="2026-01-15", revenue="500.00", order_count=5
        )
        assert point.order_count == 5

    def test_top_product(self) -> None:
        product = TopProductResponse(
            product_id="p-1",
            title="Best Seller",
            total_revenue="5000.00",
            total_quantity=200,
            main_image_url=None,
        )
        assert product.total_quantity == 200

    def test_order_distribution(self) -> None:
        dist = OrderStatusDistributionResponse(
            status="completed", count=50, percentage=33.3
        )
        assert dist.percentage == 33.3


class TestPaginatedResponse:
    def test_generic_pagination(self) -> None:
        resp = PaginatedResponse[ProductSummaryResponse](
            items=[],
            total=0,
            page=1,
            page_size=20,
            total_pages=0,
        )
        assert resp.total == 0
        assert resp.total_pages == 0

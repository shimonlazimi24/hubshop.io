"""Tests for enhanced promotion and coupon schemas."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend.modules.commerce.schemas import (
    CouponResponse,
    CreateFlashDealRequest,
    CreateProductDiscountRequest,
    UpdatePromotionProductsRequest,
)


class TestCreateFlashDealRequest:
    def test_valid_flash_deal(self) -> None:
        req = CreateFlashDealRequest(
            shop_id="shop_001",
            title="Summer Flash",
            product_ids=["prod_1"],
            countdown_duration_hours=48,
            max_quantity=100,
            price_rules=[
                {
                    "sku_id": "sku_1",
                    "original_price": "29.99",
                    "discount_price": "19.99",
                }
            ],
        )
        assert req.countdown_duration_hours == 48

    def test_countdown_max_72_hours(self) -> None:
        with pytest.raises(ValidationError):
            CreateFlashDealRequest(
                shop_id="shop_001",
                title="Too Long",
                product_ids=["prod_1"],
                countdown_duration_hours=73,
                price_rules=[
                    {
                        "sku_id": "sku_1",
                        "original_price": "10",
                        "discount_price": "5",
                    }
                ],
            )

    def test_countdown_min_1_hour(self) -> None:
        with pytest.raises(ValidationError):
            CreateFlashDealRequest(
                shop_id="shop_001",
                title="Too Short",
                product_ids=["prod_1"],
                countdown_duration_hours=0,
                price_rules=[
                    {
                        "sku_id": "sku_1",
                        "original_price": "10",
                        "discount_price": "5",
                    }
                ],
            )


class TestCreateProductDiscountRequest:
    def test_valid_percentage_discount(self) -> None:
        req = CreateProductDiscountRequest(
            shop_id="shop_001",
            title="20% Off",
            product_ids=["prod_1"],
            discount_type="PERCENTAGE",
            discount_value="20",
        )
        assert req.discount_type == "PERCENTAGE"

    def test_valid_fixed_discount(self) -> None:
        req = CreateProductDiscountRequest(
            shop_id="shop_001",
            title="$5 Off",
            product_ids=["prod_1"],
            discount_type="FIXED_AMOUNT",
            discount_value="5.00",
            start_time="2026-04-01T00:00:00Z",
            end_time="2026-04-07T00:00:00Z",
        )
        assert req.discount_type == "FIXED_AMOUNT"


class TestCouponResponse:
    def test_coupon_response_from_attributes(self) -> None:
        now = datetime.now(UTC)

        class FakeCoupon:
            id = "uuid-1"
            platform_coupon_id = "coupon_001"
            code = "SAVE20"
            discount_type = "PERCENTAGE"
            discount_value = "20.0"
            min_order_amount = "10.00"
            validity_start = now
            validity_end = now
            total_claim_limit = 1000
            per_user_limit = 1
            claimed_count = 50
            used_count = 30
            status = "ACTIVE"
            created_at = now
            updated_at = now

        resp = CouponResponse.model_validate(FakeCoupon(), from_attributes=True)
        assert resp.code == "SAVE20"


class TestUpdatePromotionProductsRequest:
    def test_add_products(self) -> None:
        req = UpdatePromotionProductsRequest(
            product_ids=["prod_1", "prod_2"],
            action="ADD",
        )
        assert req.action == "ADD"

    def test_remove_products(self) -> None:
        req = UpdatePromotionProductsRequest(
            product_ids=["prod_1"],
            action="REMOVE",
        )
        assert req.action == "REMOVE"

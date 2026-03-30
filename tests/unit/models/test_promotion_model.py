"""Tests for extended Promotion model fields."""

import uuid

from backend.db.models.commerce import Promotion


class TestPromotionModel:
    def test_promotion_has_flash_deal_fields(self) -> None:
        promo = Promotion(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_activity_id="act_001",
            promotion_type="FLASH_DEAL",
            title="Summer Flash Sale",
            status="ACTIVE",
            max_quantity=100,
            countdown_duration_hours=48,
            price_rules=[
                {
                    "sku_id": "sku_1",
                    "original_price": "29.99",
                    "discount_price": "19.99",
                }
            ],
        )
        assert promo.max_quantity == 100
        assert promo.countdown_duration_hours == 48
        assert promo.price_rules[0]["discount_price"] == "19.99"

    def test_promotion_flash_deal_fields_nullable(self) -> None:
        promo = Promotion(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_activity_id="act_002",
            promotion_type="DISCOUNT",
            title="Regular Discount",
            status="ACTIVE",
        )
        assert promo.max_quantity is None
        assert promo.countdown_duration_hours is None
        assert promo.price_rules is None

    def test_promotion_has_product_count(self) -> None:
        promo = Promotion(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_activity_id="act_003",
            promotion_type="DISCOUNT",
            title="Test",
            status="ACTIVE",
            product_count=5,
        )
        assert promo.product_count == 5

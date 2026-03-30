"""Integration tests for promotions module -- schema validation end-to-end."""

import pytest
from pydantic import ValidationError

from backend.modules.commerce.schemas import (
    CreateFlashDealRequest,
    CreateProductDiscountRequest,
    CreatePromotionRequest,
)


@pytest.mark.integration
class TestPromotionSchemaIntegration:
    def test_flash_deal_full_roundtrip(self) -> None:
        req = CreateFlashDealRequest(
            shop_id="shop_001",
            title="Flash Sale: Summer Collection",
            product_ids=["prod_1", "prod_2"],
            countdown_duration_hours=24,
            max_quantity=500,
            price_rules=[
                {
                    "sku_id": "sku_1",
                    "original_price": "49.99",
                    "discount_price": "29.99",
                },
                {
                    "sku_id": "sku_2",
                    "original_price": "39.99",
                    "discount_price": "24.99",
                },
            ],
            start_time="2026-04-01T00:00:00Z",
            end_time="2026-04-02T00:00:00Z",
        )
        data = req.model_dump()
        assert data["countdown_duration_hours"] == 24
        assert len(data["price_rules"]) == 2

    def test_invalid_flash_deal_rejected(self) -> None:
        with pytest.raises(ValidationError):
            CreateFlashDealRequest(
                shop_id="shop_001",
                title="Bad",
                product_ids=["prod_1"],
                countdown_duration_hours=100,
                price_rules=[],
            )

    def test_product_discount_roundtrip(self) -> None:
        req = CreateProductDiscountRequest(
            shop_id="shop_001",
            title="20% Off Everything",
            product_ids=["prod_1", "prod_2", "prod_3"],
            discount_type="PERCENTAGE",
            discount_value="20",
        )
        data = req.model_dump()
        assert data["discount_type"] == "PERCENTAGE"

    def test_legacy_create_promotion_still_works(self) -> None:
        req = CreatePromotionRequest(
            shop_id="shop_001",
            title="Generic Promo",
            promotion_type="DISCOUNT",
        )
        assert req.shop_id == "shop_001"

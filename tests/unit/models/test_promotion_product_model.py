"""Tests for PromotionProduct junction model."""

import uuid

from backend.db.models.promotion_product import PromotionProduct


class TestPromotionProductModel:
    def test_creation_with_all_fields(self) -> None:
        pp = PromotionProduct(
            promotion_id=uuid.uuid4(),
            product_id=uuid.uuid4(),
            sku_id=uuid.uuid4(),
            original_price="29.99",
            discount_price="19.99",
            quantity_limit=50,
        )
        assert pp.original_price == "29.99"
        assert pp.discount_price == "19.99"
        assert pp.quantity_limit == 50

    def test_sku_and_quantity_nullable(self) -> None:
        pp = PromotionProduct(
            promotion_id=uuid.uuid4(),
            product_id=uuid.uuid4(),
            original_price="10.00",
            discount_price="7.50",
        )
        assert pp.sku_id is None
        assert pp.quantity_limit is None

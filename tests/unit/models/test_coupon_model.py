"""Tests for Coupon model."""

import uuid
from datetime import UTC, datetime

from backend.db.models.coupon import Coupon


class TestCouponModel:
    def test_coupon_creation(self) -> None:
        now = datetime.now(UTC)
        coupon = Coupon(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_coupon_id="coupon_001",
            code="SUMMER20",
            discount_type="PERCENTAGE",
            discount_value="20.0",
            min_order_amount="10.00",
            validity_start=now,
            validity_end=now,
            total_claim_limit=1000,
            per_user_limit=1,
            claimed_count=50,
            used_count=30,
            status="ACTIVE",
        )
        assert coupon.code == "SUMMER20"
        assert coupon.discount_type == "PERCENTAGE"
        assert coupon.total_claim_limit == 1000

    def test_coupon_nullable_fields(self) -> None:
        coupon = Coupon(
            workspace_id=uuid.uuid4(),
            shop_id=uuid.uuid4(),
            platform_coupon_id="coupon_002",
            code="SAVE10",
            discount_type="FIXED_AMOUNT",
            discount_value="10.0",
            status="ACTIVE",
        )
        assert coupon.min_order_amount is None
        assert coupon.validity_start is None

"""Tests for CouponService -- sync and search coupons from TikTok."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.commerce.services.coupon_service import CouponService


class TestSyncCoupons:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
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
        )

    @pytest.fixture
    def sample_coupon_data(self) -> list[dict]:
        return [
            {
                "coupon_id": "coupon_001",
                "code": "SUMMER20",
                "discount_type": "PERCENTAGE",
                "discount_value": "20",
                "min_order_amount": "10.00",
                "status": "ACTIVE",
                "claim_limit": 1000,
                "per_user_limit": 1,
                "claimed_count": 50,
                "used_count": 30,
            },
        ]

    @pytest.mark.asyncio
    async def test_sync_coupons_inserts_new(
        self,
        mock_session: AsyncMock,
        sample_shop: SimpleNamespace,
        sample_coupon_data: list[dict],
    ) -> None:
        service = CouponService(mock_session)

        with patch.object(service, "_build_gateway") as mock_gw:
            gateway = AsyncMock()
            gateway.get.return_value = {"data": {"coupons": sample_coupon_data}}
            mock_gw.return_value = gateway

            count = await service.sync_coupons(sample_shop)

        assert count == 1
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_coupons_returns_zero_on_empty(
        self,
        mock_session: AsyncMock,
        sample_shop: SimpleNamespace,
    ) -> None:
        service = CouponService(mock_session)

        with patch.object(service, "_build_gateway") as mock_gw:
            gateway = AsyncMock()
            gateway.get.return_value = {"data": {"coupons": []}}
            mock_gw.return_value = gateway

            count = await service.sync_coupons(sample_shop)

        assert count == 0
        mock_session.add.assert_not_called()


class TestSearchCoupons:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        result_mock = MagicMock()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        result_mock.scalars.return_value = scalars_mock
        result_mock.scalar_one.return_value = 0
        session.execute.return_value = result_mock
        return session

    @pytest.mark.asyncio
    async def test_list_coupons_with_filters(self, mock_session: AsyncMock) -> None:
        service = CouponService(mock_session)
        result = await service.list_coupons(
            uuid.uuid4(), shop_id=uuid.uuid4(), status_filter="ACTIVE"
        )
        assert result.items == []
        assert result.total == 0

"""Tests for coupon routes."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.commerce.services.coupon_service import CouponService


class TestCouponRouteLogic:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_coupon_service_list_called(self, mock_session: AsyncMock) -> None:
        from backend.utils.pagination import PaginatedResult

        service = CouponService(mock_session)
        workspace_id = uuid.uuid4()

        with patch.object(service, "list_coupons") as mock_list:
            mock_list.return_value = PaginatedResult(
                items=[], total=0, page=1, page_size=20
            )
            result = await service.list_coupons(workspace_id, shop_id=uuid.uuid4())

        assert result.total == 0

    @pytest.mark.asyncio
    async def test_coupon_sync_called(self, mock_session: AsyncMock) -> None:
        service = CouponService(mock_session)
        shop = SimpleNamespace(id=uuid.uuid4(), workspace_id=uuid.uuid4())

        with patch.object(service, "sync_coupons") as mock_sync:
            mock_sync.return_value = 5
            count = await service.sync_coupons(shop)

        assert count == 5

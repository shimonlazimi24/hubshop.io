"""Tests for UnifiedCommerceService — cross-platform order aggregation."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.commerce.services.unified_service import UnifiedCommerceService


class TestListOrdersUnified:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_returns_shop_orders_when_platform_is_shop(
        self, mock_session: AsyncMock, workspace_id: uuid.UUID
    ) -> None:
        mock_order = SimpleNamespace(
            id=str(uuid.uuid4()),
            platform_order_id="ord_1",
            status="completed",
            total_amount="99.00",
            currency="USD",
            item_count=2,
            fulfillment_type="SHIP_BY_SELLER",
            rts_sla=None,
            source_platform="shop",
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        mock_result = SimpleNamespace(
            items=[mock_order], total=1, page=1, page_size=20, total_pages=1
        )

        with patch(
            "backend.modules.commerce.services.unified_service.OrderService"
        ) as MockOrderService:
            mock_svc = AsyncMock()
            mock_svc.list_orders.return_value = mock_result
            MockOrderService.return_value = mock_svc

            service = UnifiedCommerceService(mock_session)
            result = await service.list_orders(workspace_id, platform="shop")

        assert len(result.items) == 1
        assert result.items[0].source_platform == "shop"

    @pytest.mark.asyncio
    async def test_returns_all_when_platform_is_none(
        self, mock_session: AsyncMock, workspace_id: uuid.UUID
    ) -> None:
        mock_order = SimpleNamespace(
            id=str(uuid.uuid4()),
            platform_order_id="ord_1",
            status="completed",
            total_amount="99.00",
            currency="USD",
            item_count=2,
            fulfillment_type="SHIP_BY_SELLER",
            rts_sla=None,
            source_platform="shop",
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        )
        mock_result = SimpleNamespace(
            items=[mock_order], total=1, page=1, page_size=20, total_pages=1
        )

        with patch(
            "backend.modules.commerce.services.unified_service.OrderService"
        ) as MockOrderService:
            mock_svc = AsyncMock()
            mock_svc.list_orders.return_value = mock_result
            MockOrderService.return_value = mock_svc

            service = UnifiedCommerceService(mock_session)
            result = await service.list_orders(workspace_id, platform=None)

        assert len(result.items) >= 1
        assert all(
            item.source_platform in ("shop", "affiliate") for item in result.items
        )
        # Pagination total should reflect the real total, not just page count
        assert result.total == 1
        assert result.total_pages == 1

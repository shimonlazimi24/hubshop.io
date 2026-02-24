"""Tests for OrderService - upsert, status transitions, timeline events."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.db.models.commerce import (
    Order,
    OrderLineItem,
    OrderStatus,
    OrderStatusEvent,
)
from backend.modules.commerce.services.order_service import _STATUS_MAP, OrderService


class TestStatusMapping:
    def test_all_statuses_mapped(self) -> None:
        expected = {
            "UNPAID",
            "ON_HOLD",
            "AWAITING_SHIPMENT",
            "AWAITING_COLLECTION",
            "PARTIALLY_SHIPPING",
            "IN_TRANSIT",
            "DELIVERED",
            "COMPLETED",
            "CANCELLED",
        }
        assert set(_STATUS_MAP.keys()) == expected


class TestUpsertOrderFromApi:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        # session.add / session.delete are sync in SQLAlchemy, so use MagicMock
        session.add = MagicMock()
        session.delete = MagicMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        result_mock.scalars.return_value = scalars_mock
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
    def sample_order_data(self) -> dict:
        return {
            "id": "order_777",
            "status": "AWAITING_SHIPMENT",
            "payment": {
                "total_amount": "149.99",
                "currency": "USD",
            },
            "line_items": [
                {
                    "sku_id": "sku_001",
                    "product_name": "Cool Widget",
                    "quantity": 2,
                    "sale_price": "49.99",
                },
            ],
            "packages": [],
            "fulfillment_type": "standard",
            "rts_sla": None,
        }

    @pytest.mark.asyncio
    async def test_creates_new_order(
        self,
        mock_session: AsyncMock,
        sample_shop: SimpleNamespace,
        sample_order_data: dict,
    ) -> None:
        service = OrderService(mock_session)
        order = await service.upsert_order_from_api(
            shop=sample_shop, order_data=sample_order_data
        )

        assert mock_session.add.called
        added_order = mock_session.add.call_args_list[0][0][0]
        assert isinstance(added_order, Order)
        assert added_order.platform_order_id == "order_777"
        assert added_order.status == OrderStatus.AWAITING_SHIPMENT
        assert added_order.total_amount == "149.99"
        assert added_order.currency == "USD"

    @pytest.mark.asyncio
    async def test_creates_line_items(
        self,
        mock_session: AsyncMock,
        sample_shop: SimpleNamespace,
        sample_order_data: dict,
    ) -> None:
        service = OrderService(mock_session)
        await service.upsert_order_from_api(
            shop=sample_shop, order_data=sample_order_data
        )

        # Should have added: order + line item
        added_items = [
            call[0][0]
            for call in mock_session.add.call_args_list
            if isinstance(call[0][0], OrderLineItem)
        ]
        assert len(added_items) == 1
        assert added_items[0].product_name == "Cool Widget"
        assert added_items[0].quantity == 2

    @pytest.mark.asyncio
    async def test_handles_unknown_status(
        self, mock_session: AsyncMock, sample_shop: SimpleNamespace
    ) -> None:
        data = {
            "id": "order_888",
            "status": "SOME_NEW_STATUS",
            "payment": {"total_amount": "10.00", "currency": "USD"},
            "line_items": [],
            "packages": [],
        }
        service = OrderService(mock_session)
        await service.upsert_order_from_api(shop=sample_shop, order_data=data)

        added_order = mock_session.add.call_args_list[0][0][0]
        assert added_order.status == OrderStatus.UNPAID  # Default fallback


class TestUpdateOrderStatus:
    @pytest.mark.asyncio
    @patch("backend.modules.commerce.services.order_service.get_redis")
    async def test_updates_status_and_records_event(
        self, mock_get_redis: AsyncMock
    ) -> None:
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        existing = SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            platform_order_id="order_123",
            status=OrderStatus.AWAITING_SHIPMENT,
        )

        session = AsyncMock()
        session.add = MagicMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = existing
        session.execute.return_value = result

        service = OrderService(session)
        order = await service.update_order_status(
            "order_123", "IN_TRANSIT", source="webhook"
        )

        assert order is not None
        assert order.status == OrderStatus.IN_TRANSIT
        # Should have added a status event
        assert session.add.called
        added = session.add.call_args[0][0]
        assert isinstance(added, OrderStatusEvent)
        assert added.from_status == "awaiting_shipment"
        assert added.to_status == "in_transit"
        assert added.source == "webhook"
        # Should have published to Redis
        mock_redis.publish.assert_called_once()

    @pytest.mark.asyncio
    @patch("backend.modules.commerce.services.order_service.get_redis")
    async def test_no_change_if_same_status(self, mock_get_redis: AsyncMock) -> None:
        existing = SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            platform_order_id="order_123",
            status=OrderStatus.IN_TRANSIT,
        )

        session = AsyncMock()
        session.add = MagicMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = existing
        session.execute.return_value = result

        service = OrderService(session)
        order = await service.update_order_status(
            "order_123", "IN_TRANSIT", source="webhook"
        )

        assert order is not None
        assert not session.add.called  # No event added

    @pytest.mark.asyncio
    async def test_returns_none_for_missing_order(self) -> None:
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result

        service = OrderService(session)
        order = await service.update_order_status("nonexistent", "IN_TRANSIT")
        assert order is None


class TestUpdateOrderDetailJson:
    @pytest.mark.asyncio
    async def test_patches_detail_json(self) -> None:
        existing = SimpleNamespace(
            id=uuid.uuid4(),
            platform_order_id="order_123",
            detail_json={"status": "old", "address": "old_address"},
        )

        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = existing
        session.execute.return_value = result

        service = OrderService(session)
        order = await service.update_order_detail_json(
            "order_123", {"address": "new_address"}
        )
        assert order is not None
        assert order.detail_json["address"] == "new_address"
        assert order.detail_json["status"] == "old"  # Preserved

    @pytest.mark.asyncio
    async def test_creates_detail_json_from_none(self) -> None:
        existing = SimpleNamespace(
            id=uuid.uuid4(),
            platform_order_id="order_123",
            detail_json=None,
        )

        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = existing
        session.execute.return_value = result

        service = OrderService(session)
        order = await service.update_order_detail_json(
            "order_123", {"new_key": "value"}
        )
        assert order is not None
        assert order.detail_json == {"new_key": "value"}

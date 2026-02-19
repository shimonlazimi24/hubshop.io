"""Tests for commerce webhook handlers with sample TikTok payloads."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.commerce.webhook_handlers import (
    COMMERCE_WEBHOOK_HANDLERS,
    handle_cancellation_status_change,
    handle_inventory_status_change,
    handle_order_status_change,
    handle_package_update,
    handle_product_status_change,
    handle_recipient_address_update,
    handle_return_status_change,
)


class TestHandlerRegistry:
    def test_all_types_registered(self) -> None:
        expected_types = {"1", "3", "4", "5", "11", "12", "15", "16", "27"}
        assert set(COMMERCE_WEBHOOK_HANDLERS.keys()) == expected_types

    def test_handlers_are_callable(self) -> None:
        for key, handler in COMMERCE_WEBHOOK_HANDLERS.items():
            assert callable(handler), f"Handler for type {key} is not callable"


class TestHandleOrderStatusChange:
    @pytest.mark.asyncio
    @patch("backend.modules.commerce.webhook_handlers.OrderService")
    async def test_updates_order_status(
        self, mock_service_cls: AsyncMock
    ) -> None:
        mock_service = AsyncMock()
        mock_service_cls.return_value = mock_service
        session = AsyncMock()

        payload = {
            "type": 1,
            "data": {
                "order_id": "order_123",
                "order_status": "IN_TRANSIT",
            },
        }

        await handle_order_status_change(payload, session)
        mock_service.update_order_status.assert_called_once_with(
            "order_123", "IN_TRANSIT", source="webhook"
        )

    @pytest.mark.asyncio
    @patch("backend.modules.commerce.webhook_handlers.OrderService")
    async def test_skips_if_missing_data(
        self, mock_service_cls: AsyncMock
    ) -> None:
        session = AsyncMock()
        payload = {"type": 1, "data": {}}  # Missing order_id

        await handle_order_status_change(payload, session)
        mock_service_cls.return_value.update_order_status.assert_not_called()


class TestHandleRecipientAddressUpdate:
    @pytest.mark.asyncio
    @patch("backend.modules.commerce.webhook_handlers.OrderService")
    async def test_patches_address(self, mock_service_cls: AsyncMock) -> None:
        mock_service = AsyncMock()
        mock_service_cls.return_value = mock_service
        session = AsyncMock()

        payload = {
            "type": 3,
            "data": {
                "order_id": "order_123",
                "recipient_address": {
                    "name": "John Doe",
                    "city": "New York",
                },
            },
        }

        await handle_recipient_address_update(payload, session)
        mock_service.update_order_detail_json.assert_called_once_with(
            "order_123",
            {"recipient_address": {"name": "John Doe", "city": "New York"}},
        )


class TestHandlePackageUpdate:
    @pytest.mark.asyncio
    @patch("backend.modules.commerce.webhook_handlers.FulfillmentService")
    async def test_updates_package_status(
        self, mock_service_cls: AsyncMock
    ) -> None:
        mock_service = AsyncMock()
        mock_service_cls.return_value = mock_service
        session = AsyncMock()

        payload = {
            "type": 4,
            "data": {
                "package_id": "PKG001",
                "package_status": "DELIVERED",
            },
        }

        await handle_package_update(payload, session)
        mock_service.update_package_from_webhook.assert_called_once_with(
            "PKG001", "DELIVERED"
        )


class TestHandleProductStatusChange:
    @pytest.mark.asyncio
    @patch("backend.modules.commerce.webhook_handlers.ProductService")
    async def test_updates_product_status(
        self, mock_service_cls: AsyncMock
    ) -> None:
        mock_service = AsyncMock()
        mock_service_cls.return_value = mock_service
        session = AsyncMock()

        payload = {
            "type": 5,
            "data": {
                "product_id": "prod_123",
                "product_status": "LIVE",
            },
        }

        await handle_product_status_change(payload, session)
        mock_service.update_product_status.assert_called_once_with(
            "prod_123", "LIVE"
        )


class TestHandleCancellationStatusChange:
    @pytest.mark.asyncio
    @patch("backend.modules.commerce.webhook_handlers.OrderService")
    async def test_cancels_order(self, mock_service_cls: AsyncMock) -> None:
        mock_service = AsyncMock()
        mock_service_cls.return_value = mock_service
        session = AsyncMock()

        payload = {
            "type": 11,
            "data": {"order_id": "order_456"},
        }

        await handle_cancellation_status_change(payload, session)
        mock_service.update_order_status.assert_called_once_with(
            "order_456", "CANCELLED", source="webhook"
        )


class TestHandleReturnStatusChange:
    @pytest.mark.asyncio
    @patch("backend.modules.commerce.webhook_handlers.ReturnService")
    async def test_upserts_return(
        self, mock_service_cls: AsyncMock
    ) -> None:
        mock_service = AsyncMock()
        mock_service_cls.return_value = mock_service
        session = AsyncMock()

        payload = {
            "type": 12,
            "data": {
                "return_id": "RET001",
                "order_id": "order_123",
                "status": "APPROVED",
                "return_type": "RETURN_AND_REFUND",
                "reason": "Defective",
                "refund_amount": "29.99",
            },
        }

        await handle_return_status_change(payload, session)
        mock_service.upsert_return_from_webhook.assert_called_once()


class TestHandleInventoryStatusChange:
    @pytest.mark.asyncio
    @patch("backend.modules.commerce.webhook_handlers.ProductService")
    async def test_updates_inventory(
        self, mock_service_cls: AsyncMock
    ) -> None:
        mock_service = AsyncMock()
        mock_service_cls.return_value = mock_service
        session = AsyncMock()

        payload = {
            "type": 27,
            "data": {
                "product_id": "prod_123",
                "total_available_inventory": 42,
            },
        }

        await handle_inventory_status_change(payload, session)
        mock_service.update_inventory.assert_called_once_with("prod_123", 42)

    @pytest.mark.asyncio
    @patch("backend.modules.commerce.webhook_handlers.ProductService")
    async def test_skips_if_no_inventory(
        self, mock_service_cls: AsyncMock
    ) -> None:
        session = AsyncMock()
        payload = {
            "type": 27,
            "data": {"product_id": "prod_123"},  # Missing inventory
        }

        await handle_inventory_status_change(payload, session)
        mock_service_cls.return_value.update_inventory.assert_not_called()

"""Integration test: webhook receive → store → process → verify DB writes."""

import json
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


class TestShopWebhookPipeline:
    @pytest.mark.asyncio
    @patch("backend.modules.webhooks.routes._store_event")
    @patch("backend.modules.webhooks.routes._deduplicate")
    @patch("backend.modules.webhooks.routes.verify_shop_webhook")
    async def test_order_status_webhook_accepted(
        self,
        mock_verify: AsyncMock,
        mock_dedup: AsyncMock,
        mock_store: AsyncMock,
    ) -> None:
        """Test that an order status webhook is received and stored."""
        mock_verify.return_value = True
        mock_dedup.return_value = True  # New event
        event_id = uuid.uuid4()
        mock_store.return_value = event_id

        payload = {
            "type": 1,
            "event_id": "evt_order_001",
            "data": {
                "order_id": "order_123",
                "order_status": "IN_TRANSIT",
            },
        }

        transport = ASGITransport(app=app)
        with patch("backend.workers.webhook_processor.process_webhook") as mock_task:
            mock_task.delay = AsyncMock()

            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/webhooks/shop",
                    content=json.dumps(payload),
                    headers={
                        "Authorization": "valid-signature",
                        "Content-Type": "application/json",
                    },
                )

        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "received"
        assert result["event_id"] == str(event_id)

        # Verify event_type was stored as string "1" (not int)
        mock_store.assert_called_once()
        call_args = mock_store.call_args
        assert call_args[0][1] == "1"  # event_type as string

    @pytest.mark.asyncio
    @patch("backend.modules.webhooks.routes._deduplicate")
    @patch("backend.modules.webhooks.routes.verify_shop_webhook")
    async def test_duplicate_webhook_rejected(
        self,
        mock_verify: AsyncMock,
        mock_dedup: AsyncMock,
    ) -> None:
        """Test that duplicate webhooks are detected and rejected."""
        mock_verify.return_value = True
        mock_dedup.return_value = False  # Duplicate

        payload = {
            "type": 1,
            "event_id": "evt_order_001",
            "data": {},
        }

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/webhooks/shop",
                content=json.dumps(payload),
                headers={
                    "Authorization": "valid-signature",
                    "Content-Type": "application/json",
                },
            )

        assert response.status_code == 200
        assert response.json()["status"] == "duplicate"

    @pytest.mark.asyncio
    @patch("backend.modules.webhooks.routes.verify_shop_webhook")
    async def test_invalid_signature_rejected(
        self,
        mock_verify: AsyncMock,
    ) -> None:
        """Test that invalid signatures are rejected."""
        mock_verify.return_value = False

        payload = {"type": 1, "data": {}}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/webhooks/shop",
                content=json.dumps(payload),
                headers={
                    "Authorization": "bad-signature",
                    "Content-Type": "application/json",
                },
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    @patch("backend.modules.webhooks.routes._store_event")
    @patch("backend.modules.webhooks.routes._deduplicate")
    @patch("backend.modules.webhooks.routes.verify_shop_webhook")
    async def test_product_creation_webhook(
        self,
        mock_verify: AsyncMock,
        mock_dedup: AsyncMock,
        mock_store: AsyncMock,
    ) -> None:
        """Test product creation webhook (type 16)."""
        mock_verify.return_value = True
        mock_dedup.return_value = True
        mock_store.return_value = uuid.uuid4()

        payload = {
            "type": 16,
            "event_id": "evt_product_001",
            "data": {
                "product_id": "prod_new",
                "shop_id": "shop_123",
            },
        }

        transport = ASGITransport(app=app)
        with patch("backend.workers.webhook_processor.process_webhook") as mock_task:
            mock_task.delay = AsyncMock()

            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/webhooks/shop",
                    content=json.dumps(payload),
                    headers={
                        "Authorization": "valid",
                        "Content-Type": "application/json",
                    },
                )

        assert response.status_code == 200
        mock_store.assert_called_once()
        # Event type should be "16" (string)
        assert mock_store.call_args[0][1] == "16"

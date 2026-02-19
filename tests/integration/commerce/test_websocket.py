"""Integration tests for WebSocket commerce endpoint."""

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


class TestWebSocketAuth:
    @pytest.mark.asyncio
    async def test_rejects_missing_token(self) -> None:
        """WebSocket without token should be rejected."""
        from starlette.testclient import TestClient

        client = TestClient(app)
        workspace_id = uuid.uuid4()

        with pytest.raises(Exception):
            with client.websocket_connect(
                f"/api/commerce/ws/{workspace_id}"
            ):
                pass

    @pytest.mark.asyncio
    async def test_rejects_invalid_token(self) -> None:
        """WebSocket with invalid JWT should be rejected."""
        from starlette.testclient import TestClient

        client = TestClient(app)
        workspace_id = uuid.uuid4()

        with pytest.raises(Exception):
            with client.websocket_connect(
                f"/api/commerce/ws/{workspace_id}?token=invalid-token"
            ):
                pass


class TestWebSocketMessages:
    @pytest.mark.asyncio
    @patch("backend.modules.commerce.routes.ws.get_redis")
    async def test_receives_published_message(
        self,
        mock_get_redis: AsyncMock,
    ) -> None:
        """Test that a message published to Redis is forwarded via WebSocket."""
        from backend.auth.jwt import create_access_token
        from starlette.testclient import TestClient

        # Create a valid token
        user_id = uuid.uuid4()
        token = create_access_token(user_id=user_id)

        workspace_id = uuid.uuid4()

        # Mock Redis pubsub - pubsub() is sync, so use MagicMock
        mock_redis = AsyncMock()
        mock_pubsub = AsyncMock()
        mock_redis.pubsub = MagicMock(return_value=mock_pubsub)

        # First call returns a message, second returns None (to break the loop)
        test_message = json.dumps({
            "type": "order_status_change",
            "order_id": str(uuid.uuid4()),
            "from_status": "awaiting_shipment",
            "to_status": "in_transit",
        })

        call_count = 0

        async def mock_get_message(ignore_subscribe_messages=True, timeout=1.0):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {
                    "type": "message",
                    "data": test_message.encode("utf-8"),
                }
            return None

        mock_pubsub.get_message = mock_get_message
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.close = AsyncMock()
        mock_get_redis.return_value = mock_redis

        client = TestClient(app)
        with client.websocket_connect(
            f"/api/commerce/ws/{workspace_id}?token={token}"
        ) as ws:
            data = ws.receive_text()
            parsed = json.loads(data)
            assert parsed["type"] == "order_status_change"
            assert parsed["to_status"] == "in_transit"

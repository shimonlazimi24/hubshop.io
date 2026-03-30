"""Tests for Connect WebSocket endpoint."""

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.testclient import TestClient

from backend.main import app


class TestConnectWebSocketAuth:
    @pytest.mark.asyncio
    async def test_rejects_missing_token(self) -> None:
        client = TestClient(app)
        workspace_id = uuid.uuid4()

        with pytest.raises(Exception):
            with client.websocket_connect(f"/api/connect/ws/{workspace_id}"):
                pass

    @pytest.mark.asyncio
    async def test_rejects_invalid_token(self) -> None:
        client = TestClient(app)
        workspace_id = uuid.uuid4()

        with (
            pytest.raises(Exception),
            client.websocket_connect(f"/api/connect/ws/{workspace_id}?token=invalid"),
        ):
            pass


class TestConnectWebSocketMessages:
    @pytest.mark.asyncio
    @patch("backend.modules.connect.ws.get_redis")
    async def test_receives_sync_progress(self, mock_get_redis: AsyncMock) -> None:
        from backend.auth.jwt import create_access_token

        user_id = uuid.uuid4()
        token = create_access_token(user_id=user_id)
        workspace_id = uuid.uuid4()

        mock_redis = AsyncMock()
        mock_pubsub = AsyncMock()
        mock_redis.pubsub = MagicMock(return_value=mock_pubsub)

        test_message = json.dumps(
            {
                "type": "sync_progress",
                "platform": "shop",
                "sync_type": "orders",
                "items_synced": 50,
                "items_total": 200,
            }
        )

        call_count = 0

        async def mock_get_message(ignore_subscribe_messages=True, timeout=1.0):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"type": "message", "data": test_message.encode("utf-8")}
            return None

        mock_pubsub.get_message = mock_get_message
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.close = AsyncMock()
        mock_get_redis.return_value = mock_redis

        client = TestClient(app)
        with client.websocket_connect(
            f"/api/connect/ws/{workspace_id}?token={token}"
        ) as ws:
            data = ws.receive_text()
            parsed = json.loads(data)
            assert parsed["type"] == "sync_progress"
            assert parsed["items_synced"] == 50

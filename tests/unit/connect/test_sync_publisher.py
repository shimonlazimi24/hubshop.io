"""Tests for sync progress publisher."""

import json
import uuid
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.connect.services.sync_publisher import publish_sync_event


class TestPublishSyncEvent:
    @pytest.mark.asyncio
    @patch("backend.modules.connect.services.sync_publisher.get_redis")
    async def test_publishes_progress_event(self, mock_get_redis: AsyncMock) -> None:
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        workspace_id = uuid.uuid4()
        await publish_sync_event(
            workspace_id=workspace_id,
            event_type="sync_progress",
            platform="shop",
            sync_type="orders",
            items_synced=50,
            items_total=200,
        )

        mock_redis.publish.assert_called_once()
        channel = mock_redis.publish.call_args[0][0]
        assert channel == f"connect:sync:{workspace_id}"
        payload = json.loads(mock_redis.publish.call_args[0][1])
        assert payload["type"] == "sync_progress"
        assert payload["items_synced"] == 50

    @pytest.mark.asyncio
    @patch("backend.modules.connect.services.sync_publisher.get_redis")
    async def test_publishes_complete_event(self, mock_get_redis: AsyncMock) -> None:
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        workspace_id = uuid.uuid4()
        await publish_sync_event(
            workspace_id=workspace_id,
            event_type="sync_complete",
            platform="shop",
            sync_type="orders",
            items_synced=200,
            items_total=200,
        )

        payload = json.loads(mock_redis.publish.call_args[0][1])
        assert payload["type"] == "sync_complete"
        assert payload["items_synced"] == 200

    @pytest.mark.asyncio
    @patch("backend.modules.connect.services.sync_publisher.get_redis")
    async def test_publishes_error_event(self, mock_get_redis: AsyncMock) -> None:
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        workspace_id = uuid.uuid4()
        await publish_sync_event(
            workspace_id=workspace_id,
            event_type="sync_failed",
            platform="marketing",
            sync_type="campaigns",
            error="API rate limited",
        )

        payload = json.loads(mock_redis.publish.call_args[0][1])
        assert payload["type"] == "sync_failed"
        assert payload["error"] == "API rate limited"

"""Tests for webhook route handlers (backend/modules/webhooks/routes.py)."""

import json
import uuid
from unittest.mock import AsyncMock, patch

import pytest

from backend.db.models.platform import Platform


@pytest.mark.unit
class TestShopWebhookRoute:
    """Tests for the POST /webhooks/shop endpoint."""

    async def test_valid_shop_webhook_stores_event(self) -> None:
        """Valid signature should store event and return event_id."""
        payload = {
            "type": "ORDER_STATUS_CHANGE",
            "event_id": "evt-shop-001",
            "data": {"order_id": "123"},
        }
        body = json.dumps(payload).encode()

        with (
            patch(
                "backend.modules.webhooks.routes.verify_shop_webhook",
                return_value=True,
            ),
            patch(
                "backend.modules.webhooks.routes._deduplicate",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "backend.modules.webhooks.routes._store_event",
                new_callable=AsyncMock,
                return_value=uuid.uuid4(),
            ) as mock_store,
            patch("backend.workers.webhook_processor.process_webhook") as mock_task,
        ):
            from backend.modules.webhooks.routes import shop_webhook

            # Create a mock request
            mock_request = AsyncMock()
            mock_request.body.return_value = body

            result = await shop_webhook(
                request=mock_request,
                authorization="valid-sig",
            )

        assert result["status"] == "received"
        assert "event_id" in result
        mock_store.assert_awaited_once()
        # Verify the stored event has correct platform
        call_args = mock_store.call_args
        assert call_args[0][0] == Platform.SHOP
        assert call_args[0][1] == "ORDER_STATUS_CHANGE"

    async def test_invalid_shop_signature_raises_401(self) -> None:
        """Invalid shop webhook signature should raise 401."""
        from fastapi import HTTPException

        with patch(
            "backend.modules.webhooks.routes.verify_shop_webhook",
            return_value=False,
        ):
            from backend.modules.webhooks.routes import shop_webhook

            mock_request = AsyncMock()
            mock_request.body.return_value = b'{"type":"test"}'

            with pytest.raises(HTTPException) as exc_info:
                await shop_webhook(
                    request=mock_request,
                    authorization="bad-sig",
                )

            assert exc_info.value.status_code == 401

    async def test_duplicate_shop_event_returns_duplicate(self) -> None:
        """Duplicate event (already processed) should return 'duplicate' status."""
        payload = {
            "type": "ORDER_STATUS_CHANGE",
            "event_id": "evt-duplicate-001",
        }
        body = json.dumps(payload).encode()

        with (
            patch(
                "backend.modules.webhooks.routes.verify_shop_webhook",
                return_value=True,
            ),
            patch(
                "backend.modules.webhooks.routes._deduplicate",
                new_callable=AsyncMock,
                return_value=False,  # Not new = duplicate
            ),
        ):
            from backend.modules.webhooks.routes import shop_webhook

            mock_request = AsyncMock()
            mock_request.body.return_value = body

            result = await shop_webhook(
                request=mock_request,
                authorization="valid-sig",
            )

        assert result["status"] == "duplicate"

    async def test_shop_webhook_enqueues_celery_task(self) -> None:
        """After storing, should enqueue the process_webhook Celery task."""
        event_id = uuid.uuid4()
        payload = {"type": "PRODUCT_UPDATE", "event_id": "evt-task-001"}
        body = json.dumps(payload).encode()

        with (
            patch(
                "backend.modules.webhooks.routes.verify_shop_webhook",
                return_value=True,
            ),
            patch(
                "backend.modules.webhooks.routes._deduplicate",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "backend.modules.webhooks.routes._store_event",
                new_callable=AsyncMock,
                return_value=event_id,
            ),
            patch("backend.workers.webhook_processor.process_webhook") as mock_task,
        ):
            from backend.modules.webhooks.routes import shop_webhook

            mock_request = AsyncMock()
            mock_request.body.return_value = body

            await shop_webhook(
                request=mock_request,
                authorization="valid-sig",
            )

        mock_task.delay.assert_called_once_with(str(event_id))


@pytest.mark.unit
class TestDeveloperWebhookRoute:
    """Tests for the POST /webhooks/developer endpoint."""

    async def test_valid_developer_webhook_stores_event(self) -> None:
        """Valid developer signature stores event and returns event_id."""
        payload = {
            "event": "video.publish",
            "event_id": "evt-dev-001",
            "data": {},
        }
        body = json.dumps(payload).encode()

        with (
            patch(
                "backend.modules.webhooks.routes.verify_developer_webhook",
                return_value=True,
            ),
            patch(
                "backend.modules.webhooks.routes._deduplicate",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "backend.modules.webhooks.routes._store_event",
                new_callable=AsyncMock,
                return_value=uuid.uuid4(),
            ) as mock_store,
            patch("backend.workers.webhook_processor.process_webhook") as mock_task,
        ):
            from backend.modules.webhooks.routes import developer_webhook

            mock_request = AsyncMock()
            mock_request.body.return_value = body

            result = await developer_webhook(
                request=mock_request,
                tiktok_signature="t=123,s=valid",
            )

        assert result["status"] == "received"
        call_args = mock_store.call_args
        assert call_args[0][0] == Platform.DEVELOPER
        assert call_args[0][1] == "video.publish"

    async def test_invalid_developer_signature_raises_401(self) -> None:
        """Invalid developer webhook signature should raise 401."""
        from fastapi import HTTPException

        with patch(
            "backend.modules.webhooks.routes.verify_developer_webhook",
            return_value=False,
        ):
            from backend.modules.webhooks.routes import developer_webhook

            mock_request = AsyncMock()
            mock_request.body.return_value = b'{"event":"test"}'

            with pytest.raises(HTTPException) as exc_info:
                await developer_webhook(
                    request=mock_request,
                    tiktok_signature="t=123,s=bad",
                )

            assert exc_info.value.status_code == 401

    async def test_duplicate_developer_event(self) -> None:
        """Duplicate developer event returns 'duplicate' status."""
        payload = {"event": "video.publish", "event_id": "evt-dup-dev"}
        body = json.dumps(payload).encode()

        with (
            patch(
                "backend.modules.webhooks.routes.verify_developer_webhook",
                return_value=True,
            ),
            patch(
                "backend.modules.webhooks.routes._deduplicate",
                new_callable=AsyncMock,
                return_value=False,
            ),
        ):
            from backend.modules.webhooks.routes import developer_webhook

            mock_request = AsyncMock()
            mock_request.body.return_value = body

            result = await developer_webhook(
                request=mock_request,
                tiktok_signature="t=123,s=valid",
            )

        assert result["status"] == "duplicate"


@pytest.mark.unit
class TestMarketingWebhookRoute:
    """Tests for the POST /webhooks/marketing endpoint."""

    async def test_marketing_webhook_stores_event(self) -> None:
        """Marketing webhook should store event (no signature check)."""
        payload = {"type": "campaign.status_change", "event_id": "evt-mkt-001"}
        body = json.dumps(payload).encode()

        with (
            patch(
                "backend.modules.webhooks.routes._deduplicate",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "backend.modules.webhooks.routes._store_event",
                new_callable=AsyncMock,
                return_value=uuid.uuid4(),
            ) as mock_store,
            patch("backend.workers.webhook_processor.process_webhook") as mock_task,
        ):
            from backend.modules.webhooks.routes import marketing_webhook

            mock_request = AsyncMock()
            mock_request.body.return_value = body

            result = await marketing_webhook(request=mock_request)

        assert result["status"] == "received"
        call_args = mock_store.call_args
        assert call_args[0][0] == Platform.MARKETING

    async def test_duplicate_marketing_event(self) -> None:
        """Duplicate marketing event returns 'duplicate'."""
        payload = {"type": "ad.update", "event_id": "evt-mkt-dup"}
        body = json.dumps(payload).encode()

        with (
            patch(
                "backend.modules.webhooks.routes._deduplicate",
                new_callable=AsyncMock,
                return_value=False,
            ),
        ):
            from backend.modules.webhooks.routes import marketing_webhook

            mock_request = AsyncMock()
            mock_request.body.return_value = body

            result = await marketing_webhook(request=mock_request)

        assert result["status"] == "duplicate"


@pytest.mark.unit
class TestDeduplication:
    """Tests for the _deduplicate helper function."""

    async def test_new_event_returns_true(self) -> None:
        """First occurrence of an idempotency key returns True (is new)."""
        mock_redis = AsyncMock()
        mock_redis.set.return_value = True  # nx=True succeeded

        with patch(
            "backend.modules.webhooks.routes.get_redis",
            new_callable=AsyncMock,
            return_value=mock_redis,
        ):
            from backend.modules.webhooks.routes import _deduplicate

            result = await _deduplicate("shop:evt-001")

        assert result is True
        mock_redis.set.assert_awaited_once_with(
            "webhook:dedup:shop:evt-001", "1", nx=True, ex=86400
        )

    async def test_duplicate_event_returns_false(self) -> None:
        """Already-seen idempotency key returns False (duplicate)."""
        mock_redis = AsyncMock()
        mock_redis.set.return_value = None  # nx=True failed (key exists)

        with patch(
            "backend.modules.webhooks.routes.get_redis",
            new_callable=AsyncMock,
            return_value=mock_redis,
        ):
            from backend.modules.webhooks.routes import _deduplicate

            result = await _deduplicate("shop:evt-001")

        assert result is False

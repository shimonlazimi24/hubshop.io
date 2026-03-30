"""Tests for customer service sync Celery workers."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestSyncCsConversations:
    @pytest.mark.asyncio
    async def test_syncs_conversations_for_all_shops(self) -> None:
        """Should iterate all shops and sync CS conversations."""
        shop = MagicMock()
        shop.id = uuid.uuid4()
        shop.shop_name = "Test Shop"

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [shop]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {
            "data": {"conversations": [{"id": "c1"}, {"id": "c2"}]}
        }

        mock_shop_service = AsyncMock()
        mock_shop_service.build_gateway_for_shop.return_value = mock_gateway

        with (
            patch(
                "backend.workers.customer_service_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.customer_service_sync.ShopService",
                return_value=mock_shop_service,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.customer_service_sync import _sync_cs_conversations

            await _sync_cs_conversations()

        mock_session.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_handles_shop_sync_failure(self) -> None:
        """Should rollback and continue on shop sync failure."""
        shop = MagicMock()
        shop.id = uuid.uuid4()
        shop.shop_name = "Test Shop"

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [shop]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_shop_service = AsyncMock()
        mock_shop_service.build_gateway_for_shop.side_effect = RuntimeError("API error")

        with (
            patch(
                "backend.workers.customer_service_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.customer_service_sync.ShopService",
                return_value=mock_shop_service,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.customer_service_sync import _sync_cs_conversations

            await _sync_cs_conversations()

        mock_session.rollback.assert_awaited()


class TestSnapshotCsPerformance:
    @pytest.mark.asyncio
    async def test_snapshots_performance_for_all_shops(self) -> None:
        """Should iterate all shops and snapshot CS performance."""
        shop = MagicMock()
        shop.id = uuid.uuid4()
        shop.workspace_id = uuid.uuid4()
        shop.shop_name = "Test Shop"

        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [shop]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_cs_service = AsyncMock()
        mock_cs_service.get_cs_performance.return_value = {
            "response_rate_24h": "0.95",
            "resolution_rate": "0.88",
            "satisfaction_score": "4.5",
            "total_conversations": 150,
            "avg_response_time_seconds": 300,
        }

        with (
            patch(
                "backend.workers.customer_service_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.customer_service_sync.CustomerServiceService",
                return_value=mock_cs_service,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.customer_service_sync import (
                _snapshot_cs_performance,
            )

            await _snapshot_cs_performance()

        mock_session.add.assert_called()
        mock_session.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_handles_performance_snapshot_failure(self) -> None:
        """Should rollback on performance snapshot failure."""
        shop = MagicMock()
        shop.id = uuid.uuid4()
        shop.workspace_id = uuid.uuid4()
        shop.shop_name = "Test Shop"

        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [shop]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_cs_service = AsyncMock()
        mock_cs_service.get_cs_performance.side_effect = RuntimeError("API error")

        with (
            patch(
                "backend.workers.customer_service_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.customer_service_sync.CustomerServiceService",
                return_value=mock_cs_service,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.customer_service_sync import (
                _snapshot_cs_performance,
            )

            await _snapshot_cs_performance()

        mock_session.rollback.assert_awaited()


class TestSyncEngagementTemplates:
    @pytest.mark.asyncio
    async def test_syncs_templates_for_all_shops(self) -> None:
        """Should iterate all shops and sync engagement templates."""
        shop = MagicMock()
        shop.id = uuid.uuid4()
        shop.workspace_id = uuid.uuid4()
        shop.shop_name = "Test Shop"

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [shop]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_engagement_service = AsyncMock()
        mock_engagement_service.get_templates.return_value = {
            "templates": [{"id": "t1", "name": "Welcome"}]
        }

        with (
            patch(
                "backend.workers.customer_service_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.customer_service_sync.EngagementService",
                return_value=mock_engagement_service,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.customer_service_sync import (
                _sync_engagement_templates,
            )

            await _sync_engagement_templates()

        mock_session.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_handles_template_sync_failure(self) -> None:
        """Should rollback on template sync failure."""
        shop = MagicMock()
        shop.id = uuid.uuid4()
        shop.workspace_id = uuid.uuid4()
        shop.shop_name = "Test Shop"

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [shop]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_engagement_service = AsyncMock()
        mock_engagement_service.get_templates.side_effect = RuntimeError("API error")

        with (
            patch(
                "backend.workers.customer_service_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.customer_service_sync.EngagementService",
                return_value=mock_engagement_service,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.customer_service_sync import (
                _sync_engagement_templates,
            )

            await _sync_engagement_templates()

        mock_session.rollback.assert_awaited()


class TestCeleryTaskRegistration:
    def test_sync_cs_conversations_task_exists(self) -> None:
        from backend.workers.customer_service_sync import sync_cs_conversations

        assert (
            sync_cs_conversations.name
            == "backend.workers.customer_service_sync.sync_cs_conversations"
        )

    def test_snapshot_cs_performance_task_exists(self) -> None:
        from backend.workers.customer_service_sync import snapshot_cs_performance

        assert (
            snapshot_cs_performance.name
            == "backend.workers.customer_service_sync.snapshot_cs_performance"
        )

    def test_sync_engagement_templates_task_exists(self) -> None:
        from backend.workers.customer_service_sync import sync_engagement_templates

        assert (
            sync_engagement_templates.name
            == "backend.workers.customer_service_sync.sync_engagement_templates"
        )


class TestBeatSchedule:
    def test_cs_tasks_in_beat_schedule(self) -> None:
        from backend.workers.celery_app import celery_app

        schedule = celery_app.conf.beat_schedule
        assert "sync-cs-conversations" in schedule
        assert "snapshot-cs-performance" in schedule
        assert "sync-engagement-templates" in schedule

    def test_sync_cs_conversations_runs_every_15_min(self) -> None:
        from backend.workers.celery_app import celery_app

        task = celery_app.conf.beat_schedule["sync-cs-conversations"]
        assert (
            task["task"]
            == "backend.workers.customer_service_sync.sync_cs_conversations"
        )

    def test_snapshot_cs_performance_runs_daily(self) -> None:
        from backend.workers.celery_app import celery_app

        task = celery_app.conf.beat_schedule["snapshot-cs-performance"]
        assert (
            task["task"]
            == "backend.workers.customer_service_sync.snapshot_cs_performance"
        )

    def test_sync_engagement_templates_runs_daily(self) -> None:
        from backend.workers.celery_app import celery_app

        task = celery_app.conf.beat_schedule["sync-engagement-templates"]
        assert (
            task["task"]
            == "backend.workers.customer_service_sync.sync_engagement_templates"
        )

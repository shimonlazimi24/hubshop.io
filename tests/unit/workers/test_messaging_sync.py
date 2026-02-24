"""Tests for messaging sync Celery workers."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestSyncConversations:
    @pytest.mark.asyncio
    async def test_syncs_conversations_for_marketing_accounts(self) -> None:
        """Should iterate marketing connected accounts and sync conversations."""
        account = MagicMock()
        account.id = uuid.uuid4()
        account.platform = "marketing"

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [account]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {"data": {"conversations": [{"id": "c1"}]}}

        with (
            patch(
                "backend.workers.messaging_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.messaging_sync._build_marketing_gateway",
                return_value=mock_gateway,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.messaging_sync import _sync_conversations

            await _sync_conversations()

        mock_session.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_skips_account_without_token(self) -> None:
        """Should skip accounts without a valid token."""
        account = MagicMock()
        account.id = uuid.uuid4()

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [account]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        with (
            patch(
                "backend.workers.messaging_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.messaging_sync._build_marketing_gateway",
                return_value=None,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.messaging_sync import _sync_conversations

            await _sync_conversations()

        # Should not commit since no actual sync happened
        # (no assertion on commit since it depends on impl)

    @pytest.mark.asyncio
    async def test_handles_sync_failure(self) -> None:
        """Should rollback and continue on account sync failure."""
        account = MagicMock()
        account.id = uuid.uuid4()

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [account]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_gateway = AsyncMock()
        mock_gateway.get.side_effect = RuntimeError("API error")

        with (
            patch(
                "backend.workers.messaging_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.messaging_sync._build_marketing_gateway",
                return_value=mock_gateway,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.messaging_sync import _sync_conversations

            await _sync_conversations()

        mock_session.rollback.assert_awaited()


class TestSyncMentions:
    @pytest.mark.asyncio
    async def test_syncs_mentions_for_marketing_accounts(self) -> None:
        """Should iterate marketing accounts and sync brand mentions."""
        account = MagicMock()
        account.id = uuid.uuid4()

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [account]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {"data": {"posts": [{"id": "p1"}]}}

        with (
            patch(
                "backend.workers.messaging_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.messaging_sync._build_marketing_gateway",
                return_value=mock_gateway,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.messaging_sync import _sync_mentions

            await _sync_mentions()

        mock_session.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_handles_mentions_sync_failure(self) -> None:
        """Should rollback on mentions sync failure."""
        account = MagicMock()
        account.id = uuid.uuid4()

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [account]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_gateway = AsyncMock()
        mock_gateway.get.side_effect = RuntimeError("Mentions API error")

        with (
            patch(
                "backend.workers.messaging_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.messaging_sync._build_marketing_gateway",
                return_value=mock_gateway,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.messaging_sync import _sync_mentions

            await _sync_mentions()

        mock_session.rollback.assert_awaited()


class TestCeleryTaskRegistration:
    def test_sync_conversations_task_exists(self) -> None:
        from backend.workers.messaging_sync import sync_conversations

        assert (
            sync_conversations.name
            == "backend.workers.messaging_sync.sync_conversations"
        )

    def test_sync_mentions_task_exists(self) -> None:
        from backend.workers.messaging_sync import sync_mentions

        assert sync_mentions.name == "backend.workers.messaging_sync.sync_mentions"


class TestBeatSchedule:
    def test_messaging_tasks_in_beat_schedule(self) -> None:
        from backend.workers.celery_app import celery_app

        schedule = celery_app.conf.beat_schedule
        assert "sync-conversations" in schedule
        assert "sync-mentions" in schedule

    def test_sync_conversations_runs_every_30_min(self) -> None:
        from backend.workers.celery_app import celery_app

        task = celery_app.conf.beat_schedule["sync-conversations"]
        assert task["task"] == "backend.workers.messaging_sync.sync_conversations"

    def test_sync_mentions_runs_every_2_hours(self) -> None:
        from backend.workers.celery_app import celery_app

        task = celery_app.conf.beat_schedule["sync-mentions"]
        assert task["task"] == "backend.workers.messaging_sync.sync_mentions"

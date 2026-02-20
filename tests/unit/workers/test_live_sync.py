"""Tests for LIVE sync Celery workers."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestMonitorLiveStream:
    @pytest.mark.asyncio
    async def test_handles_tiktok_live_not_installed(self) -> None:
        """Should set session status to ERROR when TikTokLive isn't installed."""
        session_id = str(uuid.uuid4())

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()

        mock_wrapper = MagicMock()
        mock_wrapper.connect = AsyncMock(
            side_effect=NotImplementedError("not installed")
        )
        mock_wrapper.on_event = MagicMock()

        with (
            patch(
                "backend.workers.live_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.live_sync.TikTokLiveClientWrapper",
                return_value=mock_wrapper,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.live_sync import _monitor_live_stream

            await _monitor_live_stream(session_id, "test_user")

        mock_session.execute.assert_awaited()
        mock_session.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_handles_connection_error(self) -> None:
        """Should set session status to ERROR on unexpected connection failure."""
        session_id = str(uuid.uuid4())

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()

        mock_wrapper = MagicMock()
        mock_wrapper.connect = AsyncMock(
            side_effect=ConnectionError("Stream unavailable")
        )
        mock_wrapper.on_event = MagicMock()

        with (
            patch(
                "backend.workers.live_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.live_sync.TikTokLiveClientWrapper",
                return_value=mock_wrapper,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.live_sync import _monitor_live_stream

            await _monitor_live_stream(session_id, "test_user")

        mock_session.execute.assert_awaited()
        mock_session.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_registers_callbacks_for_all_event_types(self) -> None:
        """Should register event callbacks for all event types."""
        session_id = str(uuid.uuid4())

        mock_wrapper = MagicMock()
        mock_wrapper.connect = AsyncMock()
        mock_wrapper.on_event = MagicMock()

        with patch(
            "backend.workers.live_sync.TikTokLiveClientWrapper",
            return_value=mock_wrapper,
        ):
            from backend.workers.live_sync import _monitor_live_stream

            await _monitor_live_stream(session_id, "test_user")

        from backend.tiktok.live.client import LiveEventType

        assert mock_wrapper.on_event.call_count == len(LiveEventType)


class TestComputeLiveAnalytics:
    @pytest.mark.asyncio
    async def test_computes_analytics_for_session(self) -> None:
        """Should compute and store analytics for a completed session."""
        session_id = str(uuid.uuid4())

        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        from backend.db.models.live import LiveEventType

        count_results = []
        for _ in LiveEventType:
            r = MagicMock()
            r.scalar.return_value = 5
            count_results.append(r)

        viewer_result = MagicMock()
        viewer_result.scalar.return_value = 100

        commenters_result = MagicMock()
        commenters_result.all.return_value = [("user1", 10), ("user2", 5)]

        gifters_result = MagicMock()
        gifters_result.all.return_value = [("gifter1", 3)]

        mock_session.execute = AsyncMock(
            side_effect=count_results
            + [viewer_result, commenters_result, gifters_result]
        )

        with patch(
            "backend.workers.live_sync.async_session_factory"
        ) as mock_factory:
            mock_factory.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.live_sync import _compute_live_analytics

            await _compute_live_analytics(session_id)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_handles_analytics_error(self) -> None:
        """Should rollback on analytics computation failure."""
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(side_effect=RuntimeError("DB error"))
        mock_session.rollback = AsyncMock()

        with patch(
            "backend.workers.live_sync.async_session_factory"
        ) as mock_factory:
            mock_factory.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.live_sync import _compute_live_analytics

            await _compute_live_analytics(str(uuid.uuid4()))

        mock_session.rollback.assert_awaited()


class TestCleanupStaleSessions:
    @pytest.mark.asyncio
    async def test_cleans_up_stale_sessions(self) -> None:
        """Should update sessions stuck monitoring for over 24h."""
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        with patch(
            "backend.workers.live_sync.async_session_factory"
        ) as mock_factory:
            mock_factory.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.live_sync import _cleanup_stale_sessions

            await _cleanup_stale_sessions()

        mock_session.execute.assert_awaited_once()
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_handles_cleanup_error(self) -> None:
        """Should rollback on cleanup failure."""
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(side_effect=RuntimeError("DB error"))
        mock_session.rollback = AsyncMock()

        with patch(
            "backend.workers.live_sync.async_session_factory"
        ) as mock_factory:
            mock_factory.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.live_sync import _cleanup_stale_sessions

            await _cleanup_stale_sessions()

        mock_session.rollback.assert_awaited()


class TestCeleryTaskRegistration:
    def test_monitor_live_stream_task_exists(self) -> None:
        from backend.workers.live_sync import monitor_live_stream

        assert (
            monitor_live_stream.name
            == "backend.workers.live_sync.monitor_live_stream"
        )

    def test_compute_live_analytics_task_exists(self) -> None:
        from backend.workers.live_sync import compute_live_analytics

        assert (
            compute_live_analytics.name
            == "backend.workers.live_sync.compute_live_analytics"
        )

    def test_cleanup_stale_sessions_task_exists(self) -> None:
        from backend.workers.live_sync import cleanup_stale_sessions

        assert (
            cleanup_stale_sessions.name
            == "backend.workers.live_sync.cleanup_stale_sessions"
        )


class TestBeatSchedule:
    def test_intelligence_tasks_in_beat_schedule(self) -> None:
        from backend.workers.celery_app import celery_app

        schedule = celery_app.conf.beat_schedule
        assert "sync-trends" in schedule
        assert "sync-competitor-content" in schedule

    def test_live_tasks_in_beat_schedule(self) -> None:
        from backend.workers.celery_app import celery_app

        schedule = celery_app.conf.beat_schedule
        assert "cleanup-stale-live-sessions" in schedule

    def test_sync_trends_runs_every_4_hours(self) -> None:
        from backend.workers.celery_app import celery_app

        task = celery_app.conf.beat_schedule["sync-trends"]
        assert task["task"] == "backend.workers.intelligence_sync.sync_trends"

    def test_cleanup_runs_hourly(self) -> None:
        from backend.workers.celery_app import celery_app

        task = celery_app.conf.beat_schedule["cleanup-stale-live-sessions"]
        assert (
            task["task"] == "backend.workers.live_sync.cleanup_stale_sessions"
        )

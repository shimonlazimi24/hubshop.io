"""Tests for LiveAnalyticsService - analytics retrieval, events, summary."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.live.services.analytics_service import LiveAnalyticsService


class TestGetSessionAnalytics:
    @pytest.mark.asyncio
    async def test_returns_analytics_for_valid_session(self) -> None:
        workspace_id = uuid.uuid4()
        session_id = uuid.uuid4()

        analytics_obj = SimpleNamespace(
            id=uuid.uuid4(),
            session_id=session_id,
            total_viewers=100,
            engagement_rate=0.75,
        )

        mock_session = AsyncMock()
        # First call: verify session exists
        session_check = MagicMock()
        session_check.scalar_one_or_none.return_value = session_id
        # Second call: fetch analytics
        analytics_result = MagicMock()
        analytics_result.scalar_one_or_none.return_value = analytics_obj
        mock_session.execute = AsyncMock(side_effect=[session_check, analytics_result])

        service = LiveAnalyticsService(mock_session)
        result = await service.get_session_analytics(workspace_id, session_id)

        assert result is not None
        assert result.total_viewers == 100
        assert result.engagement_rate == 0.75

    @pytest.mark.asyncio
    async def test_returns_none_when_session_not_found(self) -> None:
        mock_session = AsyncMock()
        session_check = MagicMock()
        session_check.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = session_check

        service = LiveAnalyticsService(mock_session)
        result = await service.get_session_analytics(uuid.uuid4(), uuid.uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_analytics_not_computed(self) -> None:
        workspace_id = uuid.uuid4()
        session_id = uuid.uuid4()

        mock_session = AsyncMock()
        session_check = MagicMock()
        session_check.scalar_one_or_none.return_value = session_id
        analytics_result = MagicMock()
        analytics_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(side_effect=[session_check, analytics_result])

        service = LiveAnalyticsService(mock_session)
        result = await service.get_session_analytics(workspace_id, session_id)

        assert result is None


class TestGetSessionEvents:
    @pytest.mark.asyncio
    async def test_returns_paginated_events(self) -> None:
        workspace_id = uuid.uuid4()
        session_id = uuid.uuid4()

        event1 = SimpleNamespace(id=uuid.uuid4(), event_type="comment")
        event2 = SimpleNamespace(id=uuid.uuid4(), event_type="like")

        mock_session = AsyncMock()
        # Session check
        session_check = MagicMock()
        session_check.scalar_one_or_none.return_value = session_id
        # Count query
        count_result = MagicMock()
        count_result.scalar_one.return_value = 2
        # Items query
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = [event1, event2]

        mock_session.execute = AsyncMock(
            side_effect=[session_check, count_result, items_result]
        )

        service = LiveAnalyticsService(mock_session)
        result = await service.get_session_events(
            workspace_id, session_id, page=1, page_size=50
        )

        assert result.total == 2
        assert len(result.items) == 2
        assert result.page == 1

    @pytest.mark.asyncio
    async def test_returns_empty_when_session_not_found(self) -> None:
        mock_session = AsyncMock()
        session_check = MagicMock()
        session_check.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = session_check

        service = LiveAnalyticsService(mock_session)
        result = await service.get_session_events(
            uuid.uuid4(), uuid.uuid4(), page=1, page_size=50
        )

        assert result.total == 0
        assert result.items == []

    @pytest.mark.asyncio
    async def test_filters_by_event_type(self) -> None:
        workspace_id = uuid.uuid4()
        session_id = uuid.uuid4()

        comment_event = SimpleNamespace(id=uuid.uuid4(), event_type="comment")

        mock_session = AsyncMock()
        session_check = MagicMock()
        session_check.scalar_one_or_none.return_value = session_id
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = [comment_event]

        mock_session.execute = AsyncMock(
            side_effect=[session_check, count_result, items_result]
        )

        service = LiveAnalyticsService(mock_session)
        result = await service.get_session_events(
            workspace_id, session_id, event_type="comment", page=1, page_size=50
        )

        assert result.total == 1
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_pagination(self) -> None:
        workspace_id = uuid.uuid4()
        session_id = uuid.uuid4()

        mock_session = AsyncMock()
        session_check = MagicMock()
        session_check.scalar_one_or_none.return_value = session_id
        count_result = MagicMock()
        count_result.scalar_one.return_value = 100
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = [
            SimpleNamespace(id=uuid.uuid4()) for _ in range(10)
        ]

        mock_session.execute = AsyncMock(
            side_effect=[session_check, count_result, items_result]
        )

        service = LiveAnalyticsService(mock_session)
        result = await service.get_session_events(
            workspace_id, session_id, page=3, page_size=10
        )

        assert result.total == 100
        assert result.page == 3
        assert result.total_pages == 10


class TestComputeAnalytics:
    @pytest.mark.asyncio
    async def test_dispatches_celery_task(self) -> None:
        mock_session = AsyncMock()
        session_id = uuid.uuid4()

        with patch("backend.workers.live_sync.compute_live_analytics") as mock_task:
            mock_task.delay = MagicMock()

            service = LiveAnalyticsService(mock_session)
            await service.compute_analytics(session_id)

            mock_task.delay.assert_called_once_with(str(session_id))


class TestGetSessionsSummary:
    @pytest.mark.asyncio
    async def test_returns_summary_with_data(self) -> None:
        workspace_id = uuid.uuid4()
        session_id_1 = uuid.uuid4()
        session_id_2 = uuid.uuid4()

        mock_session = AsyncMock()
        # Total count
        total_result = MagicMock()
        total_result.scalar_one.return_value = 2
        # Session IDs
        ids_result = MagicMock()
        ids_result.all.return_value = [(session_id_1,), (session_id_2,)]
        # Analytics aggregation
        agg_result = MagicMock()
        agg_result.one.return_value = (0.65, 500)

        mock_session.execute = AsyncMock(
            side_effect=[total_result, ids_result, agg_result]
        )

        service = LiveAnalyticsService(mock_session)
        result = await service.get_sessions_summary(workspace_id, days=30)

        assert result["total_sessions"] == 2
        assert result["avg_engagement_rate"] == 0.65
        assert result["total_viewers"] == 500
        assert result["period_days"] == 30

    @pytest.mark.asyncio
    async def test_returns_zeros_when_no_sessions(self) -> None:
        mock_session = AsyncMock()
        total_result = MagicMock()
        total_result.scalar_one.return_value = 0
        ids_result = MagicMock()
        ids_result.all.return_value = []

        mock_session.execute = AsyncMock(side_effect=[total_result, ids_result])

        service = LiveAnalyticsService(mock_session)
        result = await service.get_sessions_summary(uuid.uuid4(), days=7)

        assert result["total_sessions"] == 0
        assert result["avg_engagement_rate"] == 0.0
        assert result["total_viewers"] == 0
        assert result["period_days"] == 7

    @pytest.mark.asyncio
    async def test_custom_days_parameter(self) -> None:
        mock_session = AsyncMock()
        total_result = MagicMock()
        total_result.scalar_one.return_value = 0
        ids_result = MagicMock()
        ids_result.all.return_value = []

        mock_session.execute = AsyncMock(side_effect=[total_result, ids_result])

        service = LiveAnalyticsService(mock_session)
        result = await service.get_sessions_summary(uuid.uuid4(), days=90)

        assert result["period_days"] == 90

    @pytest.mark.asyncio
    async def test_rounds_engagement_rate(self) -> None:
        workspace_id = uuid.uuid4()
        session_id_1 = uuid.uuid4()

        mock_session = AsyncMock()
        total_result = MagicMock()
        total_result.scalar_one.return_value = 1
        ids_result = MagicMock()
        ids_result.all.return_value = [(session_id_1,)]
        agg_result = MagicMock()
        agg_result.one.return_value = (0.123456789, 42)

        mock_session.execute = AsyncMock(
            side_effect=[total_result, ids_result, agg_result]
        )

        service = LiveAnalyticsService(mock_session)
        result = await service.get_sessions_summary(workspace_id, days=30)

        assert result["avg_engagement_rate"] == 0.1235

"""Tests for StreamMonitorService - session lifecycle, listing, filtering."""

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.db.models.live import LiveSession, SessionStatus
from backend.modules.live.services.stream_monitor_service import StreamMonitorService


class TestStartMonitoring:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_creates_session_in_monitoring_status(
        self, mock_session: AsyncMock
    ) -> None:
        with patch("backend.workers.live_sync.monitor_live_stream") as mock_task:
            mock_task.delay = MagicMock()
            service = StreamMonitorService(mock_session)
            workspace_id = uuid.uuid4()

            result = await service.start_monitoring(workspace_id, unique_id="test_user")

            assert mock_session.add.called
            added = mock_session.add.call_args_list[0][0][0]
            assert isinstance(added, LiveSession)
            assert added.unique_id == "test_user"
            assert added.status == SessionStatus.MONITORING.value
            assert added.workspace_id == workspace_id

    @pytest.mark.asyncio
    async def test_dispatches_celery_task(self, mock_session: AsyncMock) -> None:
        with patch("backend.workers.live_sync.monitor_live_stream") as mock_task:
            mock_task.delay = MagicMock()
            service = StreamMonitorService(mock_session)

            result = await service.start_monitoring(
                uuid.uuid4(), unique_id="streamer123"
            )

            mock_task.delay.assert_called_once()
            call_args = mock_task.delay.call_args[0]
            assert call_args[1] == "streamer123"

    @pytest.mark.asyncio
    async def test_sets_started_at_timestamp(self, mock_session: AsyncMock) -> None:
        with patch("backend.workers.live_sync.monitor_live_stream") as mock_task:
            mock_task.delay = MagicMock()
            service = StreamMonitorService(mock_session)

            before = datetime.now(tz=UTC)
            await service.start_monitoring(uuid.uuid4(), unique_id="user1")
            after = datetime.now(tz=UTC)

            added = mock_session.add.call_args_list[0][0][0]
            assert before <= added.started_at <= after

    @pytest.mark.asyncio
    async def test_flushes_session(self, mock_session: AsyncMock) -> None:
        with patch("backend.workers.live_sync.monitor_live_stream") as mock_task:
            mock_task.delay = MagicMock()
            service = StreamMonitorService(mock_session)

            await service.start_monitoring(uuid.uuid4(), unique_id="user1")

            mock_session.flush.assert_awaited_once()


class TestStopMonitoring:
    @pytest.mark.asyncio
    async def test_marks_session_as_ended(self) -> None:
        session_id = uuid.uuid4()
        workspace_id = uuid.uuid4()
        live_session = SimpleNamespace(
            id=session_id,
            workspace_id=workspace_id,
            unique_id="test_user",
            status=SessionStatus.MONITORING.value,
            ended_at=None,
        )
        mock_session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = live_session
        mock_session.execute.return_value = result_mock
        mock_session.flush = AsyncMock()

        service = StreamMonitorService(mock_session)
        result = await service.stop_monitoring(workspace_id, session_id)

        assert result is not None
        assert result.status == SessionStatus.ENDED.value
        assert result.ended_at is not None

    @pytest.mark.asyncio
    async def test_returns_none_for_missing_session(self) -> None:
        mock_session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock

        service = StreamMonitorService(mock_session)
        result = await service.stop_monitoring(uuid.uuid4(), uuid.uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_sets_ended_at_timestamp(self) -> None:
        session_id = uuid.uuid4()
        workspace_id = uuid.uuid4()
        live_session = SimpleNamespace(
            id=session_id,
            workspace_id=workspace_id,
            status=SessionStatus.MONITORING.value,
            ended_at=None,
        )
        mock_session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = live_session
        mock_session.execute.return_value = result_mock
        mock_session.flush = AsyncMock()

        service = StreamMonitorService(mock_session)
        before = datetime.now(tz=UTC)
        result = await service.stop_monitoring(workspace_id, session_id)
        after = datetime.now(tz=UTC)

        assert result is not None
        assert before <= result.ended_at <= after


class TestGetSession:
    @pytest.mark.asyncio
    async def test_returns_session(self) -> None:
        session_id = uuid.uuid4()
        workspace_id = uuid.uuid4()
        live_session = SimpleNamespace(
            id=session_id,
            workspace_id=workspace_id,
            unique_id="streamer",
        )
        mock_session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = live_session
        mock_session.execute.return_value = result_mock

        service = StreamMonitorService(mock_session)
        result = await service.get_session(workspace_id, session_id)

        assert result is not None
        assert result.unique_id == "streamer"

    @pytest.mark.asyncio
    async def test_returns_none_for_missing(self) -> None:
        mock_session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock

        service = StreamMonitorService(mock_session)
        result = await service.get_session(uuid.uuid4(), uuid.uuid4())

        assert result is None


class TestListSessions:
    @pytest.mark.asyncio
    async def test_returns_paginated_result(self) -> None:
        mock_session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        s1 = SimpleNamespace(id=uuid.uuid4(), unique_id="user1")
        s2 = SimpleNamespace(id=uuid.uuid4(), unique_id="user2")
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = [s1, s2]

        mock_session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = StreamMonitorService(mock_session)
        result = await service.list_sessions(uuid.uuid4(), page=1, page_size=20)

        assert result.total == 2
        assert len(result.items) == 2
        assert result.page == 1
        assert result.page_size == 20

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_sessions(self) -> None:
        mock_session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = StreamMonitorService(mock_session)
        result = await service.list_sessions(uuid.uuid4())

        assert result.total == 0
        assert result.items == []
        assert result.total_pages == 0

    @pytest.mark.asyncio
    async def test_pagination_calculation(self) -> None:
        mock_session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 25
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = [
            SimpleNamespace(id=uuid.uuid4()) for _ in range(10)
        ]
        mock_session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = StreamMonitorService(mock_session)
        result = await service.list_sessions(uuid.uuid4(), page=2, page_size=10)

        assert result.total == 25
        assert result.page == 2
        assert result.total_pages == 3


class TestGetActiveSessions:
    @pytest.mark.asyncio
    async def test_returns_monitoring_sessions(self) -> None:
        s1 = SimpleNamespace(
            id=uuid.uuid4(),
            status=SessionStatus.MONITORING.value,
        )
        s2 = SimpleNamespace(
            id=uuid.uuid4(),
            status=SessionStatus.MONITORING.value,
        )
        mock_session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [s1, s2]
        mock_session.execute.return_value = result_mock

        service = StreamMonitorService(mock_session)
        result = await service.get_active_sessions(uuid.uuid4())

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_returns_empty_when_none_active(self) -> None:
        mock_session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = result_mock

        service = StreamMonitorService(mock_session)
        result = await service.get_active_sessions(uuid.uuid4())

        assert result == []

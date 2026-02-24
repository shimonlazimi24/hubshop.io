"""Tests for PublishService - list, get, update status, calendar entries."""

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.modules.content.services.publish_service import PublishService


class TestListPublishJobs:
    @pytest.mark.asyncio
    async def test_list_publish_jobs_paginated(self) -> None:
        session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 3
        job1 = SimpleNamespace(id=uuid.uuid4(), title="Video 1", status="PENDING")
        job2 = SimpleNamespace(id=uuid.uuid4(), title="Video 2", status="PUBLISHED")
        job3 = SimpleNamespace(id=uuid.uuid4(), title="Video 3", status="PENDING")
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = [job1, job2, job3]

        session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = PublishService(session)
        result = await service.list_publish_jobs(uuid.uuid4(), page=1, page_size=20)

        assert result.total == 3
        assert len(result.items) == 3
        assert result.page == 1
        assert result.page_size == 20

    @pytest.mark.asyncio
    async def test_list_publish_jobs_empty(self) -> None:
        session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []

        session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = PublishService(session)
        result = await service.list_publish_jobs(uuid.uuid4())

        assert result.total == 0
        assert result.items == []
        assert result.total_pages == 0


class TestGetPublishJob:
    @pytest.mark.asyncio
    async def test_get_publish_job_found(self) -> None:
        job = SimpleNamespace(
            id=uuid.uuid4(),
            publish_id="pub_123",
            title="My Video",
            status="PUBLISHED",
        )
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = job
        session.execute.return_value = result

        service = PublishService(session)
        found = await service.get_publish_job(job.id)

        assert found is not None
        assert found.publish_id == "pub_123"
        assert found.title == "My Video"

    @pytest.mark.asyncio
    async def test_get_publish_job_not_found(self) -> None:
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result

        service = PublishService(session)
        found = await service.get_publish_job(uuid.uuid4())

        assert found is None


class TestUpdatePublishStatus:
    @pytest.mark.asyncio
    async def test_update_publish_status(self) -> None:
        existing_job = SimpleNamespace(
            id=uuid.uuid4(),
            publish_id="pub_456",
            status="PENDING",
            platform_video_id=None,
            error_message=None,
        )
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = existing_job
        session.execute.return_value = result
        session.flush = AsyncMock()

        service = PublishService(session)
        updated = await service.update_publish_status(
            publish_id="pub_456",
            status="PUBLISHED",
            platform_video_id="vid_789",
            error_message=None,
        )

        assert updated is not None
        assert updated.status == "PUBLISHED"
        assert updated.platform_video_id == "vid_789"
        # error_message should remain None since we passed None (falsy)
        assert updated.error_message is None

    @pytest.mark.asyncio
    async def test_update_publish_status_with_error(self) -> None:
        existing_job = SimpleNamespace(
            id=uuid.uuid4(),
            publish_id="pub_err",
            status="PENDING",
            platform_video_id=None,
            error_message=None,
        )
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = existing_job
        session.execute.return_value = result
        session.flush = AsyncMock()

        service = PublishService(session)
        updated = await service.update_publish_status(
            publish_id="pub_err",
            status="FAILED",
            error_message="Upload timed out",
        )

        assert updated is not None
        assert updated.status == "FAILED"
        assert updated.error_message == "Upload timed out"

    @pytest.mark.asyncio
    async def test_update_publish_status_not_found(self) -> None:
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result

        service = PublishService(session)
        updated = await service.update_publish_status(
            publish_id="pub_nonexistent",
            status="PUBLISHED",
        )

        assert updated is None


class TestGetCalendarEntries:
    @pytest.mark.asyncio
    async def test_get_calendar_entries(self) -> None:
        workspace_id = uuid.uuid4()

        # Two videos on the same day, one on another day
        video1 = SimpleNamespace(
            id=uuid.uuid4(),
            platform_video_id="v1",
            create_time=datetime(2026, 2, 10, 12, 0, 0, tzinfo=UTC),
        )
        video2 = SimpleNamespace(
            id=uuid.uuid4(),
            platform_video_id="v2",
            create_time=datetime(2026, 2, 10, 15, 0, 0, tzinfo=UTC),
        )
        video3 = SimpleNamespace(
            id=uuid.uuid4(),
            platform_video_id="v3",
            create_time=datetime(2026, 2, 20, 8, 0, 0, tzinfo=UTC),
        )

        # One publish job on a different day
        job1 = SimpleNamespace(
            id=uuid.uuid4(),
            platform_video_id=None,
            created_at=datetime(2026, 2, 15, 10, 0, 0, tzinfo=UTC),
        )

        video_result = MagicMock()
        video_result.scalars.return_value.all.return_value = [video1, video2, video3]
        job_result = MagicMock()
        job_result.scalars.return_value.all.return_value = [job1]

        session = AsyncMock()
        session.execute = AsyncMock(side_effect=[video_result, job_result])

        service = PublishService(session)
        entries = await service.get_calendar_entries(workspace_id, year=2026, month=2)

        # Should have 3 dates: Feb 10 (2 videos), Feb 15 (1 job), Feb 20 (1 video)
        assert len(entries) == 3
        dates = [e["date"] for e in entries]
        assert "2026-02-10" in dates
        assert "2026-02-15" in dates
        assert "2026-02-20" in dates

        feb10 = next(e for e in entries if e["date"] == "2026-02-10")
        assert feb10["video_count"] == 2

        feb15 = next(e for e in entries if e["date"] == "2026-02-15")
        assert feb15["video_count"] == 1

    @pytest.mark.asyncio
    async def test_get_calendar_entries_empty(self) -> None:
        workspace_id = uuid.uuid4()

        video_result = MagicMock()
        video_result.scalars.return_value.all.return_value = []
        job_result = MagicMock()
        job_result.scalars.return_value.all.return_value = []

        session = AsyncMock()
        session.execute = AsyncMock(side_effect=[video_result, job_result])

        service = PublishService(session)
        entries = await service.get_calendar_entries(workspace_id, year=2026, month=3)

        assert entries == []

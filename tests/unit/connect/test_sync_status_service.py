"""Tests for SyncStatusService — create, update progress, list jobs."""

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.db.models.platform import SyncJobStatus
from backend.modules.connect.services.sync_status_service import SyncStatusService


class TestCreateSyncJob:
    @pytest.mark.asyncio
    async def test_creates_job(self) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        workspace_id = uuid.uuid4()
        account_id = uuid.uuid4()

        service = SyncStatusService(session)
        job = await service.create_sync_job(
            workspace_id=workspace_id,
            connected_account_id=account_id,
            platform="shop",
            sync_type="orders",
        )

        assert session.add.called
        added = session.add.call_args[0][0]
        assert added.workspace_id == workspace_id
        assert added.platform == "shop"
        assert added.sync_type == "orders"
        assert added.status == SyncJobStatus.PENDING


class TestUpdateProgress:
    @pytest.mark.asyncio
    async def test_updates_progress(self) -> None:
        job = SimpleNamespace(
            id=uuid.uuid4(),
            status=SyncJobStatus.RUNNING,
            items_synced=0,
            items_total=None,
        )

        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = job
        session.execute = AsyncMock(return_value=result)

        service = SyncStatusService(session)
        updated = await service.update_progress(job.id, items_synced=50, items_total=200)

        assert updated is not None
        assert updated.items_synced == 50
        assert updated.items_total == 200


class TestCompleteJob:
    @pytest.mark.asyncio
    async def test_marks_completed(self) -> None:
        job = SimpleNamespace(
            id=uuid.uuid4(),
            status=SyncJobStatus.RUNNING,
            items_synced=200,
            items_total=200,
            completed_at=None,
        )

        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = job
        session.execute = AsyncMock(return_value=result)

        service = SyncStatusService(session)
        updated = await service.complete_job(job.id)

        assert updated.status == SyncJobStatus.COMPLETED
        assert updated.completed_at is not None

    @pytest.mark.asyncio
    async def test_marks_failed(self) -> None:
        job = SimpleNamespace(
            id=uuid.uuid4(),
            status=SyncJobStatus.RUNNING,
            items_synced=50,
            items_total=200,
            completed_at=None,
            error_message=None,
        )

        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = job
        session.execute = AsyncMock(return_value=result)

        service = SyncStatusService(session)
        updated = await service.fail_job(job.id, "API rate limited")

        assert updated.status == SyncJobStatus.FAILED
        assert updated.error_message == "API rate limited"
        assert updated.completed_at is not None


class TestListJobs:
    @pytest.mark.asyncio
    async def test_list_recent_jobs(self) -> None:
        workspace_id = uuid.uuid4()
        jobs = [
            SimpleNamespace(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                platform="shop",
                sync_type="orders",
                status=SyncJobStatus.COMPLETED,
                items_synced=100,
                items_total=100,
                error_message=None,
                started_at=datetime(2026, 2, 26, tzinfo=UTC),
                completed_at=datetime(2026, 2, 26, tzinfo=UTC),
                created_at=datetime(2026, 2, 26, tzinfo=UTC),
            ),
        ]

        session = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = jobs
        session.execute = AsyncMock(return_value=result)

        service = SyncStatusService(session)
        result_list = await service.list_recent_jobs(workspace_id, limit=10)

        assert len(result_list) == 1
        assert result_list[0]["platform"] == "shop"
        assert result_list[0]["status"] == "completed"

    @pytest.mark.asyncio
    async def test_get_active_jobs(self) -> None:
        workspace_id = uuid.uuid4()
        jobs = [
            SimpleNamespace(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                platform="shop",
                sync_type="products",
                status=SyncJobStatus.RUNNING,
                items_synced=42,
                items_total=200,
                error_message=None,
                started_at=datetime(2026, 2, 26, tzinfo=UTC),
                completed_at=None,
                created_at=datetime(2026, 2, 26, tzinfo=UTC),
            ),
        ]

        session = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = jobs
        session.execute = AsyncMock(return_value=result)

        service = SyncStatusService(session)
        active = await service.get_active_jobs(workspace_id)

        assert len(active) == 1
        assert active[0]["items_synced"] == 42

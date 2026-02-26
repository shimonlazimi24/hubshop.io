"""Tests for SyncJob model structure."""

import uuid

import pytest

from backend.db.models.platform import SyncJob, SyncJobStatus


@pytest.mark.unit
class TestSyncJobModel:
    def test_sync_job_has_required_fields(self) -> None:
        job = SyncJob(
            workspace_id=uuid.uuid4(),
            connected_account_id=uuid.uuid4(),
            platform="shop",
            sync_type="orders",
            status=SyncJobStatus.RUNNING,
        )
        assert job.workspace_id is not None
        assert job.platform == "shop"
        assert job.sync_type == "orders"
        assert job.status == SyncJobStatus.RUNNING
        assert job.items_synced == 0
        assert job.items_total is None
        assert job.error_message is None

    def test_sync_job_status_values(self) -> None:
        assert SyncJobStatus.PENDING.value == "pending"
        assert SyncJobStatus.RUNNING.value == "running"
        assert SyncJobStatus.COMPLETED.value == "completed"
        assert SyncJobStatus.FAILED.value == "failed"

    def test_sync_job_with_progress(self) -> None:
        job = SyncJob(
            workspace_id=uuid.uuid4(),
            connected_account_id=uuid.uuid4(),
            platform="shop",
            sync_type="products",
            status=SyncJobStatus.RUNNING,
            items_synced=50,
            items_total=200,
        )
        assert job.items_synced == 50
        assert job.items_total == 200

    def test_sync_job_with_error(self) -> None:
        job = SyncJob(
            workspace_id=uuid.uuid4(),
            connected_account_id=uuid.uuid4(),
            platform="marketing",
            sync_type="campaigns",
            status=SyncJobStatus.FAILED,
            error_message="API rate limited",
        )
        assert job.status == SyncJobStatus.FAILED
        assert job.error_message == "API rate limited"

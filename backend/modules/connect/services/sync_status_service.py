"""Service for tracking sync job progress."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.platform import SyncJob, SyncJobStatus


class SyncStatusService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_sync_job(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        platform: str,
        sync_type: str,
    ) -> SyncJob:
        job = SyncJob(
            workspace_id=workspace_id,
            connected_account_id=connected_account_id,
            platform=platform,
            sync_type=sync_type,
            status=SyncJobStatus.PENDING,
        )
        self._session.add(job)
        await self._session.flush()
        return job

    async def start_job(self, job_id: uuid.UUID) -> SyncJob | None:
        result = await self._session.execute(
            select(SyncJob).where(SyncJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            return None
        job.status = SyncJobStatus.RUNNING
        job.started_at = datetime.now(UTC)
        return job

    async def update_progress(
        self,
        job_id: uuid.UUID,
        items_synced: int,
        items_total: int | None = None,
    ) -> SyncJob | None:
        result = await self._session.execute(
            select(SyncJob).where(SyncJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            return None
        job.items_synced = items_synced
        if items_total is not None:
            job.items_total = items_total
        return job

    async def complete_job(self, job_id: uuid.UUID) -> SyncJob | None:
        result = await self._session.execute(
            select(SyncJob).where(SyncJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            return None
        job.status = SyncJobStatus.COMPLETED
        job.completed_at = datetime.now(UTC)
        return job

    async def fail_job(self, job_id: uuid.UUID, error: str) -> SyncJob | None:
        result = await self._session.execute(
            select(SyncJob).where(SyncJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            return None
        job.status = SyncJobStatus.FAILED
        job.error_message = error
        job.completed_at = datetime.now(UTC)
        return job

    async def list_recent_jobs(
        self, workspace_id: uuid.UUID, limit: int = 20
    ) -> list[dict]:
        result = await self._session.execute(
            select(SyncJob)
            .where(SyncJob.workspace_id == workspace_id)
            .order_by(SyncJob.created_at.desc())
            .limit(limit)
        )
        jobs = result.scalars().all()
        return [self._serialize(j) for j in jobs]

    async def get_active_jobs(self, workspace_id: uuid.UUID) -> list[dict]:
        result = await self._session.execute(
            select(SyncJob)
            .where(SyncJob.workspace_id == workspace_id)
            .where(SyncJob.status.in_([SyncJobStatus.PENDING, SyncJobStatus.RUNNING]))
            .order_by(SyncJob.created_at.desc())
        )
        jobs = result.scalars().all()
        return [self._serialize(j) for j in jobs]

    @staticmethod
    def _serialize(job: SyncJob) -> dict:
        return {
            "id": str(job.id),
            "platform": job.platform,
            "sync_type": job.sync_type,
            "status": job.status.value if hasattr(job.status, "value") else job.status,
            "items_synced": job.items_synced,
            "items_total": job.items_total,
            "error_message": job.error_message,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "created_at": job.created_at.isoformat() if job.created_at else None,
        }

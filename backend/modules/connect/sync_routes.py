"""API routes for sync status and manual sync triggers."""

from __future__ import annotations

import uuid
from typing import Literal

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from backend.db.models.platform import ConnectedAccount, Platform
from backend.dependencies import CurrentUser, DBSession
from backend.modules.connect.services.sync_status_service import SyncStatusService

router = APIRouter(prefix="/connect/sync", tags=["connect-sync"])


async def _get_connected_account(
    db: DBSession, workspace_id: uuid.UUID, platform: str
) -> ConnectedAccount | None:
    platform_enum = Platform(platform)
    result = await db.execute(
        select(ConnectedAccount)
        .where(ConnectedAccount.workspace_id == workspace_id)
        .where(ConnectedAccount.platform == platform_enum)
    )
    return result.scalar_one_or_none()


@router.get("/jobs")
async def list_sync_jobs(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    limit: int = 20,
) -> list[dict]:
    service = SyncStatusService(db)
    return await service.list_recent_jobs(workspace_id, limit=limit)


@router.get("/active")
async def get_active_sync_jobs(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = SyncStatusService(db)
    return await service.get_active_jobs(workspace_id)


@router.post("/trigger")
async def trigger_manual_sync(
    workspace_id: uuid.UUID,
    platform: Literal["shop", "developer", "marketing"],
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    account = await _get_connected_account(db, workspace_id, platform)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No connected {platform} account found",
        )

    service = SyncStatusService(db)
    sync_types = _get_sync_types(platform)
    job_ids = []
    for sync_type in sync_types:
        job = await service.create_sync_job(
            workspace_id=workspace_id,
            connected_account_id=account.id,
            platform=platform,
            sync_type=sync_type,
        )
        job_ids.append(str(job.id))

    return {"status": "triggered", "job_ids": job_ids}


def _get_sync_types(platform: str) -> list[str]:
    if platform == "shop":
        return ["orders", "products"]
    elif platform == "marketing":
        return ["campaigns", "ad_groups", "ads"]
    elif platform == "developer":
        return ["videos"]
    return []

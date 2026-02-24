"""Routes for competitor tracking endpoints."""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.intelligence.services.competitor_service import CompetitorService

router = APIRouter()


class AddCompetitorRequest(BaseModel):
    tiktok_username: str


class CompareCompetitorsRequest(BaseModel):
    competitor_ids: list[uuid.UUID]


@router.post("/competitors")
async def add_competitor(
    workspace_id: uuid.UUID,
    body: AddCompetitorRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict[str, Any]:
    """Add a competitor to track."""
    # Research client is injected via sync tasks in production;
    # for the route we create a lightweight stub that the caller
    # can override or mock in tests.
    import os

    from backend.tiktok.research.client import TikTokResearchClient

    client = TikTokResearchClient(
        client_key=os.environ.get("TIKTOK_DEVELOPER_CLIENT_KEY", ""),
        client_secret=os.environ.get("TIKTOK_DEVELOPER_CLIENT_SECRET", ""),
    )
    try:
        service = CompetitorService(db)
        return await service.add_competitor(workspace_id, body.tiktok_username, client)
    finally:
        await client.close()


@router.delete("/competitors/{competitor_id}")
async def remove_competitor(
    competitor_id: uuid.UUID,
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict[str, str]:
    """Remove a tracked competitor."""
    service = CompetitorService(db)
    deleted = await service.remove_competitor(workspace_id, competitor_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found",
        )
    return {"status": "deleted"}


@router.get("/competitors")
async def list_competitors(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict[str, Any]]:
    """List all tracked competitors for the workspace."""
    service = CompetitorService(db)
    return await service.list_competitors(workspace_id)


@router.get("/competitors/{competitor_id}")
async def get_competitor_detail(
    competitor_id: uuid.UUID,
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict[str, Any]:
    """Get competitor details with latest content."""
    service = CompetitorService(db)
    detail = await service.get_competitor_detail(workspace_id, competitor_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found",
        )
    return detail


@router.post("/competitors/compare")
async def compare_competitors(
    workspace_id: uuid.UUID,
    body: CompareCompetitorsRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict[str, Any]]:
    """Compare metrics across multiple competitors."""
    service = CompetitorService(db)
    return await service.compare_competitors(workspace_id, body.competitor_ids)

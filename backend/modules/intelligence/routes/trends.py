"""Routes for trend analysis endpoints."""

import uuid
from typing import Any

from fastapi import APIRouter

from backend.dependencies import CurrentUser, DBSession
from backend.modules.intelligence.services.trend_service import TrendService

router = APIRouter()


@router.get("/trends/hashtags")
async def get_trending_hashtags(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Return latest trending hashtags for the workspace."""
    service = TrendService(db)
    return await service.get_trending_hashtags(workspace_id, limit=limit)


@router.get("/trends/sounds")
async def get_trending_sounds(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Return latest trending sounds for the workspace."""
    service = TrendService(db)
    return await service.get_trending_sounds(workspace_id, limit=limit)


@router.get("/trends/history/{hashtag}")
async def get_trend_history(
    hashtag: str,
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    days: int = 30,
) -> list[dict[str, Any]]:
    """Return time-series engagement data for a specific hashtag."""
    service = TrendService(db)
    return await service.get_trend_history(workspace_id, hashtag, days=days)

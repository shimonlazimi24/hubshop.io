"""Routes for creator insight endpoints."""

import os
import uuid
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.intelligence.services.creator_insight_service import (
    CreatorInsightService,
)

router = APIRouter()


class DiscoverCreatorsRequest(BaseModel):
    keyword: str | None = None
    hashtag: str | None = None
    min_followers: int = 0
    max_count: int = 50


@router.post("/creators/discover")
async def discover_creators(
    workspace_id: uuid.UUID,
    body: DiscoverCreatorsRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict[str, Any]]:
    """Discover creators matching the given filters."""
    from backend.tiktok.research.client import TikTokResearchClient

    client = TikTokResearchClient(
        client_key=os.environ.get("TIKTOK_DEVELOPER_CLIENT_KEY", ""),
        client_secret=os.environ.get("TIKTOK_DEVELOPER_CLIENT_SECRET", ""),
    )
    try:
        service = CreatorInsightService(db)
        return await service.discover_creators(
            workspace_id,
            client,
            keyword=body.keyword,
            hashtag=body.hashtag,
            min_followers=body.min_followers,
            max_count=body.max_count,
        )
    finally:
        await client.close()


@router.get("/creators/{creator_username}")
async def get_creator_insight(
    creator_username: str,
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict[str, Any]:
    """Get detailed insight for a specific creator."""
    from backend.tiktok.research.client import TikTokResearchClient

    client = TikTokResearchClient(
        client_key=os.environ.get("TIKTOK_DEVELOPER_CLIENT_KEY", ""),
        client_secret=os.environ.get("TIKTOK_DEVELOPER_CLIENT_SECRET", ""),
    )
    try:
        service = CreatorInsightService(db)
        return await service.get_creator_insight(workspace_id, creator_username, client)
    finally:
        await client.close()

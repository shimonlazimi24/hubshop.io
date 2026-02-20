import uuid

from fastapi import APIRouter

from backend.dependencies import CurrentUser, DBSession
from backend.modules.creators.schemas import SearchCreatorsRequest
from backend.modules.creators.services.creator_discovery_service import (
    CreatorDiscoveryService,
)

router = APIRouter()


@router.post("/discover")
async def search_creators(
    workspace_id: uuid.UUID,
    body: SearchCreatorsRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = CreatorDiscoveryService(db)
    results = await service.search_creators(
        workspace_id,
        query=body.query,
        min_followers=body.min_followers,
        max_followers=body.max_followers,
        categories=body.categories,
    )
    return {"creators": results}


@router.get("/discover/{creator_username}")
async def get_creator_info(
    workspace_id: uuid.UUID,
    creator_username: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = CreatorDiscoveryService(db)
    info = await service.get_creator_info(workspace_id, creator_username)
    return {"creator": info}


@router.get("/discover/{creator_username}/audience")
async def get_creator_audience(
    workspace_id: uuid.UUID,
    creator_username: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = CreatorDiscoveryService(db)
    audience = await service.get_creator_audience(workspace_id, creator_username)
    return {"audience": audience}

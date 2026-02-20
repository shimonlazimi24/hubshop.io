import uuid

from fastapi import APIRouter, Query
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.organic.services.account_service import OrganicAccountService

router = APIRouter()


class PublishVideoRequest(BaseModel):
    connected_account_id: uuid.UUID
    video_config: dict


class PublishPhotoRequest(BaseModel):
    connected_account_id: uuid.UUID
    photo_config: dict


@router.get("/accounts/profile")
async def get_profile(
    workspace_id: uuid.UUID,
    connected_account_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = OrganicAccountService(db)
    return await service.get_profile(workspace_id, connected_account_id)


@router.get("/accounts/posts")
async def get_posts(
    workspace_id: uuid.UUID,
    connected_account_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    service = OrganicAccountService(db)
    return await service.get_posts(
        workspace_id, connected_account_id, page=page, page_size=page_size
    )


@router.get("/accounts/benchmarks")
async def get_benchmarks(
    workspace_id: uuid.UUID,
    connected_account_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    category: str | None = Query(None),
) -> dict:
    service = OrganicAccountService(db)
    return await service.get_benchmarks(
        workspace_id, connected_account_id, category=category
    )


@router.post("/accounts/posts/video/publish")
async def publish_video(
    workspace_id: uuid.UUID,
    body: PublishVideoRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = OrganicAccountService(db)
    return await service.publish_video(
        workspace_id,
        body.connected_account_id,
        video_config=body.video_config,
    )


@router.post("/accounts/posts/photo/publish")
async def publish_photo(
    workspace_id: uuid.UUID,
    body: PublishPhotoRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = OrganicAccountService(db)
    return await service.publish_photo(
        workspace_id,
        body.connected_account_id,
        photo_config=body.photo_config,
    )


@router.get("/accounts/posts/status")
async def get_publish_status(
    workspace_id: uuid.UUID,
    connected_account_id: uuid.UUID,
    publish_id: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = OrganicAccountService(db)
    return await service.get_publish_status(
        workspace_id, connected_account_id, publish_id=publish_id
    )


@router.get("/accounts/posts/hashtags/recommend")
async def recommend_hashtags(
    workspace_id: uuid.UUID,
    connected_account_id: uuid.UUID,
    text: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = OrganicAccountService(db)
    return await service.recommend_hashtags(
        workspace_id, connected_account_id, text=text
    )

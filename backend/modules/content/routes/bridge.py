import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.content.services.content_creator_bridge import (
    ContentCreatorBridge,
)
from backend.modules.creators.schemas import ContentAuthorizationResponse

router = APIRouter()


@router.get("/videos/{video_id}/creator")
async def get_video_with_creator(
    video_id: uuid.UUID,
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = ContentCreatorBridge(db)
    result = await service.get_video_with_creator(video_id, workspace_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    return result


@router.post(
    "/videos/{video_id}/spark-ad-request",
    response_model=ContentAuthorizationResponse,
    status_code=201,
)
async def request_spark_ad_for_video(
    video_id: uuid.UUID,
    workspace_id: uuid.UUID,
    creator_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> ContentAuthorizationResponse:
    service = ContentCreatorBridge(db)
    try:
        auth = await service.request_spark_ad_for_video(
            workspace_id, video_id, creator_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    return ContentAuthorizationResponse.model_validate(auth)


@router.get("/creators/{creator_id}/content-summary")
async def get_creator_content_summary(
    creator_id: uuid.UUID,
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = ContentCreatorBridge(db)
    result = await service.get_creator_content_summary(workspace_id, creator_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator not found",
        )
    return result

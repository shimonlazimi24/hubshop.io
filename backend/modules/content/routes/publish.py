import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import PaginatedResponse
from backend.modules.content.schemas import (
    ContentPublishJobResponse,
    PublishPhotoRequest,
    PublishVideoRequest,
)
from backend.modules.content.services.publish_service import PublishService

router = APIRouter()


@router.post(
    "/publish",
    response_model=ContentPublishJobResponse,
)
async def publish_video(
    workspace_id: uuid.UUID,
    body: PublishVideoRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> ContentPublishJobResponse:
    service = PublishService(db)
    job = await service.create_publish_job(
        workspace_id,
        video_url=body.video_url,
        title=body.title,
        privacy_level=body.privacy_level,
        disable_duet=body.disable_duet,
        disable_comment=body.disable_comment,
        disable_stitch=body.disable_stitch,
        brand_content_toggle=body.brand_content_toggle,
        brand_organic_toggle=body.brand_organic_toggle,
    )
    return ContentPublishJobResponse.model_validate(job)


@router.post(
    "/publish/photo",
    response_model=ContentPublishJobResponse,
)
async def publish_photo(
    workspace_id: uuid.UUID,
    body: PublishPhotoRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> ContentPublishJobResponse:
    service = PublishService(db)
    job = await service.create_photo_publish_job(
        workspace_id,
        photo_urls=body.photo_urls,
        title=body.title,
        description=body.description,
        privacy_level=body.privacy_level,
        disable_comment=body.disable_comment,
        auto_add_music=body.auto_add_music,
        photo_cover_index=body.photo_cover_index,
    )
    return ContentPublishJobResponse.model_validate(job)


@router.get(
    "/publish/jobs",
    response_model=PaginatedResponse[ContentPublishJobResponse],
)
async def list_publish_jobs(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    status_filter: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[ContentPublishJobResponse]:
    service = PublishService(db)
    result = await service.list_publish_jobs(
        workspace_id,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[ContentPublishJobResponse.model_validate(j) for j in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.get(
    "/publish/{publish_id}/status",
    response_model=ContentPublishJobResponse,
)
async def get_publish_status(
    publish_id: str,
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> ContentPublishJobResponse:
    service = PublishService(db)
    job = await service.check_and_update_publish_status(workspace_id, publish_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publish job not found",
        )
    return ContentPublishJobResponse.model_validate(job)

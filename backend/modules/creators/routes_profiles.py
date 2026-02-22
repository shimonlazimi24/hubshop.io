import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import PaginatedResponse
from backend.modules.creators.schemas import (
    CreatorDetailResponse,
    CreatorProfileResponse,
)
from backend.modules.creators.services.creator_profile_service import (
    CreatorProfileService,
)

router = APIRouter()


@router.get(
    "/profiles",
    response_model=PaginatedResponse[CreatorProfileResponse],
)
async def list_profiles(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    is_saved: bool | None = None,
    tier: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[CreatorProfileResponse]:
    service = CreatorProfileService(db)
    result = await service.list_creators(
        workspace_id,
        is_saved=is_saved,
        tier=tier,
        search=search,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[CreatorProfileResponse.model_validate(c) for c in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.get(
    "/profiles/{creator_id}",
    response_model=CreatorDetailResponse,
)
async def get_profile(
    creator_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> CreatorDetailResponse:
    service = CreatorProfileService(db)
    creator = await service.get_creator(creator_id)
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator not found",
        )
    return CreatorDetailResponse.model_validate(creator)


@router.post(
    "/profiles/{creator_id}/save",
    response_model=CreatorProfileResponse,
)
async def toggle_save_creator(
    creator_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    is_saved: bool = True,
) -> CreatorProfileResponse:
    service = CreatorProfileService(db)
    creator = await service.save_creator(creator_id, is_saved)
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator not found",
        )
    return CreatorProfileResponse.model_validate(creator)


@router.post(
    "/profiles/{creator_id}/sync-metrics",
    response_model=CreatorDetailResponse,
)
async def sync_creator_metrics(
    creator_id: uuid.UUID,
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> CreatorDetailResponse:
    from backend.modules.creators.services.creator_service import CreatorService

    profile_service = CreatorProfileService(db)
    creator = await profile_service.get_creator(creator_id)
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator not found",
        )
    service = CreatorService(db)
    updated = await service.sync_creator_metrics(creator, workspace_id)
    return CreatorDetailResponse.model_validate(updated)


@router.get("/profiles/{creator_id}/videos")
async def get_creator_videos(
    creator_id: uuid.UUID,
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    from backend.modules.creators.services.creator_service import CreatorService

    profile_service = CreatorProfileService(db)
    creator = await profile_service.get_creator(creator_id)
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator not found",
        )
    service = CreatorService(db)
    videos = await service.get_creator_videos(workspace_id, creator)
    return {"videos": videos}

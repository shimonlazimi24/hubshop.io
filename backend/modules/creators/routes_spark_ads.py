import uuid

from fastapi import APIRouter

from backend.dependencies import CurrentUser, DBSession
from backend.modules.creators.schemas import (
    ContentAuthorizationResponse,
    RequestAuthorizationRequest,
)
from backend.modules.creators.services.spark_ads_service import SparkAdsService

router = APIRouter()


@router.post(
    "/spark-ads/authorize",
    response_model=ContentAuthorizationResponse,
    status_code=201,
)
async def request_authorization(
    workspace_id: uuid.UUID,
    body: RequestAuthorizationRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> ContentAuthorizationResponse:
    service = SparkAdsService(db)
    auth = await service.request_authorization(
        workspace_id,
        creator_id=uuid.UUID(body.creator_id),
        platform_video_id=body.platform_video_id,
    )
    return ContentAuthorizationResponse.model_validate(auth)


@router.get(
    "/spark-ads/authorizations",
    response_model=list[ContentAuthorizationResponse],
)
async def list_authorizations(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    creator_id: uuid.UUID | None = None,
    status_filter: str | None = None,
) -> list[ContentAuthorizationResponse]:
    service = SparkAdsService(db)
    authorizations = await service.list_authorizations(
        workspace_id,
        creator_id=creator_id,
        status_filter=status_filter,
    )
    return [
        ContentAuthorizationResponse.model_validate(a) for a in authorizations
    ]

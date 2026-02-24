import uuid

from fastapi import APIRouter, HTTPException, status

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
    return [ContentAuthorizationResponse.model_validate(a) for a in authorizations]


@router.post(
    "/spark-ads/authorizations/{auth_id}/check",
    response_model=ContentAuthorizationResponse,
)
async def check_authorization_status(
    auth_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> ContentAuthorizationResponse:
    service = SparkAdsService(db)
    auth = await service.check_authorization_status(auth_id)
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authorization not found",
        )
    return ContentAuthorizationResponse.model_validate(auth)


@router.post(
    "/spark-ads/authorizations/{auth_id}/cancel",
    response_model=ContentAuthorizationResponse,
)
async def cancel_authorization(
    auth_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> ContentAuthorizationResponse:
    service = SparkAdsService(db)
    auth = await service.cancel_authorization(auth_id)
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authorization not found",
        )
    return ContentAuthorizationResponse.model_validate(auth)


@router.get("/spark-ads/authorizations/{auth_id}/code")
async def get_authorization_code(
    auth_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = SparkAdsService(db)
    code = await service.get_authorization_code(auth_id)
    return {"authorization_code": code}


@router.get(
    "/spark-ads/authorized-videos",
    response_model=list[ContentAuthorizationResponse],
)
async def list_authorized_videos(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[ContentAuthorizationResponse]:
    service = SparkAdsService(db)
    auths = await service.list_authorized_videos(workspace_id)
    return [ContentAuthorizationResponse.model_validate(a) for a in auths]

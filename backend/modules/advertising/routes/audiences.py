import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.schemas import (
    AudienceResponse,
    CreateCustomAudienceRequest,
    CreateLookalikeAudienceRequest,
)
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.audience_service import AudienceService
from backend.modules.commerce.schemas import PaginatedResponse

router = APIRouter()


@router.get(
    "/audiences",
    response_model=PaginatedResponse[AudienceResponse],
)
async def list_audiences(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    ad_account_id: uuid.UUID | None = None,
    audience_type: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[AudienceResponse]:
    service = AudienceService(db)
    result = await service.list_audiences(
        workspace_id,
        ad_account_id=ad_account_id,
        audience_type=audience_type,
        search=search,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[AudienceResponse.model_validate(a) for a in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.post("/audiences/custom", response_model=AudienceResponse)
async def create_custom_audience(
    workspace_id: uuid.UUID,
    body: CreateCustomAudienceRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> AudienceResponse:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = AudienceService(db)
    audience = await service.create_custom_audience(
        workspace_id, ad_account, name=body.name, file_paths=body.file_paths
    )
    return AudienceResponse.model_validate(audience)


@router.post("/audiences/lookalike", response_model=AudienceResponse)
async def create_lookalike_audience(
    workspace_id: uuid.UUID,
    body: CreateLookalikeAudienceRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> AudienceResponse:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = AudienceService(db)
    audience = await service.create_lookalike_audience(
        workspace_id,
        ad_account,
        name=body.name,
        source_audience_id=body.source_audience_id,
        lookalike_ratio=body.lookalike_ratio,
    )
    return AudienceResponse.model_validate(audience)


@router.delete("/audiences/{audience_id}")
async def delete_audience(
    audience_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = AudienceService(db)
    audience = await service.get_audience(audience_id)
    if not audience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Audience not found"
        )

    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account(audience.ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    await service.delete_audience(audience, ad_account)
    return {"deleted": True}


@router.post("/audiences/sync")
async def sync_audiences(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    ad_account_id: uuid.UUID | None = None,
) -> dict:
    account_service = AdAccountService(db)
    if ad_account_id:
        ad_account = await account_service.get_ad_account(ad_account_id)
        if not ad_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
            )
        accounts = [ad_account]
    else:
        accounts = await account_service.list_ad_accounts(workspace_id)

    service = AudienceService(db)
    total_synced = 0
    for account in accounts:
        count = await service.sync_audiences(account)
        total_synced += count

    return {"synced": total_synced}


class ShareAudienceRequest(BaseModel):
    target_advertiser_ids: list[str]


class AudienceOverlapRequest(BaseModel):
    audience_ids: list[uuid.UUID]


class UploadAudienceFileRequest(BaseModel):
    file_data: list[str]
    hash_type: str = "SHA256"


class CreateRuleAudienceRequest(BaseModel):
    ad_account_id: str
    name: str
    rules: list[dict]


@router.post("/audiences/{audience_id}/share")
async def share_audience(
    workspace_id: uuid.UUID,
    audience_id: uuid.UUID,
    body: ShareAudienceRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = AudienceService(db)
    try:
        return await service.share_audience(
            workspace_id, audience_id, body.target_advertiser_ids
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.post("/audiences/overlap")
async def get_audience_overlap(
    workspace_id: uuid.UUID,
    body: AudienceOverlapRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = AudienceService(db)
    try:
        return await service.get_audience_overlap(workspace_id, body.audience_ids)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@router.post("/audiences/{audience_id}/upload")
async def upload_audience_file(
    workspace_id: uuid.UUID,
    audience_id: uuid.UUID,
    body: UploadAudienceFileRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = AudienceService(db)
    try:
        return await service.upload_audience_file(
            workspace_id, audience_id, body.file_data, body.hash_type
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.post("/audiences/rule", response_model=AudienceResponse)
async def create_rule_audience(
    workspace_id: uuid.UUID,
    body: CreateRuleAudienceRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> AudienceResponse:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ad account not found"
        )

    service = AudienceService(db)
    audience = await service.create_rule_audience(
        workspace_id, ad_account, name=body.name, rules=body.rules
    )
    return AudienceResponse.model_validate(audience)

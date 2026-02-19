import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.schemas import (
    AdDetailResponse,
    AdSummaryResponse,
    CreateAdRequest,
    StatusUpdateRequest,
    UpdateAdRequest,
)
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.ad_group_service import AdGroupService
from backend.modules.advertising.services.ad_service import AdService
from backend.modules.commerce.schemas import PaginatedResponse

router = APIRouter()


@router.get(
    "/creatives",
    response_model=PaginatedResponse[AdSummaryResponse],
)
async def list_ads(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    adgroup_id: uuid.UUID | None = None,
    ad_account_id: uuid.UUID | None = None,
    status_filter: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[AdSummaryResponse]:
    service = AdService(db)
    result = await service.list_ads(
        workspace_id,
        adgroup_id=adgroup_id,
        ad_account_id=ad_account_id,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[AdSummaryResponse.model_validate(a) for a in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.get(
    "/creatives/{ad_id}",
    response_model=AdDetailResponse,
)
async def get_ad(
    ad_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> AdDetailResponse:
    service = AdService(db)
    ad = await service.get_ad(ad_id)
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found",
        )
    return AdDetailResponse.model_validate(ad)


@router.post("/creatives", response_model=AdDetailResponse)
async def create_ad(
    workspace_id: uuid.UUID,
    body: CreateAdRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> AdDetailResponse:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    adgroup_service = AdGroupService(db)
    ad_group = await adgroup_service.get_ad_group(uuid.UUID(body.adgroup_id))
    if not ad_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad group not found",
        )

    service = AdService(db)
    ad = await service.create_ad(
        workspace_id,
        ad_account,
        ad_group,
        ad_name=body.ad_name,
        ad_format=body.ad_format,
        ad_text=body.ad_text,
        call_to_action=body.call_to_action,
        landing_page_url=body.landing_page_url,
    )
    return AdDetailResponse.model_validate(ad)


@router.put(
    "/creatives/{ad_id}",
    response_model=AdDetailResponse,
)
async def update_ad(
    ad_id: uuid.UUID,
    body: UpdateAdRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> AdDetailResponse:
    service = AdService(db)
    ad = await service.get_ad(ad_id)
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found",
        )

    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account(ad.ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    updated = await service.update_ad(
        ad,
        ad_account,
        ad_name=body.ad_name,
        ad_text=body.ad_text,
        call_to_action=body.call_to_action,
        landing_page_url=body.landing_page_url,
    )
    return AdDetailResponse.model_validate(updated)


@router.post(
    "/creatives/{ad_id}/status",
    response_model=AdDetailResponse,
)
async def update_ad_status(
    ad_id: uuid.UUID,
    body: StatusUpdateRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> AdDetailResponse:
    service = AdService(db)
    ad = await service.get_ad(ad_id)
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found",
        )

    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account(ad.ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    updated = await service.update_ad_status(
        ad, ad_account, operation_status=body.operation_status
    )
    return AdDetailResponse.model_validate(updated)


@router.post("/creatives/sync")
async def sync_ads(
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ad account not found",
            )
        accounts = [ad_account]
    else:
        accounts = await account_service.list_ad_accounts(workspace_id)

    ad_service = AdService(db)
    total_synced = 0
    for account in accounts:
        count = await ad_service.sync_ads(account)
        total_synced += count

    return {"synced": total_synced}

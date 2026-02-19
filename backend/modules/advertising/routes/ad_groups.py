import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.schemas import (
    AdGroupDetailResponse,
    AdGroupSummaryResponse,
    CreateAdGroupRequest,
    StatusUpdateRequest,
    UpdateAdGroupRequest,
)
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.ad_group_service import AdGroupService
from backend.modules.advertising.services.campaign_service import CampaignService
from backend.modules.commerce.schemas import PaginatedResponse

router = APIRouter()


@router.get(
    "/ad-groups",
    response_model=PaginatedResponse[AdGroupSummaryResponse],
)
async def list_ad_groups(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    campaign_id: uuid.UUID | None = None,
    ad_account_id: uuid.UUID | None = None,
    status_filter: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[AdGroupSummaryResponse]:
    service = AdGroupService(db)
    result = await service.list_ad_groups(
        workspace_id,
        campaign_id=campaign_id,
        ad_account_id=ad_account_id,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[AdGroupSummaryResponse.model_validate(ag) for ag in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.get(
    "/ad-groups/{adgroup_id}",
    response_model=AdGroupDetailResponse,
)
async def get_ad_group(
    adgroup_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> AdGroupDetailResponse:
    service = AdGroupService(db)
    ad_group = await service.get_ad_group(adgroup_id)
    if not ad_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad group not found",
        )
    return AdGroupDetailResponse.model_validate(ad_group)


@router.post("/ad-groups", response_model=AdGroupDetailResponse)
async def create_ad_group(
    workspace_id: uuid.UUID,
    body: CreateAdGroupRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> AdGroupDetailResponse:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    campaign_service = CampaignService(db)
    campaign = await campaign_service.get_campaign(uuid.UUID(body.campaign_id))
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    service = AdGroupService(db)
    ad_group = await service.create_ad_group(
        workspace_id,
        ad_account,
        campaign,
        adgroup_name=body.adgroup_name,
        placement_type=body.placement_type,
        bid_type=body.bid_type,
        bid_amount=body.bid_amount,
        budget=body.budget,
        optimization_goal=body.optimization_goal,
        targeting=body.targeting,
    )
    return AdGroupDetailResponse.model_validate(ad_group)


@router.put(
    "/ad-groups/{adgroup_id}",
    response_model=AdGroupDetailResponse,
)
async def update_ad_group(
    adgroup_id: uuid.UUID,
    body: UpdateAdGroupRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> AdGroupDetailResponse:
    service = AdGroupService(db)
    ad_group = await service.get_ad_group(adgroup_id)
    if not ad_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad group not found",
        )

    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account(ad_group.ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    updated = await service.update_ad_group(
        ad_group,
        ad_account,
        adgroup_name=body.adgroup_name,
        bid_type=body.bid_type,
        bid_amount=body.bid_amount,
        budget=body.budget,
        optimization_goal=body.optimization_goal,
        targeting=body.targeting,
    )
    return AdGroupDetailResponse.model_validate(updated)


@router.post(
    "/ad-groups/{adgroup_id}/status",
    response_model=AdGroupDetailResponse,
)
async def update_ad_group_status(
    adgroup_id: uuid.UUID,
    body: StatusUpdateRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> AdGroupDetailResponse:
    service = AdGroupService(db)
    ad_group = await service.get_ad_group(adgroup_id)
    if not ad_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad group not found",
        )

    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account(ad_group.ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    updated = await service.update_ad_group_status(
        ad_group, ad_account, operation_status=body.operation_status
    )
    return AdGroupDetailResponse.model_validate(updated)


@router.post("/ad-groups/sync")
async def sync_ad_groups(
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

    ad_group_service = AdGroupService(db)
    total_synced = 0
    for account in accounts:
        count = await ad_group_service.sync_ad_groups(account)
        total_synced += count

    return {"synced": total_synced}

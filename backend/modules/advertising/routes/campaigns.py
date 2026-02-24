import uuid
from typing import Literal

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.advertising.schemas import (
    CampaignDetailResponse,
    CampaignSummaryResponse,
    CreateCampaignRequest,
    StatusUpdateRequest,
    UpdateCampaignRequest,
)
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.modules.advertising.services.campaign_service import CampaignService
from backend.modules.advertising.services.unified_service import (
    UnifiedAdvertisingService,
)
from backend.modules.commerce.schemas import PaginatedResponse

router = APIRouter()


@router.get(
    "/campaigns",
    response_model=PaginatedResponse[CampaignSummaryResponse],
)
async def list_campaigns(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    ad_account_id: uuid.UUID | None = None,
    objective: str | None = None,
    status_filter: str | None = None,
    search: str | None = None,
    platform: Literal["marketing", "shop"] | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[CampaignSummaryResponse]:
    service = UnifiedAdvertisingService(db)
    return await service.list_campaigns(
        workspace_id,
        platform=platform,
        ad_account_id=ad_account_id,
        objective=objective,
        status_filter=status_filter,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/campaigns/{campaign_id}",
    response_model=CampaignDetailResponse,
)
async def get_campaign(
    campaign_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> CampaignDetailResponse:
    service = CampaignService(db)
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return CampaignDetailResponse.model_validate(campaign)


@router.post("/campaigns", response_model=CampaignDetailResponse)
async def create_campaign(
    workspace_id: uuid.UUID,
    body: CreateCampaignRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> CampaignDetailResponse:
    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account_by_advertiser_id(
        body.ad_account_id
    )
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    service = CampaignService(db)
    campaign = await service.create_campaign(
        workspace_id,
        ad_account,
        campaign_name=body.campaign_name,
        objective_type=body.objective_type,
        budget_mode=body.budget_mode,
        budget=body.budget,
    )
    return CampaignDetailResponse.model_validate(campaign)


@router.put(
    "/campaigns/{campaign_id}",
    response_model=CampaignDetailResponse,
)
async def update_campaign(
    campaign_id: uuid.UUID,
    body: UpdateCampaignRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> CampaignDetailResponse:
    service = CampaignService(db)
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account(campaign.ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    updated = await service.update_campaign(
        campaign,
        ad_account,
        campaign_name=body.campaign_name,
        budget_mode=body.budget_mode,
        budget=body.budget,
    )
    return CampaignDetailResponse.model_validate(updated)


@router.post(
    "/campaigns/{campaign_id}/status",
    response_model=CampaignDetailResponse,
)
async def update_campaign_status(
    campaign_id: uuid.UUID,
    body: StatusUpdateRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> CampaignDetailResponse:
    service = CampaignService(db)
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    account_service = AdAccountService(db)
    ad_account = await account_service.get_ad_account(campaign.ad_account_id)
    if not ad_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad account not found",
        )

    updated = await service.update_campaign_status(
        campaign, ad_account, operation_status=body.operation_status
    )
    return CampaignDetailResponse.model_validate(updated)


@router.post("/campaigns/sync")
async def sync_campaigns(
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

    campaign_service = CampaignService(db)
    total_synced = 0
    for account in accounts:
        count = await campaign_service.sync_campaigns(account)
        total_synced += count

    return {"synced": total_synced}

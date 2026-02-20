import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import PaginatedResponse
from backend.modules.creators.schemas import (
    CreateCreatorCampaignRequest,
    CreatorCampaignResponse,
    CreatorInvitationResponse,
    InviteCreatorRequest,
    UpdateCreatorCampaignRequest,
)
from backend.modules.creators.services.campaign_service import (
    CreatorCampaignService,
)

router = APIRouter()


@router.get(
    "/campaigns",
    response_model=PaginatedResponse[CreatorCampaignResponse],
)
async def list_campaigns(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    status_filter: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[CreatorCampaignResponse]:
    service = CreatorCampaignService(db)
    result = await service.list_campaigns(
        workspace_id,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[CreatorCampaignResponse.model_validate(c) for c in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.post(
    "/campaigns",
    response_model=CreatorCampaignResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_campaign(
    workspace_id: uuid.UUID,
    body: CreateCreatorCampaignRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> CreatorCampaignResponse:
    service = CreatorCampaignService(db)
    campaign = await service.create_campaign(
        workspace_id,
        name=body.name,
        description=body.description,
        budget=body.budget,
        start_date=body.start_date,
        end_date=body.end_date,
        target_categories=body.target_categories,
        requirements=body.requirements,
    )
    return CreatorCampaignResponse.model_validate(campaign)


@router.get(
    "/campaigns/{campaign_id}",
    response_model=CreatorCampaignResponse,
)
async def get_campaign(
    campaign_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> CreatorCampaignResponse:
    service = CreatorCampaignService(db)
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator campaign not found",
        )
    return CreatorCampaignResponse.model_validate(campaign)


@router.put(
    "/campaigns/{campaign_id}",
    response_model=CreatorCampaignResponse,
)
async def update_campaign(
    campaign_id: uuid.UUID,
    body: UpdateCreatorCampaignRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> CreatorCampaignResponse:
    service = CreatorCampaignService(db)
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator campaign not found",
        )
    updated = await service.update_campaign(
        campaign,
        name=body.name,
        description=body.description,
        status=body.status,
        budget=body.budget,
    )
    return CreatorCampaignResponse.model_validate(updated)


@router.post(
    "/campaigns/{campaign_id}/invite",
    response_model=CreatorInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def invite_creator(
    campaign_id: uuid.UUID,
    body: InviteCreatorRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> CreatorInvitationResponse:
    service = CreatorCampaignService(db)
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator campaign not found",
        )
    invitation = await service.invite_creator(
        campaign_id,
        uuid.UUID(body.creator_id),
        message=body.message,
        offered_amount=body.offered_amount,
    )
    return CreatorInvitationResponse.model_validate(invitation)


@router.get(
    "/campaigns/{campaign_id}/invitations",
    response_model=list[CreatorInvitationResponse],
)
async def list_invitations(
    campaign_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    status_filter: str | None = None,
) -> list[CreatorInvitationResponse]:
    service = CreatorCampaignService(db)
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator campaign not found",
        )
    invitations = await service.list_invitations(
        campaign_id,
        status_filter=status_filter,
    )
    return [CreatorInvitationResponse.model_validate(i) for i in invitations]

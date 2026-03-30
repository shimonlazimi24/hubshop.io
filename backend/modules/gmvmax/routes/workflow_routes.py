import uuid

from fastapi import APIRouter, HTTPException, Query, status

from backend.db.models.gmvmax import CampaignType, DraftStatus
from backend.dependencies import CurrentUser, DBSession, WorkspaceId
from backend.modules.gmvmax.schemas import (
    CreateDraftRequest,
    DeepLinkResponse,
    DraftResponse,
    LinkDraftRequest,
)
from backend.modules.gmvmax.services.workflow_service import GmvMaxWorkflowService

router = APIRouter()


@router.post(
    "/drafts", response_model=DraftResponse, status_code=status.HTTP_201_CREATED
)
async def create_draft(
    request: CreateDraftRequest,
    current_user: CurrentUser,
    db: DBSession,
    workspace_id: WorkspaceId,
) -> DraftResponse:
    service = GmvMaxWorkflowService(db)
    try:
        draft = await service.create_draft(
            workspace_id=workspace_id,
            user_id=current_user.id,
            request=request,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return DraftResponse.model_validate(draft)


@router.get("/drafts/{draft_id}", response_model=DraftResponse)
async def get_draft(
    draft_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> DraftResponse:
    service = GmvMaxWorkflowService(db)
    draft = await service.get_draft(draft_id)
    if draft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )
    return DraftResponse.model_validate(draft)


@router.get("/drafts", response_model=dict)
async def list_drafts(
    current_user: CurrentUser,
    db: DBSession,
    workspace_id: WorkspaceId,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
) -> dict:
    parsed_status: DraftStatus | None = None
    if status_filter is not None:
        try:
            parsed_status = DraftStatus(status_filter)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter: {status_filter}",
            ) from exc

    service = GmvMaxWorkflowService(db)
    result = await service.list_drafts(
        workspace_id=workspace_id,
        page=page,
        page_size=page_size,
        status_filter=parsed_status,
    )

    return {
        "items": [DraftResponse.model_validate(d) for d in result.items],
        "total": result.total,
        "page": result.page,
        "page_size": result.page_size,
        "total_pages": result.total_pages,
    }


@router.post("/drafts/{draft_id}/link", response_model=DraftResponse)
async def link_draft(
    draft_id: uuid.UUID,
    request: LinkDraftRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> DraftResponse:
    service = GmvMaxWorkflowService(db)
    draft = await service.link_draft(draft_id, request)
    if draft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found",
        )
    return DraftResponse.model_validate(draft)


@router.get("/deep-link/{campaign_type}", response_model=DeepLinkResponse)
async def get_deep_link(
    campaign_type: str,
    current_user: CurrentUser,
    db: DBSession,
) -> DeepLinkResponse:
    try:
        ct = CampaignType(campaign_type)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid campaign type: {campaign_type}",
        ) from exc

    service = GmvMaxWorkflowService(db)
    url = service.generate_deep_link(ct)
    return DeepLinkResponse(url=url, campaign_type=ct.value)

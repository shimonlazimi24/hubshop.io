import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import (
    PaginatedResponse,
    ReturnActionRequest,
    ReturnResponse,
)
from backend.modules.commerce.services.return_service import ReturnService

router = APIRouter()


@router.get(
    "/returns",
    response_model=PaginatedResponse[ReturnResponse],
)
async def list_returns(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[ReturnResponse]:
    service = ReturnService(db)
    result = await service.list_returns(
        workspace_id, page=page, page_size=page_size
    )
    return PaginatedResponse(
        items=[ReturnResponse.model_validate(r) for r in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.post(
    "/returns/{return_id}/approve",
    response_model=ReturnResponse,
)
async def approve_return(
    return_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    body: ReturnActionRequest | None = None,
) -> ReturnResponse:
    service = ReturnService(db)
    ret = await service.approve_return(
        return_id, reason=body.reason if body else None
    )
    if not ret:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Return request not found",
        )
    return ReturnResponse.model_validate(ret)


@router.post(
    "/returns/{return_id}/reject",
    response_model=ReturnResponse,
)
async def reject_return(
    return_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    body: ReturnActionRequest | None = None,
) -> ReturnResponse:
    service = ReturnService(db)
    ret = await service.reject_return(
        return_id, reason=body.reason if body else None
    )
    if not ret:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Return request not found",
        )
    return ReturnResponse.model_validate(ret)

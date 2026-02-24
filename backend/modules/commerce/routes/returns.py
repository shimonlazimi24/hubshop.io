import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import (
    CalculateRefundRequest,
    CreateReturnRequest,
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
    result = await service.list_returns(workspace_id, page=page, page_size=page_size)
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
    ret = await service.approve_return(return_id, reason=body.reason if body else None)
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
    ret = await service.reject_return(return_id, reason=body.reason if body else None)
    if not ret:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Return request not found",
        )
    return ReturnResponse.model_validate(ret)


@router.post("/returns", status_code=201)
async def create_return(
    body: CreateReturnRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = ReturnService(db)
    return await service.create_return(
        uuid.UUID(body.shop_id),
        body.order_id,
        body.return_type,
        body.reason,
    )


@router.get("/returns/search")
async def search_returns(
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = ReturnService(db)
    return await service.search_returns(shop_id)


@router.get("/returns/{return_id}/records")
async def get_return_records(
    return_id: str,
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = ReturnService(db)
    return await service.get_return_records(shop_id, return_id)


@router.get("/returns/reject-reasons")
async def get_reject_reasons(
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = ReturnService(db)
    return await service.get_reject_reasons(shop_id)


@router.post("/returns/refund/calculate")
async def calculate_refund(
    body: CalculateRefundRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = ReturnService(db)
    return await service.calculate_refund(
        uuid.UUID(body.shop_id), body.order_id, body.items
    )

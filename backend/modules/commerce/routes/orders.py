import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import (
    CancelOrderRequest,
    CancellationActionRequest,
    OrderDetailResponse,
    OrderSummaryResponse,
    OrderTimelineEventResponse,
    PaginatedResponse,
)
from backend.modules.commerce.services.fulfillment_service import FulfillmentService
from backend.modules.commerce.services.order_service import OrderService

router = APIRouter()


@router.get(
    "/orders",
    response_model=PaginatedResponse[OrderSummaryResponse],
)
async def list_orders(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    shop_id: uuid.UUID | None = None,
    status_filter: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[OrderSummaryResponse]:
    service = OrderService(db)
    result = await service.list_orders(
        workspace_id,
        shop_id=shop_id,
        status=status_filter,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[OrderSummaryResponse.model_validate(o) for o in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.get("/orders/cancellations")
async def search_cancellations(
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = OrderService(db)
    return await service.search_cancellations(shop_id)


@router.get(
    "/orders/{order_id}",
    response_model=OrderDetailResponse,
)
async def get_order(
    order_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> OrderDetailResponse:
    service = OrderService(db)
    order = await service.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return OrderDetailResponse.model_validate(order)


@router.get(
    "/orders/{order_id}/timeline",
    response_model=list[OrderTimelineEventResponse],
)
async def get_order_timeline(
    order_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[OrderTimelineEventResponse]:
    service = OrderService(db)
    events = await service.get_order_timeline(order_id)
    return [OrderTimelineEventResponse.model_validate(e) for e in events]


@router.get("/orders/{order_id}/tracking")
async def get_order_tracking(
    order_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    order_service = OrderService(db)
    order = await order_service.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    fulfillment_service = FulfillmentService(db)
    tracking = await fulfillment_service.get_tracking(order)
    return {"tracking": tracking}


@router.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    body: CancelOrderRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = OrderService(db)
    return await service.cancel_order(
        uuid.UUID(body.shop_id), order_id, body.cancel_reason
    )


@router.post("/orders/{order_id}/cancellation/approve")
async def approve_cancellation(
    order_id: str,
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = OrderService(db)
    return await service.approve_cancellation(shop_id, order_id)


@router.post("/orders/{order_id}/cancellation/reject")
async def reject_cancellation(
    order_id: str,
    body: CancellationActionRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = OrderService(db)
    return await service.reject_cancellation(
        uuid.UUID(body.shop_id), order_id, body.reject_reason or ""
    )


@router.get("/orders/{order_id}/price-detail")
async def get_price_detail(
    order_id: str,
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    service = OrderService(db)
    return await service.get_price_detail(shop_id, order_id)

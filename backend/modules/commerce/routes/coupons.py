import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import (
    CouponResponse,
    PaginatedResponse,
)
from backend.modules.commerce.services.coupon_service import CouponService
from backend.modules.commerce.services.shop_service import ShopService

router = APIRouter()


@router.get(
    "/coupons",
    response_model=PaginatedResponse[CouponResponse],
)
async def list_coupons(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    shop_id: uuid.UUID | None = None,
    status_filter: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[CouponResponse]:
    service = CouponService(db)
    result = await service.list_coupons(
        workspace_id,
        shop_id=shop_id,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[CouponResponse.model_validate(c) for c in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.post("/coupons/sync")
async def sync_coupons(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    shop_id: uuid.UUID | None = None,
) -> dict:
    shop_service = ShopService(db)
    if shop_id:
        shop = await shop_service.get_shop(shop_id)
        if not shop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found"
            )
        shops = [shop]
    else:
        shops = await shop_service.list_shops(workspace_id)

    service = CouponService(db)
    total_synced = 0
    for shop in shops:
        count = await service.sync_coupons(shop)
        total_synced += count

    return {"synced": total_synced}

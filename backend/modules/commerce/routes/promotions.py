import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import (
    CreateFlashDealRequest,
    CreatePromotionRequest,
    PaginatedResponse,
    PromotionResponse,
    UpdatePromotionRequest,
)
from backend.modules.commerce.services.promotion_service import PromotionService
from backend.modules.commerce.services.shop_service import ShopService

router = APIRouter()


@router.get(
    "/promotions",
    response_model=PaginatedResponse[PromotionResponse],
)
async def list_promotions(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    shop_id: uuid.UUID | None = None,
    status_filter: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[PromotionResponse]:
    service = PromotionService(db)
    result = await service.list_promotions(
        workspace_id,
        shop_id=shop_id,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[PromotionResponse.model_validate(p) for p in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.get("/promotions/{promotion_id}", response_model=PromotionResponse)
async def get_promotion(
    promotion_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> PromotionResponse:
    service = PromotionService(db)
    promotion = await service.get_promotion(promotion_id)
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found"
        )
    return PromotionResponse.model_validate(promotion)


@router.post("/promotions", response_model=PromotionResponse)
async def create_promotion(
    workspace_id: uuid.UUID,
    body: CreatePromotionRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> PromotionResponse:
    shop_service = ShopService(db)
    shop = await shop_service.get_shop(uuid.UUID(body.shop_id))
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found"
        )

    service = PromotionService(db)
    promotion = await service.create_promotion(
        workspace_id,
        shop,
        title=body.title,
        promotion_type=body.promotion_type,
        start_time=body.start_time,
        end_time=body.end_time,
        discount_type=body.discount_type,
        discount_value=body.discount_value,
        product_ids=body.product_ids,
    )
    return PromotionResponse.model_validate(promotion)


@router.post("/promotions/flash-deal", response_model=PromotionResponse)
async def create_flash_deal(
    workspace_id: uuid.UUID,
    body: CreateFlashDealRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> PromotionResponse:
    shop_service = ShopService(db)
    shop = await shop_service.get_shop(uuid.UUID(body.shop_id))
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found"
        )

    service = PromotionService(db)
    promotion = await service.create_flash_deal(
        workspace_id,
        shop,
        title=body.title,
        product_ids=body.product_ids,
        countdown_duration_hours=body.countdown_duration_hours,
        price_rules=body.price_rules,
        max_quantity=body.max_quantity,
        start_time=body.start_time,
        end_time=body.end_time,
    )
    return PromotionResponse.model_validate(promotion)


@router.put("/promotions/{promotion_id}", response_model=PromotionResponse)
async def update_promotion(
    promotion_id: uuid.UUID,
    body: UpdatePromotionRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> PromotionResponse:
    service = PromotionService(db)
    promotion = await service.get_promotion(promotion_id)
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found"
        )

    shop_service = ShopService(db)
    shop = await shop_service.get_shop(promotion.shop_id)
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found"
        )

    updated = await service.update_promotion(
        promotion, shop, title=body.title, discount_value=body.discount_value
    )
    return PromotionResponse.model_validate(updated)


@router.post("/promotions/{promotion_id}/deactivate", response_model=PromotionResponse)
async def deactivate_promotion(
    promotion_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> PromotionResponse:
    service = PromotionService(db)
    promotion = await service.get_promotion(promotion_id)
    if not promotion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found"
        )

    shop_service = ShopService(db)
    shop = await shop_service.get_shop(promotion.shop_id)
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found"
        )

    updated = await service.deactivate_promotion(promotion, shop)
    return PromotionResponse.model_validate(updated)


@router.post("/promotions/sync")
async def sync_promotions(
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

    service = PromotionService(db)
    total_synced = 0
    for shop in shops:
        count = await service.sync_promotions(shop)
        total_synced += count

    return {"synced": total_synced}

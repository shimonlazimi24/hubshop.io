import uuid

from fastapi import APIRouter

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.services.seller_service import SellerService

router = APIRouter()


@router.get("/seller/shops")
async def get_active_shops(
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = SellerService(db)
    return await service.get_active_shops(shop_id)


@router.get("/seller/permissions")
async def get_seller_permissions(
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = SellerService(db)
    return await service.get_seller_permissions(shop_id)

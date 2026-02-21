import uuid

from fastapi import APIRouter

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.services.logistics_service import LogisticsService

router = APIRouter()


@router.get("/logistics/warehouses")
async def get_warehouses(
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = LogisticsService(db)
    return await service.get_warehouses(shop_id)


@router.get("/logistics/warehouses/{warehouse_id}/delivery-options")
async def get_delivery_options(
    warehouse_id: str,
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = LogisticsService(db)
    return await service.get_delivery_options(shop_id, warehouse_id)


@router.get("/logistics/shipping-providers")
async def get_shipping_providers(
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = LogisticsService(db)
    return await service.get_shipping_providers(shop_id)


@router.get("/logistics/shipping-templates")
async def get_shipping_templates(
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    service = LogisticsService(db)
    return await service.get_shipping_templates(shop_id)

import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import ShopResponse
from backend.modules.commerce.services.shop_service import ShopService

router = APIRouter()


@router.get("/shops", response_model=list[ShopResponse])
async def list_shops(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[ShopResponse]:
    service = ShopService(db)
    shops = await service.list_shops(workspace_id)
    return [ShopResponse.model_validate(s) for s in shops]


@router.get("/shops/{shop_id}", response_model=ShopResponse)
async def get_shop(
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> ShopResponse:
    service = ShopService(db)
    shop = await service.get_shop(shop_id)
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found"
        )
    return ShopResponse.model_validate(shop)


@router.post("/shops/sync", response_model=list[ShopResponse])
async def sync_shops(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[ShopResponse]:
    service = ShopService(db)
    shops = await service.sync_shops_from_connected_accounts(workspace_id)
    return [ShopResponse.model_validate(s) for s in shops]

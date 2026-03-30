import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.services.shop_service import ShopService
from backend.modules.customer_engagement.schemas import (
    CreateEngagementTaskRequest,
    CustomEngagementTaskRequest,
)
from backend.modules.customer_engagement.services.engagement_service import (
    EngagementService,
)

router = APIRouter()


async def _get_shop(db, shop_id: uuid.UUID):  # type: ignore[no-untyped-def]
    shop_service = ShopService(db)
    shop = await shop_service.get_shop(shop_id)
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found"
        )
    return shop


@router.get("/templates")
async def get_templates(
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    shop = await _get_shop(db, shop_id)
    service = EngagementService(db)
    return await service.get_templates(shop)


@router.post("/tasks")
async def create_task(
    body: CreateEngagementTaskRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    shop = await _get_shop(db, uuid.UUID(body.shop_id))
    service = EngagementService(db)
    return await service.create_task(
        shop,
        task_data={"template_id": body.template_id, "audience": body.audience},
    )


@router.post("/tasks/custom")
async def create_custom_task(
    body: CustomEngagementTaskRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    shop = await _get_shop(db, uuid.UUID(body.shop_id))
    service = EngagementService(db)
    return await service.create_custom_task(
        shop,
        task_data={"message": body.message, "audience_ids": body.audience_ids},
    )


@router.get("/tasks/{task_id}/performance")
async def get_task_performance(
    task_id: str,
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    shop = await _get_shop(db, shop_id)
    service = EngagementService(db)
    return await service.get_task_performance(shop, task_id=task_id)


@router.get("/permissions")
async def get_permissions(
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    shop = await _get_shop(db, shop_id)
    service = EngagementService(db)
    return await service.get_permissions(shop)

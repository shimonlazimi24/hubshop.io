import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import SendMessageRequest
from backend.modules.commerce.services.customer_service import CustomerServiceService
from backend.modules.commerce.services.shop_service import ShopService

router = APIRouter()


async def _get_shop(db, shop_id: uuid.UUID):  # type: ignore[no-untyped-def]
    shop_service = ShopService(db)
    shop = await shop_service.get_shop(shop_id)
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found"
        )
    return shop


@router.get("/conversations")
async def list_conversations(
    workspace_id: uuid.UUID,
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    page_size: int = 20,
    page_token: str | None = None,
) -> dict:
    shop = await _get_shop(db, shop_id)
    service = CustomerServiceService(db)
    return await service.list_conversations(
        shop, page_size=page_size, page_token=page_token
    )


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    page_size: int = 20,
    page_token: str | None = None,
) -> dict:
    shop = await _get_shop(db, shop_id)
    service = CustomerServiceService(db)
    return await service.get_conversation_messages(
        shop, conversation_id, page_size=page_size, page_token=page_token
    )


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    shop_id: uuid.UUID,
    body: SendMessageRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    shop = await _get_shop(db, shop_id)
    service = CustomerServiceService(db)
    return await service.send_message(
        shop, conversation_id, content=body.content
    )


@router.post("/conversations/{conversation_id}/read")
async def mark_as_read(
    conversation_id: str,
    shop_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    shop = await _get_shop(db, shop_id)
    service = CustomerServiceService(db)
    return await service.mark_as_read(shop, conversation_id)

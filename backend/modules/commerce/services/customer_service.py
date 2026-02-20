import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.commerce import Shop
from backend.modules.commerce.services.shop_service import ShopService

logger = logging.getLogger(__name__)


class CustomerServiceService:
    """Service for TikTok Shop customer service (conversations/messages)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_conversations(
        self,
        shop: Shop,
        *,
        page_size: int = 20,
        page_token: str | None = None,
    ) -> dict:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)

        params: dict[str, str] = {"page_size": str(page_size)}
        if page_token:
            params["page_token"] = page_token

        resp = await gateway.get(
            "/customer_service/202309/conversations",
            params=params,
        )
        return resp.get("data", {})

    async def get_conversation_messages(
        self,
        shop: Shop,
        conversation_id: str,
        *,
        page_size: int = 20,
        page_token: str | None = None,
    ) -> dict:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)

        params: dict[str, str] = {"page_size": str(page_size)}
        if page_token:
            params["page_token"] = page_token

        resp = await gateway.get(
            f"/customer_service/202309/conversations/{conversation_id}/messages",
            params=params,
        )
        return resp.get("data", {})

    async def send_message(
        self,
        shop: Shop,
        conversation_id: str,
        *,
        content: str,
    ) -> dict:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)

        resp = await gateway.post(
            f"/customer_service/202309/conversations/{conversation_id}/messages",
            json_body={"content": content, "type": "TEXT"},
        )
        return resp.get("data", {})

    async def mark_as_read(
        self,
        shop: Shop,
        conversation_id: str,
    ) -> dict:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)

        resp = await gateway.post(
            f"/customer_service/202309/conversations/{conversation_id}/read",
        )
        return resp.get("data", {})

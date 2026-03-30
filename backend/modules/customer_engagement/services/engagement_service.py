import logging

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.commerce import Shop
from backend.modules.commerce.services.shop_service import ShopService

logger = logging.getLogger(__name__)


class EngagementService:
    """Service for TikTok Shop customer engagement (templates, tasks, permissions)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_templates(self, shop: Shop) -> dict:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        resp = await gateway.get("/customer_engagement/202309/templates")
        return resp.get("data", {})

    async def create_task(self, shop: Shop, *, task_data: dict) -> dict:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        resp = await gateway.post(
            "/customer_engagement/202309/tasks",
            json_body=task_data,
        )
        return resp.get("data", {})

    async def create_custom_task(self, shop: Shop, *, task_data: dict) -> dict:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        resp = await gateway.post(
            "/customer_engagement/202309/tasks/custom",
            json_body=task_data,
        )
        return resp.get("data", {})

    async def get_task_performance(self, shop: Shop, *, task_id: str) -> dict:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        resp = await gateway.get(
            f"/customer_engagement/202309/tasks/{task_id}/performance"
        )
        return resp.get("data", {})

    async def get_permissions(self, shop: Shop) -> dict:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        resp = await gateway.get("/customer_engagement/202309/permissions")
        return resp.get("data", {})

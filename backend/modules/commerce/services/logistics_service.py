import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.modules.commerce.services.shop_service import ShopService

logger = logging.getLogger(__name__)


class LogisticsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, shop_id: uuid.UUID):
        shop_service = ShopService(self._session)
        shop = await shop_service.get_shop(shop_id)
        if not shop:
            raise ValueError(f"Shop {shop_id} not found")
        return await shop_service.build_gateway_for_shop(shop)

    async def get_warehouses(self, shop_id: uuid.UUID) -> list[dict]:
        """List all warehouses for a shop."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get("/logistics/202309/warehouses")
        return resp.get("data", {}).get("warehouses", [])

    async def get_delivery_options(
        self, shop_id: uuid.UUID, warehouse_id: str
    ) -> list[dict]:
        """Get delivery options for a specific warehouse."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get(
            f"/logistics/202309/warehouses/{warehouse_id}/delivery_options"
        )
        return resp.get("data", {}).get("delivery_options", [])

    async def get_shipping_providers(self, shop_id: uuid.UUID) -> list[dict]:
        """List shipping providers for a shop."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get("/logistics/202309/shipping_providers")
        return resp.get("data", {}).get("shipping_providers", [])

    async def get_shipping_templates(self, shop_id: uuid.UUID) -> list[dict]:
        """List shipping templates for a shop."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get("/logistics/202510/shipping_templates")
        return resp.get("data", {}).get("shipping_templates", [])

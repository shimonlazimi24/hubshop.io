import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.modules.commerce.services.shop_service import ShopService

logger = logging.getLogger(__name__)


class SellerService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, shop_id: uuid.UUID):
        shop_service = ShopService(self._session)
        shop = await shop_service.get_shop(shop_id)
        if not shop:
            raise ValueError(f"Shop {shop_id} not found")
        return await shop_service.build_gateway_for_shop(shop)

    async def get_active_shops(self, shop_id: uuid.UUID) -> list[dict]:
        """List active shops visible to the seller."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get("/seller/202309/shops")
        return resp.get("data", {}).get("shops", [])

    async def get_seller_permissions(self, shop_id: uuid.UUID) -> list[dict]:
        """Get seller permissions for a shop."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get("/seller/202309/permissions")
        return resp.get("data", {}).get("permissions", [])

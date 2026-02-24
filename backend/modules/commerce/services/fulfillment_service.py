import json
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.commerce import (
    Order,
    Package,
    PackageStatus,
    Shop,
)
from backend.modules.commerce.services.shop_service import ShopService
from backend.tiktok.rate_limiter import get_redis

logger = logging.getLogger(__name__)


class FulfillmentService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, shop_id: uuid.UUID):
        shop_service = ShopService(self._session)
        shop = await shop_service.get_shop(shop_id)
        if not shop:
            raise ValueError(f"Shop {shop_id} not found")
        return await shop_service.build_gateway_for_shop(shop)

    async def split_order(
        self,
        shop_id: uuid.UUID,
        order_id: str,
        groups: list[list[str]],
    ) -> list[dict]:
        """Split an order into multiple packages."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            "/fulfillment/202309/orders/split",
            json_body={"order_id": order_id, "groups": groups},
        )
        return resp.get("data", {}).get("packages", [])

    async def batch_ship_packages(
        self,
        shop_id: uuid.UUID,
        packages: list[dict],
    ) -> list[dict]:
        """Batch ship multiple packages at once."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            "/fulfillment/202309/packages/batch_ship",
            json_body={"packages": packages},
        )
        return resp.get("data", {}).get("results", [])

    async def search_packages(
        self,
        shop_id: uuid.UUID,
        **filters,
    ) -> list[dict]:
        """Search packages with optional filters."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            "/fulfillment/202309/packages/search",
            json_body=filters or {},
        )
        return resp.get("data", {}).get("packages", [])

    async def get_shipping_document(
        self,
        shop_id: uuid.UUID,
        package_id: str,
        document_type: str = "SHIPPING_LABEL",
    ) -> dict:
        """Get a shipping document (label, invoice, etc.) for a package."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get(
            f"/fulfillment/202309/packages/{package_id}/shipping_document",
            params={"document_type": document_type},
        )
        return resp.get("data", {})

    async def update_shipping_info(
        self,
        shop_id: uuid.UUID,
        order_id: str,
        tracking_number: str,
        shipping_provider_id: str,
    ) -> dict:
        """Update shipping info (tracking number, provider) for an order."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            "/fulfillment/202309/packages/shipping_info/update",
            json_body={
                "order_id": order_id,
                "tracking_number": tracking_number,
                "shipping_provider_id": shipping_provider_id,
            },
        )
        return resp.get("data", {})

    async def get_eligible_shipping_services(self, order: Order) -> list[dict]:
        """Get eligible shipping services for an order from TikTok API."""
        result = await self._session.execute(
            select(Shop).where(Shop.id == order.shop_id)
        )
        shop = result.scalar_one_or_none()
        if not shop:
            return []

        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)

        resp = await gateway.post(
            "/fulfillment/202309/shipping_services/query",
            json_body={"order_id": order.platform_order_id},
        )
        services = resp.get("data", {}).get("shipping_services", [])
        return [{"id": s.get("id", ""), "name": s.get("name", "")} for s in services]

    async def ship_package(
        self,
        order: Order,
        *,
        shipping_provider: str,
        tracking_number: str,
    ) -> Package:
        """Create a shipment via TikTok API and record locally."""
        result = await self._session.execute(
            select(Shop).where(Shop.id == order.shop_id)
        )
        shop = result.scalar_one_or_none()
        if not shop:
            raise ValueError(f"Shop not found for order {order.id}")

        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)

        resp = await gateway.post(
            "/fulfillment/202309/packages/ship",
            json_body={
                "order_id": order.platform_order_id,
                "shipping_provider_id": shipping_provider,
                "tracking_number": tracking_number,
            },
        )
        pkg_data = resp.get("data", {})
        platform_package_id = str(pkg_data.get("package_id", uuid.uuid4().hex))

        package = Package(
            order_id=order.id,
            platform_package_id=platform_package_id,
            status=PackageStatus.SHIPPED,
            tracking_number=tracking_number,
            shipping_provider=shipping_provider,
        )
        self._session.add(package)
        await self._session.flush()

        await self._publish_package_update(order, package)
        return package

    async def mark_package_shipped(
        self,
        package_id: uuid.UUID,
        *,
        tracking_number: str | None = None,
    ) -> Package | None:
        """Mark a package as shipped (for manual fulfillment)."""
        result = await self._session.execute(
            select(Package).where(Package.id == package_id)
        )
        package = result.scalar_one_or_none()
        if not package:
            return None

        package.status = PackageStatus.SHIPPED
        if tracking_number:
            package.tracking_number = tracking_number

        # Get order for workspace_id
        order_result = await self._session.execute(
            select(Order).where(Order.id == package.order_id)
        )
        order = order_result.scalar_one_or_none()
        if order:
            await self._publish_package_update(order, package)

        return package

    async def get_package_detail(self, package_id: uuid.UUID) -> Package | None:
        result = await self._session.execute(
            select(Package).where(Package.id == package_id)
        )
        return result.scalar_one_or_none()

    async def get_tracking(self, order: Order) -> list[dict]:
        """Get tracking info for all packages of an order from TikTok API."""
        result = await self._session.execute(
            select(Shop).where(Shop.id == order.shop_id)
        )
        shop = result.scalar_one_or_none()
        if not shop:
            return []

        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)

        resp = await gateway.get(
            f"/fulfillment/202309/orders/{order.platform_order_id}/tracking"
        )
        return resp.get("data", {}).get("tracking", [])

    async def update_package_from_webhook(
        self, platform_package_id: str, new_status: str
    ) -> Package | None:
        result = await self._session.execute(
            select(Package).where(Package.platform_package_id == platform_package_id)
        )
        package = result.scalar_one_or_none()
        if not package:
            return None

        for member in PackageStatus:
            if member.value == new_status.lower():
                package.status = member
                break

        order_result = await self._session.execute(
            select(Order).where(Order.id == package.order_id)
        )
        order = order_result.scalar_one_or_none()
        if order:
            await self._publish_package_update(order, package)

        return package

    async def _publish_package_update(self, order: Order, package: Package) -> None:
        try:
            r = await get_redis()
            message = json.dumps(
                {
                    "type": "package_update",
                    "order_id": str(order.id),
                    "package_id": str(package.id),
                    "platform_package_id": package.platform_package_id,
                    "status": package.status.value,
                    "tracking_number": package.tracking_number,
                }
            )
            await r.publish(f"commerce:ws:{order.workspace_id}", message)
        except Exception:
            logger.exception("Failed to publish package update to Redis")

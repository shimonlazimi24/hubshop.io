import json
import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.commerce import (
    Order,
    OrderLineItem,
    OrderStatus,
    OrderStatusEvent,
    Package,
    PackageStatus,
    Shop,
)
from backend.modules.commerce.services.shop_service import ShopService
from backend.tiktok.rate_limiter import get_redis
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)

_STATUS_MAP: dict[str, OrderStatus] = {
    "UNPAID": OrderStatus.UNPAID,
    "ON_HOLD": OrderStatus.ON_HOLD,
    "AWAITING_SHIPMENT": OrderStatus.AWAITING_SHIPMENT,
    "AWAITING_COLLECTION": OrderStatus.AWAITING_COLLECTION,
    "PARTIALLY_SHIPPING": OrderStatus.PARTIALLY_SHIPPING,
    "IN_TRANSIT": OrderStatus.IN_TRANSIT,
    "DELIVERED": OrderStatus.DELIVERED,
    "COMPLETED": OrderStatus.COMPLETED,
    "CANCELLED": OrderStatus.CANCELLED,
}


class OrderService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_orders(
        self,
        workspace_id: uuid.UUID,
        *,
        shop_id: uuid.UUID | None = None,
        status: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Order]:
        query = select(Order).where(Order.workspace_id == workspace_id)
        count_query = select(func.count(Order.id)).where(
            Order.workspace_id == workspace_id
        )

        if shop_id:
            query = query.where(Order.shop_id == shop_id)
            count_query = count_query.where(Order.shop_id == shop_id)
        if status:
            query = query.where(Order.status == status)
            count_query = count_query.where(Order.status == status)
        if date_from:
            query = query.where(Order.created_at >= date_from)
            count_query = count_query.where(Order.created_at >= date_from)
        if date_to:
            query = query.where(Order.created_at <= date_to)
            count_query = count_query.where(Order.created_at <= date_to)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(Order.created_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(
            items=items, total=total, page=page, page_size=page_size
        )

    async def get_order(self, order_id: uuid.UUID) -> Order | None:
        result = await self._session.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_order_by_platform_id(
        self, platform_order_id: str
    ) -> Order | None:
        result = await self._session.execute(
            select(Order).where(Order.platform_order_id == platform_order_id)
        )
        return result.scalar_one_or_none()

    async def get_order_timeline(
        self, order_id: uuid.UUID
    ) -> list[OrderStatusEvent]:
        result = await self._session.execute(
            select(OrderStatusEvent)
            .where(OrderStatusEvent.order_id == order_id)
            .order_by(OrderStatusEvent.occurred_at.asc())
        )
        return list(result.scalars().all())

    async def sync_orders(
        self,
        shop: Shop,
        *,
        create_time_from: int,
        create_time_to: int,
    ) -> int:
        """Sync orders from TikTok Shop API for a time window. Returns count."""
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        synced = 0
        next_page_token = ""

        while True:
            body: dict = {
                "page_size": 50,
                "create_time_ge": create_time_from,
                "create_time_lt": create_time_to,
            }
            if next_page_token:
                body["page_token"] = next_page_token

            resp = await gateway.post(
                "/order/202309/orders", json_body=body
            )
            data = resp.get("data", {})
            orders_list = data.get("orders", [])

            for order_brief in orders_list:
                platform_order_id = str(order_brief["id"])
                # Fetch full detail
                detail_resp = await gateway.get(
                    f"/order/202309/orders/{platform_order_id}"
                )
                order_data = detail_resp.get("data", {})
                if order_data:
                    await self.upsert_order_from_api(
                        shop=shop, order_data=order_data
                    )
                    synced += 1

            next_page_token = data.get("next_page_token", "")
            if not next_page_token or not orders_list:
                break

        return synced

    async def upsert_order_from_api(
        self, *, shop: Shop, order_data: dict
    ) -> Order:
        """Create or update an order from TikTok API payload."""
        platform_id = str(order_data["id"])
        existing = await self.get_order_by_platform_id(platform_id)

        raw_status = order_data.get("status", "UNPAID")
        new_status = _STATUS_MAP.get(raw_status, OrderStatus.UNPAID)
        payment = order_data.get("payment", {})
        total_amount = payment.get("total_amount", "0")
        currency = payment.get("currency", "USD")
        line_items_data = order_data.get("line_items", [])
        packages_data = order_data.get("packages", [])
        rts_sla_ts = order_data.get("rts_sla")
        rts_sla = (
            datetime.fromtimestamp(int(rts_sla_ts))
            if rts_sla_ts
            else None
        )

        old_status = None
        if existing:
            old_status = existing.status.value if existing.status != new_status else None
            existing.status = new_status
            existing.total_amount = total_amount
            existing.currency = currency
            existing.item_count = len(line_items_data)
            existing.fulfillment_type = order_data.get("fulfillment_type")
            existing.rts_sla = rts_sla
            existing.detail_json = order_data
            order = existing
        else:
            order = Order(
                workspace_id=shop.workspace_id,
                shop_id=shop.id,
                platform_order_id=platform_id,
                status=new_status,
                total_amount=total_amount,
                currency=currency,
                item_count=len(line_items_data),
                fulfillment_type=order_data.get("fulfillment_type"),
                rts_sla=rts_sla,
                detail_json=order_data,
            )
            self._session.add(order)
            await self._session.flush()

        # Sync line items
        await self._sync_line_items(order, line_items_data)
        # Sync packages
        await self._sync_packages(order, packages_data)

        # Record status change
        if old_status and old_status != new_status.value:
            event = OrderStatusEvent(
                order_id=order.id,
                from_status=old_status,
                to_status=new_status.value,
                source="sync",
            )
            self._session.add(event)

        return order

    async def update_order_status(
        self,
        platform_order_id: str,
        new_status_str: str,
        *,
        source: str = "webhook",
    ) -> Order | None:
        """Update order status and record event. Returns updated order."""
        order = await self.get_order_by_platform_id(platform_order_id)
        if not order:
            return None

        new_status = _STATUS_MAP.get(new_status_str)
        if not new_status or order.status == new_status:
            return order

        old_status = order.status.value
        order.status = new_status

        event = OrderStatusEvent(
            order_id=order.id,
            from_status=old_status,
            to_status=new_status.value,
            source=source,
        )
        self._session.add(event)

        await self._publish_order_update(order, old_status, new_status.value)
        return order

    async def update_order_detail_json(
        self, platform_order_id: str, detail_patch: dict
    ) -> Order | None:
        order = await self.get_order_by_platform_id(platform_order_id)
        if not order:
            return None
        current = order.detail_json or {}
        current.update(detail_patch)
        order.detail_json = current
        return order

    # --- Gateway helper ---

    async def _get_gateway(self, shop_id: uuid.UUID) -> "PlatformGateway":  # noqa: F821
        """Build gateway for a shop by ID."""
        shop_service = ShopService(self._session)
        shop = await shop_service.get_shop(shop_id)
        if not shop:
            raise ValueError(f"Shop {shop_id} not found")
        return await shop_service.build_gateway_for_shop(shop)

    # --- Cancellation management ---

    async def cancel_order(
        self, shop_id: uuid.UUID, order_id: str, cancel_reason: str
    ) -> dict:
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            "/return_refund/202309/cancellations",
            json_body={"order_id": order_id, "cancel_reason": cancel_reason},
        )
        return resp.get("data", {})

    async def approve_cancellation(
        self, shop_id: uuid.UUID, order_id: str
    ) -> dict:
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            f"/return_refund/202309/cancellations/{order_id}/approve"
        )
        return resp.get("data", {})

    async def reject_cancellation(
        self, shop_id: uuid.UUID, order_id: str, reject_reason: str = ""
    ) -> dict:
        gateway = await self._get_gateway(shop_id)
        body: dict[str, Any] = {}
        if reject_reason:
            body["reject_reason"] = reject_reason
        resp = await gateway.post(
            f"/return_refund/202309/cancellations/{order_id}/reject",
            json_body=body if body else None,
        )
        return resp.get("data", {})

    async def search_cancellations(
        self, shop_id: uuid.UUID, **filters: Any
    ) -> list[dict]:
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            "/return_refund/202309/cancellations/search",
            json_body=filters or {},
        )
        return resp.get("data", {}).get("cancellations", [])

    # --- Price detail ---

    async def get_price_detail(
        self, shop_id: uuid.UUID, order_id: str
    ) -> dict:
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get(
            f"/order/202407/orders/{order_id}/price_detail"
        )
        return resp.get("data", {})

    async def _sync_line_items(
        self, order: Order, items_data: list[dict]
    ) -> None:
        # Clear existing and re-insert for simplicity
        result = await self._session.execute(
            select(OrderLineItem).where(OrderLineItem.order_id == order.id)
        )
        for existing_item in result.scalars().all():
            await self._session.delete(existing_item)
        await self._session.flush()

        for item in items_data:
            li = OrderLineItem(
                order_id=order.id,
                platform_sku_id=str(item.get("sku_id", "")),
                product_name=item.get("product_name", ""),
                quantity=item.get("quantity", 1),
                unit_price=item.get("sale_price", "0"),
                total_price=str(
                    float(item.get("sale_price", "0"))
                    * item.get("quantity", 1)
                ),
            )
            self._session.add(li)

    async def _sync_packages(
        self, order: Order, packages_data: list[dict]
    ) -> None:
        for pkg_data in packages_data:
            platform_pkg_id = str(pkg_data["id"])
            result = await self._session.execute(
                select(Package).where(
                    Package.platform_package_id == platform_pkg_id
                )
            )
            pkg = result.scalar_one_or_none()

            pkg_status = PackageStatus.PENDING
            raw_status = pkg_data.get("status", "PENDING")
            for member in PackageStatus:
                if member.value == raw_status.lower():
                    pkg_status = member
                    break

            if pkg:
                pkg.status = pkg_status
                pkg.tracking_number = pkg_data.get("tracking_number", pkg.tracking_number)
                pkg.shipping_provider = pkg_data.get(
                    "shipping_provider_name", pkg.shipping_provider
                )
            else:
                pkg = Package(
                    order_id=order.id,
                    platform_package_id=platform_pkg_id,
                    status=pkg_status,
                    tracking_number=pkg_data.get("tracking_number"),
                    shipping_provider=pkg_data.get("shipping_provider_name"),
                )
                self._session.add(pkg)

    async def _publish_order_update(
        self, order: Order, from_status: str, to_status: str
    ) -> None:
        """Publish order status change to Redis pub/sub for WebSocket."""
        try:
            r = await get_redis()
            message = json.dumps(
                {
                    "type": "order_status_change",
                    "order_id": str(order.id),
                    "platform_order_id": order.platform_order_id,
                    "from_status": from_status,
                    "to_status": to_status,
                }
            )
            await r.publish(
                f"commerce:ws:{order.workspace_id}", message
            )
        except Exception:
            logger.exception("Failed to publish order update to Redis")

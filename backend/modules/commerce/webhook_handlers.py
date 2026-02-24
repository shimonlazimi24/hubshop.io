"""Commerce webhook handlers for TikTok Shop events.

Each handler receives the raw webhook payload and a DB session.
Webhook type IDs (integers from TikTok):
  1  = Order Status Change
  3  = Recipient Address Update
  4  = Package Update
  5  = Product Status Change
  11 = Cancellation Status Change
  12 = Return Status Change
  15 = Product Information Change
  16 = Product Creation
  27 = Inventory Status Change
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from backend.modules.commerce.services.fulfillment_service import FulfillmentService
from backend.modules.commerce.services.order_service import OrderService
from backend.modules.commerce.services.product_service import ProductService
from backend.modules.commerce.services.return_service import ReturnService
from backend.modules.commerce.services.shop_service import ShopService

logger = logging.getLogger(__name__)


async def handle_order_status_change(payload: dict, session: AsyncSession) -> None:
    """Type 1: Order status changed."""
    data = payload.get("data", {})
    platform_order_id = str(data.get("order_id", ""))
    new_status = data.get("order_status", "")

    if not platform_order_id or not new_status:
        logger.warning("Order status change webhook missing data: %s", payload)
        return

    service = OrderService(session)
    await service.update_order_status(platform_order_id, new_status, source="webhook")


async def handle_recipient_address_update(payload: dict, session: AsyncSession) -> None:
    """Type 3: Recipient address updated on an order."""
    data = payload.get("data", {})
    platform_order_id = str(data.get("order_id", ""))

    if not platform_order_id:
        return

    service = OrderService(session)
    # Patch the detail_json with the new address data
    address = data.get("recipient_address", {})
    await service.update_order_detail_json(
        platform_order_id, {"recipient_address": address}
    )


async def handle_package_update(payload: dict, session: AsyncSession) -> None:
    """Type 4: Package status updated."""
    data = payload.get("data", {})
    platform_package_id = str(data.get("package_id", ""))
    new_status = data.get("package_status", "")

    if not platform_package_id:
        return

    service = FulfillmentService(session)
    await service.update_package_from_webhook(platform_package_id, new_status)


async def handle_product_status_change(payload: dict, session: AsyncSession) -> None:
    """Type 5: Product status changed."""
    data = payload.get("data", {})
    platform_product_id = str(data.get("product_id", ""))
    new_status = data.get("product_status", "")

    if not platform_product_id or not new_status:
        return

    service = ProductService(session)
    await service.update_product_status(platform_product_id, new_status)


async def handle_cancellation_status_change(
    payload: dict, session: AsyncSession
) -> None:
    """Type 11: Order cancellation."""
    data = payload.get("data", {})
    platform_order_id = str(data.get("order_id", ""))

    if not platform_order_id:
        return

    service = OrderService(session)
    await service.update_order_status(platform_order_id, "CANCELLED", source="webhook")


async def handle_return_status_change(payload: dict, session: AsyncSession) -> None:
    """Type 12: Return/refund status changed."""
    data = payload.get("data", {})
    service = ReturnService(session)
    await service.upsert_return_from_webhook(data)


async def handle_product_information_change(
    payload: dict, session: AsyncSession
) -> None:
    """Type 15: Product information changed. Re-fetch from API."""
    data = payload.get("data", {})
    platform_product_id = str(data.get("product_id", ""))
    shop_id_str = str(data.get("shop_id", ""))

    if not platform_product_id or not shop_id_str:
        return

    # Find the shop, then fetch product detail from API
    shop_service = ShopService(session)
    shop = await shop_service.get_shop_by_platform_id(shop_id_str)
    if not shop:
        logger.warning("Product info change for unknown shop %s", shop_id_str)
        return

    gateway = await shop_service.build_gateway_for_shop(shop)
    resp = await gateway.get(f"/product/202309/products/{platform_product_id}")
    product_data = resp.get("data", {})
    if product_data:
        product_service = ProductService(session)
        await product_service.upsert_product_from_api(
            shop=shop, product_data=product_data
        )


async def handle_product_creation(payload: dict, session: AsyncSession) -> None:
    """Type 16: New product created. Fetch full detail and insert."""
    # Same logic as product information change
    await handle_product_information_change(payload, session)


async def handle_inventory_status_change(payload: dict, session: AsyncSession) -> None:
    """Type 27: Inventory quantity changed."""
    data = payload.get("data", {})
    platform_product_id = str(data.get("product_id", ""))
    total_inventory = data.get("total_available_inventory")

    if not platform_product_id or total_inventory is None:
        return

    service = ProductService(session)
    await service.update_inventory(platform_product_id, int(total_inventory))


# Registry mapping webhook type strings to handlers
COMMERCE_WEBHOOK_HANDLERS: dict[str, object] = {
    "1": handle_order_status_change,
    "3": handle_recipient_address_update,
    "4": handle_package_update,
    "5": handle_product_status_change,
    "11": handle_cancellation_status_change,
    "12": handle_return_status_change,
    "15": handle_product_information_change,
    "16": handle_product_creation,
    "27": handle_inventory_status_change,
}

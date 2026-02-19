import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.commerce import Product, ProductSku, ProductStatus, Shop
from backend.modules.commerce.services.shop_service import ShopService
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)

# TikTok API status → local enum mapping
_STATUS_MAP: dict[str, ProductStatus] = {
    "DRAFT": ProductStatus.DRAFT,
    "PENDING": ProductStatus.PENDING,
    "LIVE": ProductStatus.LIVE,
    "SELLER_DEACTIVATED": ProductStatus.SELLER_DEACTIVATED,
    "PLATFORM_DEACTIVATED": ProductStatus.PLATFORM_DEACTIVATED,
    "FROZEN": ProductStatus.FROZEN,
    "DELETED": ProductStatus.DELETED,
}


class ProductService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_products(
        self,
        workspace_id: uuid.UUID,
        *,
        shop_id: uuid.UUID | None = None,
        status: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Product]:
        query = select(Product).where(Product.workspace_id == workspace_id)
        count_query = select(func.count(Product.id)).where(
            Product.workspace_id == workspace_id
        )

        if shop_id:
            query = query.where(Product.shop_id == shop_id)
            count_query = count_query.where(Product.shop_id == shop_id)
        if status:
            query = query.where(Product.status == status)
            count_query = count_query.where(Product.status == status)
        if search:
            query = query.where(Product.title.ilike(f"%{search}%"))
            count_query = count_query.where(Product.title.ilike(f"%{search}%"))

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(Product.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(
            items=items, total=total, page=page, page_size=page_size
        )

    async def get_product(self, product_id: uuid.UUID) -> Product | None:
        result = await self._session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def sync_products(self, shop: Shop) -> int:
        """Sync products from TikTok Shop API. Returns count of upserted products."""
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        synced = 0
        next_page_token = ""

        while True:
            body: dict = {"page_size": 50}
            if next_page_token:
                body["page_token"] = next_page_token

            resp = await gateway.post(
                "/product/202309/products/search", json_body=body
            )
            data = resp.get("data", {})
            products_list = data.get("products", [])

            for product_data in products_list:
                await self.upsert_product_from_api(
                    shop=shop, product_data=product_data
                )
                synced += 1

            next_page_token = data.get("next_page_token", "")
            if not next_page_token or not products_list:
                break

        return synced

    async def upsert_product_from_api(
        self, *, shop: Shop, product_data: dict
    ) -> Product:
        """Create or update a product from TikTok API payload."""
        platform_id = str(product_data["id"])
        result = await self._session.execute(
            select(Product).where(Product.platform_product_id == platform_id)
        )
        product = result.scalar_one_or_none()

        raw_status = product_data.get("status", "DRAFT")
        status = _STATUS_MAP.get(raw_status, ProductStatus.DRAFT)
        title = product_data.get("title", "")
        main_image = (
            product_data.get("main_images", [{}])[0].get("url")
            if product_data.get("main_images")
            else None
        )
        skus_data = product_data.get("skus", [])
        inventory_total = sum(
            s.get("inventory", [{}])[0].get("quantity", 0)
            if s.get("inventory")
            else 0
            for s in skus_data
        )
        price = (
            skus_data[0].get("price", {}).get("sale_price")
            if skus_data
            else None
        )
        currency = (
            skus_data[0].get("price", {}).get("currency")
            if skus_data
            else None
        )

        if product:
            product.title = title
            product.status = status
            product.main_image_url = main_image
            product.price_amount = price
            product.currency = currency
            product.inventory_total = inventory_total
            product.sku_count = len(skus_data)
            product.detail_json = product_data
        else:
            product = Product(
                workspace_id=shop.workspace_id,
                shop_id=shop.id,
                platform_product_id=platform_id,
                title=title,
                status=status,
                main_image_url=main_image,
                price_amount=price,
                currency=currency,
                inventory_total=inventory_total,
                sku_count=len(skus_data),
                detail_json=product_data,
            )
            self._session.add(product)
            await self._session.flush()

        # Sync SKUs
        await self._sync_skus(product, skus_data)
        return product

    async def _sync_skus(
        self, product: Product, skus_data: list[dict]
    ) -> None:
        """Upsert SKUs for a product."""
        for sku_data in skus_data:
            platform_sku_id = str(sku_data["id"])
            result = await self._session.execute(
                select(ProductSku).where(
                    ProductSku.platform_sku_id == platform_sku_id
                )
            )
            sku = result.scalar_one_or_none()

            inventory_qty = (
                sku_data.get("inventory", [{}])[0].get("quantity", 0)
                if sku_data.get("inventory")
                else 0
            )
            price_amount = sku_data.get("price", {}).get("sale_price")

            if sku:
                sku.seller_sku = sku_data.get("seller_sku")
                sku.price_amount = price_amount
                sku.inventory_quantity = inventory_qty
                sku.sku_name = sku_data.get("name")
            else:
                sku = ProductSku(
                    product_id=product.id,
                    platform_sku_id=platform_sku_id,
                    seller_sku=sku_data.get("seller_sku"),
                    price_amount=price_amount,
                    inventory_quantity=inventory_qty,
                    sku_name=sku_data.get("name"),
                )
                self._session.add(sku)

    async def update_product_status(
        self, platform_product_id: str, new_status: str
    ) -> Product | None:
        result = await self._session.execute(
            select(Product).where(
                Product.platform_product_id == platform_product_id
            )
        )
        product = result.scalar_one_or_none()
        if product:
            product.status = _STATUS_MAP.get(new_status, ProductStatus.DRAFT)
        return product

    async def update_inventory(
        self, platform_product_id: str, total_inventory: int
    ) -> Product | None:
        result = await self._session.execute(
            select(Product).where(
                Product.platform_product_id == platform_product_id
            )
        )
        product = result.scalar_one_or_none()
        if product:
            product.inventory_total = total_inventory
        return product

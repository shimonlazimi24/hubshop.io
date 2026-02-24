import logging
import uuid
from typing import Any

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
            query.order_by(Product.updated_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

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

            resp = await gateway.post("/product/202309/products/search", json_body=body)
            data = resp.get("data", {})
            products_list = data.get("products", [])

            for product_data in products_list:
                await self.upsert_product_from_api(shop=shop, product_data=product_data)
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
            s.get("inventory", [{}])[0].get("quantity", 0) if s.get("inventory") else 0
            for s in skus_data
        )
        price = skus_data[0].get("price", {}).get("sale_price") if skus_data else None
        currency = skus_data[0].get("price", {}).get("currency") if skus_data else None

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

    async def _sync_skus(self, product: Product, skus_data: list[dict]) -> None:
        """Upsert SKUs for a product."""
        for sku_data in skus_data:
            platform_sku_id = str(sku_data["id"])
            result = await self._session.execute(
                select(ProductSku).where(ProductSku.platform_sku_id == platform_sku_id)
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

    async def _get_gateway(self, shop_id: uuid.UUID) -> "PlatformGateway":
        """Build gateway for a shop by ID."""
        shop_service = ShopService(self._session)
        shop = await shop_service.get_shop(shop_id)
        if not shop:
            raise ValueError(f"Shop {shop_id} not found")
        return await shop_service.build_gateway_for_shop(shop)

    async def get_categories(self, shop_id: uuid.UUID) -> list[dict]:
        """Get all product categories for a shop."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get("/product/202309/categories")
        return resp.get("data", {}).get("categories", [])

    async def recommend_categories(
        self, shop_id: uuid.UUID, product_title: str
    ) -> list[dict]:
        """Recommend categories for a product title."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            "/product/202309/categories/recommend",
            json_body={"product_title": product_title},
        )
        return resp.get("data", {}).get("categories", [])

    async def get_category_rules(
        self, shop_id: uuid.UUID, category_id: str
    ) -> list[dict]:
        """Get rules for a specific category."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get(f"/product/202309/categories/{category_id}/rules")
        return resp.get("data", {}).get("category_rules", [])

    async def get_attributes(self, shop_id: uuid.UUID, category_id: str) -> list[dict]:
        """Get attributes for a specific category."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get(f"/product/202309/categories/{category_id}/attributes")
        return resp.get("data", {}).get("attributes", [])

    async def create_product(
        self,
        workspace_id: uuid.UUID,
        shop_id: uuid.UUID,
        *,
        title: str,
        description: str,
        category_id: str,
        images: list[dict],
        skus: list[dict],
        package_dimensions: dict | None = None,
    ) -> dict:
        """Create a product on TikTok Shop and persist locally."""
        gateway = await self._get_gateway(shop_id)
        body: dict = {
            "title": title,
            "description": description,
            "category_id": category_id,
            "main_images": [
                {"uri": img.get("url", img.get("uri", ""))} for img in images
            ],
            "skus": skus,
        }
        if package_dimensions:
            body["package_dimensions"] = package_dimensions

        resp = await gateway.post("/product/202309/products", json_body=body)
        data = resp.get("data", {})

        # Fetch full product to persist locally
        product_id = data.get("product_id", "")
        if product_id:
            detail_resp = await gateway.get(f"/product/202309/products/{product_id}")
            product_data = detail_resp.get("data", {})
            if product_data:
                shop = await ShopService(self._session).get_shop(shop_id)
                if shop:
                    await self.upsert_product_from_api(
                        shop=shop, product_data=product_data
                    )

        return data

    async def edit_product(
        self,
        shop_id: uuid.UUID,
        platform_product_id: str,
        *,
        title: str,
        description: str,
        category_id: str,
        images: list[dict],
        skus: list[dict],
    ) -> dict:
        """Full product edit via TikTok API."""
        gateway = await self._get_gateway(shop_id)
        body = {
            "title": title,
            "description": description,
            "category_id": category_id,
            "main_images": [
                {"uri": img.get("url", img.get("uri", ""))} for img in images
            ],
            "skus": skus,
        }
        resp = await gateway.put(
            f"/product/202309/products/{platform_product_id}",
            json_body=body,
        )
        return resp.get("data", {})

    async def partial_edit_product(
        self,
        shop_id: uuid.UUID,
        platform_product_id: str,
        **fields: Any,
    ) -> dict:
        """Partial product edit -- only update provided fields."""
        gateway = await self._get_gateway(shop_id)
        body = {k: v for k, v in fields.items() if v is not None}
        resp = await gateway.put(
            f"/product/202312/products/{platform_product_id}/partial_edit",
            json_body=body,
        )
        return resp.get("data", {})

    async def update_product_status(
        self, platform_product_id: str, new_status: str
    ) -> Product | None:
        result = await self._session.execute(
            select(Product).where(Product.platform_product_id == platform_product_id)
        )
        product = result.scalar_one_or_none()
        if product:
            product.status = _STATUS_MAP.get(new_status, ProductStatus.DRAFT)
        return product

    async def update_inventory(
        self, platform_product_id: str, total_inventory: int
    ) -> Product | None:
        result = await self._session.execute(
            select(Product).where(Product.platform_product_id == platform_product_id)
        )
        product = result.scalar_one_or_none()
        if product:
            product.inventory_total = total_inventory
        return product

    # --- Task 4: Product Lifecycle Batch Operations ---

    async def delete_products(self, shop_id: uuid.UUID, product_ids: list[str]) -> dict:
        """Batch delete products via TikTok API."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.delete(
            "/product/202309/products",
            json_body={"product_ids": product_ids},
        )
        return resp.get("data", {})

    async def activate_products(
        self, shop_id: uuid.UUID, product_ids: list[str]
    ) -> dict:
        """Batch activate products via TikTok API."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            "/product/202309/products/activate",
            json_body={"product_ids": product_ids},
        )
        return resp.get("data", {})

    async def deactivate_products(
        self, shop_id: uuid.UUID, product_ids: list[str]
    ) -> dict:
        """Batch deactivate products via TikTok API."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            "/product/202309/products/deactivate",
            json_body={"product_ids": product_ids},
        )
        return resp.get("data", {})

    async def recover_products(
        self, shop_id: uuid.UUID, product_ids: list[str]
    ) -> dict:
        """Batch recover deleted products via TikTok API."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            "/product/202309/products/recover",
            json_body={"product_ids": product_ids},
        )
        return resp.get("data", {})

    # --- Task 5: Price & Inventory Update via API ---

    async def update_price_api(
        self, shop_id: uuid.UUID, product_id: str, skus: list[dict]
    ) -> dict:
        """Update product prices via TikTok API."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            "/product/202309/products/prices",
            json_body={"product_id": product_id, "skus": skus},
        )
        return resp.get("data", {})

    async def update_inventory_api(
        self, shop_id: uuid.UUID, product_id: str, skus: list[dict]
    ) -> dict:
        """Update product inventory via TikTok API."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            "/product/202309/products/inventory",
            json_body={"product_id": product_id, "skus": skus},
        )
        return resp.get("data", {})

    # --- Task 6: Image & File Upload ---

    async def upload_product_image(self, shop_id: uuid.UUID, image_url: str) -> dict:
        """Upload product image via URL to TikTok CDN."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            "/product/202309/images/upload",
            json_body={"img_url": image_url},
        )
        return resp.get("data", {})

    async def upload_product_file(
        self, shop_id: uuid.UUID, file_url: str, file_name: str
    ) -> dict:
        """Upload product file (certification, etc.) to TikTok."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            "/product/202309/files/upload",
            json_body={"file_url": file_url, "name": file_name},
        )
        return resp.get("data", {})

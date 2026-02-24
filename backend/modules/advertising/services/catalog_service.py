import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount, Catalog
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class CatalogService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, ad_account: AdAccount):
        account_service = AdAccountService(self._session)
        return await account_service.build_gateway_for_ad_account(ad_account)

    async def list_catalogs(
        self,
        workspace_id: uuid.UUID,
        *,
        ad_account_id: uuid.UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Catalog]:
        query = select(Catalog).where(Catalog.workspace_id == workspace_id)
        count_query = select(func.count(Catalog.id)).where(
            Catalog.workspace_id == workspace_id
        )

        if ad_account_id:
            query = query.where(Catalog.ad_account_id == ad_account_id)
            count_query = count_query.where(Catalog.ad_account_id == ad_account_id)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(Catalog.updated_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    async def get_catalog(self, catalog_id: uuid.UUID) -> Catalog | None:
        result = await self._session.execute(
            select(Catalog).where(Catalog.id == catalog_id)
        )
        return result.scalar_one_or_none()

    async def create_catalog(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        name: str,
    ) -> Catalog:
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        resp = await gateway.post(
            "/catalog/create/",
            json_body={
                "bc_id": ad_account.advertiser_id,
                "catalog_name": name,
            },
        )
        data = resp.get("data", {})
        platform_id = str(data.get("catalog_id", ""))

        catalog = Catalog(
            workspace_id=workspace_id,
            ad_account_id=ad_account.id,
            platform_catalog_id=platform_id,
            name=name,
            detail_json=data,
        )
        self._session.add(catalog)
        await self._session.flush()
        return catalog

    async def add_products_to_catalog(
        self,
        catalog: Catalog,
        ad_account: AdAccount,
        *,
        product_ids: list[str],
    ) -> dict:
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        resp = await gateway.post(
            "/catalog/product/add/",
            json_body={
                "bc_id": ad_account.advertiser_id,
                "catalog_id": catalog.platform_catalog_id,
                "product_ids": product_ids,
            },
        )
        return resp.get("data", {})

    async def sync_catalogs(self, ad_account: AdAccount) -> int:
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)
        synced = 0
        page = 1

        while True:
            resp = await gateway.get(
                "/catalog/list/",
                params={
                    "bc_id": ad_account.advertiser_id,
                    "page": str(page),
                    "page_size": "100",
                },
            )
            data = resp.get("data", {})
            catalog_list = data.get("catalogs", [])

            for cat_data in catalog_list:
                await self._upsert_catalog(ad_account, cat_data)
                synced += 1

            total_page = data.get("page_info", {}).get("total_page", 1)
            if page >= total_page or not catalog_list:
                break
            page += 1

        return synced

    # ---- Product Set methods ----

    async def list_product_sets(
        self,
        ad_account: AdAccount,
        catalog_id: str,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List product sets for a catalog."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/catalog/product_set/get/",
            params={
                "bc_id": ad_account.advertiser_id,
                "catalog_id": catalog_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def get_product_set_products(
        self,
        ad_account: AdAccount,
        catalog_id: str,
        product_set_id: str,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List products within a product set."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/catalog/product_set/product/get/",
            params={
                "bc_id": ad_account.advertiser_id,
                "catalog_id": catalog_id,
                "product_set_id": product_set_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def create_product_set_by_conditions(
        self,
        ad_account: AdAccount,
        catalog_id: str,
        name: str,
        conditions: list[dict],
    ) -> dict:
        """Create a product set using filter conditions."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/catalog/product_set/condition/create/",
            json_body={
                "bc_id": ad_account.advertiser_id,
                "catalog_id": catalog_id,
                "product_set_name": name,
                "conditions": conditions,
            },
        )
        return resp.get("data", {})

    async def create_product_set_by_file(
        self,
        ad_account: AdAccount,
        catalog_id: str,
        name: str,
        file_url: str,
    ) -> dict:
        """Create a product set from an uploaded file."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/catalog/product_set/file/create/",
            json_body={
                "bc_id": ad_account.advertiser_id,
                "catalog_id": catalog_id,
                "product_set_name": name,
                "file_url": file_url,
            },
        )
        return resp.get("data", {})

    async def update_product_set(
        self,
        ad_account: AdAccount,
        catalog_id: str,
        product_set_id: str,
        *,
        name: str | None = None,
        conditions: list[dict] | None = None,
    ) -> dict:
        """Update a product set name and/or conditions."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "bc_id": ad_account.advertiser_id,
            "catalog_id": catalog_id,
            "product_set_id": product_set_id,
        }
        if name is not None:
            body["product_set_name"] = name
        if conditions is not None:
            body["conditions"] = conditions
        resp = await gateway.post(
            "/catalog/product_set/update/",
            json_body=body,
        )
        return resp.get("data", {})

    async def delete_product_sets(
        self,
        ad_account: AdAccount,
        catalog_id: str,
        product_set_ids: list[str],
    ) -> dict:
        """Delete one or more product sets."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/catalog/product_set/delete/",
            json_body={
                "bc_id": ad_account.advertiser_id,
                "catalog_id": catalog_id,
                "product_set_ids": product_set_ids,
            },
        )
        return resp.get("data", {})

    # ---- Feed Management methods ----

    async def list_feeds(
        self,
        ad_account: AdAccount,
        catalog_id: str,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List feeds for a catalog."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/catalog/feed/get/",
            params={
                "bc_id": ad_account.advertiser_id,
                "catalog_id": catalog_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def create_feed(
        self,
        ad_account: AdAccount,
        catalog_id: str,
        feed_name: str,
        feed_url: str,
        auto_update: bool = True,
        schedule: dict | None = None,
    ) -> dict:
        """Create a new feed for a catalog."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "bc_id": ad_account.advertiser_id,
            "catalog_id": catalog_id,
            "feed_name": feed_name,
            "feed_url": feed_url,
            "auto_update": auto_update,
        }
        if schedule is not None:
            body["schedule"] = schedule
        resp = await gateway.post("/catalog/feed/create/", json_body=body)
        return resp.get("data", {})

    async def update_feed(
        self,
        ad_account: AdAccount,
        catalog_id: str,
        feed_id: str,
        feed_name: str | None = None,
        feed_url: str | None = None,
    ) -> dict:
        """Update a feed's name and/or URL."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "bc_id": ad_account.advertiser_id,
            "catalog_id": catalog_id,
            "feed_id": feed_id,
        }
        if feed_name is not None:
            body["feed_name"] = feed_name
        if feed_url is not None:
            body["feed_url"] = feed_url
        resp = await gateway.post("/catalog/feed/update/", json_body=body)
        return resp.get("data", {})

    async def delete_feed(
        self,
        ad_account: AdAccount,
        catalog_id: str,
        feed_id: str,
    ) -> dict:
        """Delete a feed from a catalog."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/catalog/feed/delete/",
            json_body={
                "bc_id": ad_account.advertiser_id,
                "catalog_id": catalog_id,
                "feed_id": feed_id,
            },
        )
        return resp.get("data", {})

    async def get_feed_log(
        self,
        ad_account: AdAccount,
        catalog_id: str,
        feed_id: str,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Get the sync log for a feed."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/catalog/feed/log/",
            params={
                "bc_id": ad_account.advertiser_id,
                "catalog_id": catalog_id,
                "feed_id": feed_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def update_feed_schedule(
        self,
        ad_account: AdAccount,
        catalog_id: str,
        feed_id: str,
        schedule: dict,
    ) -> dict:
        """Update the sync schedule for a feed."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/catalog/feed/schedule/update/",
            json_body={
                "bc_id": ad_account.advertiser_id,
                "catalog_id": catalog_id,
                "feed_id": feed_id,
                "schedule": schedule,
            },
        )
        return resp.get("data", {})

    # ---- Insights, Diagnostics & Event Source methods ----

    async def get_catalog_overview(
        self,
        ad_account: AdAccount,
        catalog_id: str,
    ) -> dict:
        """Get catalog overview statistics."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/catalog/overview/get/",
            params={
                "bc_id": ad_account.advertiser_id,
                "catalog_id": catalog_id,
            },
        )
        return resp.get("data", {})

    async def get_trending_products(
        self,
        ad_account: AdAccount,
        catalog_id: str,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Get trending products for a catalog."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/catalog/insights/product/trending/",
            params={
                "bc_id": ad_account.advertiser_id,
                "catalog_id": catalog_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def get_trending_categories(
        self,
        ad_account: AdAccount,
        catalog_id: str,
    ) -> dict:
        """Get trending categories for a catalog."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/catalog/insights/category/trending/",
            params={
                "bc_id": ad_account.advertiser_id,
                "catalog_id": catalog_id,
            },
        )
        return resp.get("data", {})

    async def get_product_diagnostics(
        self,
        ad_account: AdAccount,
        catalog_id: str,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Get product diagnostics for a catalog."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/catalog/diagnostics/product/get/",
            params={
                "bc_id": ad_account.advertiser_id,
                "catalog_id": catalog_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def get_event_source_diagnostics(
        self,
        ad_account: AdAccount,
        catalog_id: str,
    ) -> dict:
        """Get event source diagnostics for a catalog."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/catalog/diagnostics/event_source/get/",
            params={
                "bc_id": ad_account.advertiser_id,
                "catalog_id": catalog_id,
            },
        )
        return resp.get("data", {})

    async def bind_event_source(
        self,
        ad_account: AdAccount,
        catalog_id: str,
        event_source_id: str,
    ) -> dict:
        """Bind an event source to a catalog."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/catalog/event_source/bind/",
            json_body={
                "bc_id": ad_account.advertiser_id,
                "catalog_id": catalog_id,
                "event_source_id": event_source_id,
            },
        )
        return resp.get("data", {})

    async def unbind_event_source(
        self,
        ad_account: AdAccount,
        catalog_id: str,
        event_source_id: str,
    ) -> dict:
        """Unbind an event source from a catalog."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/catalog/event_source/unbind/",
            json_body={
                "bc_id": ad_account.advertiser_id,
                "catalog_id": catalog_id,
                "event_source_id": event_source_id,
            },
        )
        return resp.get("data", {})

    async def _upsert_catalog(self, ad_account: AdAccount, cat_data: dict) -> Catalog:
        platform_id = str(cat_data.get("catalog_id", ""))
        result = await self._session.execute(
            select(Catalog).where(Catalog.platform_catalog_id == platform_id)
        )
        catalog = result.scalar_one_or_none()

        name = cat_data.get("catalog_name", "")
        product_count = cat_data.get("product_count", 0)
        status = cat_data.get("status", "ACTIVE")

        if catalog:
            catalog.name = name
            catalog.product_count = product_count
            catalog.status = status
            catalog.detail_json = cat_data
        else:
            catalog = Catalog(
                workspace_id=ad_account.workspace_id,
                ad_account_id=ad_account.id,
                platform_catalog_id=platform_id,
                name=name,
                product_count=product_count,
                status=status,
                detail_json=cat_data,
            )
            self._session.add(catalog)
            await self._session.flush()

        return catalog

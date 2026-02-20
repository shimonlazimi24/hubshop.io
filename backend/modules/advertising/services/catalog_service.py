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

        return PaginatedResult(
            items=items, total=total, page=page, page_size=page_size
        )

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

    async def _upsert_catalog(
        self, ad_account: AdAccount, cat_data: dict
    ) -> Catalog:
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

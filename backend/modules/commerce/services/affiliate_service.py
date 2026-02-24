import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.affiliate import (
    AffiliateProduct,
    CreatorApplication,
    OpenCollaboration,
    TargetCollaboration,
)
from backend.db.models.commerce import Shop
from backend.modules.commerce.services.shop_service import ShopService
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class AffiliateService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # --- Affiliate Products ---

    async def list_affiliate_products(
        self,
        workspace_id: uuid.UUID,
        *,
        shop_id: uuid.UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[AffiliateProduct]:
        query = select(AffiliateProduct).where(
            AffiliateProduct.workspace_id == workspace_id
        )
        count_query = select(func.count(AffiliateProduct.id)).where(
            AffiliateProduct.workspace_id == workspace_id
        )

        if shop_id:
            query = query.where(AffiliateProduct.shop_id == shop_id)
            count_query = count_query.where(AffiliateProduct.shop_id == shop_id)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(AffiliateProduct.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())
        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    async def add_to_marketplace(
        self,
        workspace_id: uuid.UUID,
        shop: Shop,
        *,
        product_id: str,
        commission_rate: str,
    ) -> AffiliateProduct:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)

        await gateway.post(
            "/affiliate/202309/seller/open_collaboration_settings",
            json_body={
                "product_ids": [product_id],
                "commission_rate": commission_rate,
            },
        )

        product = AffiliateProduct(
            workspace_id=workspace_id,
            shop_id=shop.id,
            product_id=product_id,
            commission_rate=commission_rate,
            status="ACTIVE",
        )
        self._session.add(product)
        await self._session.flush()
        return product

    async def remove_from_marketplace(
        self,
        affiliate_product: AffiliateProduct,
        shop: Shop,
    ) -> None:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)

        await gateway.post(
            "/affiliate/202309/seller/open_collaboration_settings/remove",
            json_body={"product_ids": [affiliate_product.product_id]},
        )
        affiliate_product.status = "INACTIVE"

    # --- Open Collaborations ---

    async def list_open_collaborations(
        self,
        workspace_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[OpenCollaboration]:
        query = select(OpenCollaboration).where(
            OpenCollaboration.workspace_id == workspace_id
        )
        count_query = select(func.count(OpenCollaboration.id)).where(
            OpenCollaboration.workspace_id == workspace_id
        )

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(OpenCollaboration.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())
        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    async def create_open_collaboration(
        self,
        workspace_id: uuid.UUID,
        shop: Shop,
        *,
        product_id: str,
        commission_rate: str,
    ) -> OpenCollaboration:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)

        resp = await gateway.post(
            "/affiliate/202309/seller/open_collaborations",
            json_body={
                "product_id": product_id,
                "commission_rate": commission_rate,
            },
        )

        collab = OpenCollaboration(
            workspace_id=workspace_id,
            product_id=product_id,
            commission_rate=commission_rate,
            status="ACTIVE",
            detail_json=resp.get("data", {}),
        )
        self._session.add(collab)
        await self._session.flush()
        return collab

    # --- Target Collaborations ---

    async def list_target_collaborations(
        self,
        workspace_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[TargetCollaboration]:
        query = select(TargetCollaboration).where(
            TargetCollaboration.workspace_id == workspace_id
        )
        count_query = select(func.count(TargetCollaboration.id)).where(
            TargetCollaboration.workspace_id == workspace_id
        )

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(TargetCollaboration.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())
        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    async def create_target_collaboration(
        self,
        workspace_id: uuid.UUID,
        shop: Shop,
        *,
        product_id: str,
        creator_id: str,
        commission_rate: str,
    ) -> TargetCollaboration:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)

        resp = await gateway.post(
            "/affiliate/202309/seller/target_collaborations",
            json_body={
                "product_id": product_id,
                "creator_id": creator_id,
                "commission_rate": commission_rate,
            },
        )

        collab = TargetCollaboration(
            workspace_id=workspace_id,
            product_id=product_id,
            creator_id=creator_id,
            commission_rate=commission_rate,
            status="ACTIVE",
            invite_status="PENDING",
            detail_json=resp.get("data", {}),
        )
        self._session.add(collab)
        await self._session.flush()
        return collab

    # --- Creator Applications ---

    async def respond_to_application(
        self,
        application_id: uuid.UUID,
        *,
        approved: bool,
    ) -> CreatorApplication:
        result = await self._session.execute(
            select(CreatorApplication).where(CreatorApplication.id == application_id)
        )
        application = result.scalar_one_or_none()
        if not application:
            raise ValueError("Application not found")

        application.status = "APPROVED" if approved else "REJECTED"
        return application

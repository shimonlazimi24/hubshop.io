import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.affiliate import (
    AffiliateOrder,
    AffiliateProduct,
    CreatorApplication,
    OpenCollaboration,
    SampleRequest,
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

    # --- Creator Discovery (E1) ---

    async def search_creators(
        self,
        shop: Shop,
        *,
        category: str | None = None,
        min_followers: int | None = None,
        page_size: int = 20,
    ) -> dict:
        """Search for affiliate creators on TikTok Shop."""
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        params: dict[str, str] = {"page_size": str(page_size)}
        if category:
            params["category"] = category
        if min_followers:
            params["min_followers"] = str(min_followers)
        resp = await gateway.get("/affiliate/202309/seller/creators", params=params)
        return resp.get("data", {})

    async def get_creator_performance(self, shop: Shop, creator_id: str) -> dict:
        """Get performance metrics for a specific affiliate creator."""
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        resp = await gateway.get(
            f"/affiliate/202309/seller/creators/{creator_id}/performance"
        )
        return resp.get("data", {})

    async def get_creator_profile(self, shop: Shop, creator_id: str) -> dict:
        """Get profile details for a specific affiliate creator."""
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        resp = await gateway.get(
            f"/affiliate/202309/seller/creators/{creator_id}/profile"
        )
        return resp.get("data", {})

    # --- Sample Management (E2) ---

    async def list_sample_requests(
        self,
        workspace_id: uuid.UUID,
        *,
        shop_id: uuid.UUID | None = None,
        status_filter: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[SampleRequest]:
        """List sample requests for a workspace."""
        query = select(SampleRequest).where(SampleRequest.workspace_id == workspace_id)
        count_query = select(func.count(SampleRequest.id)).where(
            SampleRequest.workspace_id == workspace_id
        )

        if shop_id:
            query = query.where(SampleRequest.shop_id == shop_id)
            count_query = count_query.where(SampleRequest.shop_id == shop_id)

        if status_filter:
            query = query.where(SampleRequest.status == status_filter)
            count_query = count_query.where(SampleRequest.status == status_filter)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(SampleRequest.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())
        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    async def review_sample(
        self,
        shop: Shop,
        request_id: str,
        *,
        approved: bool,
        reason: str | None = None,
    ) -> dict:
        """Approve or reject a sample request via TikTok API."""
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        body: dict[str, object] = {"approved": approved}
        if reason:
            body["reason"] = reason
        resp = await gateway.post(
            f"/affiliate/202309/seller/samples/{request_id}/review",
            json_body=body,
        )
        return resp.get("data", {})

    # --- Affiliate Order Tracking (E3) ---

    async def list_affiliate_orders(
        self,
        workspace_id: uuid.UUID,
        *,
        shop_id: uuid.UUID | None = None,
        creator_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[AffiliateOrder]:
        """List affiliate orders for a workspace."""
        query = select(AffiliateOrder).where(
            AffiliateOrder.workspace_id == workspace_id
        )
        count_query = select(func.count(AffiliateOrder.id)).where(
            AffiliateOrder.workspace_id == workspace_id
        )

        if shop_id:
            query = query.where(AffiliateOrder.shop_id == shop_id)
            count_query = count_query.where(AffiliateOrder.shop_id == shop_id)

        if creator_id:
            query = query.where(AffiliateOrder.creator_id == creator_id)
            count_query = count_query.where(AffiliateOrder.creator_id == creator_id)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(AffiliateOrder.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())
        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    async def sync_affiliate_orders(self, shop: Shop) -> int:
        """Fetch affiliate orders from TikTok API and upsert locally."""
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        resp = await gateway.get("/affiliate/202309/seller/orders")
        orders_data = resp.get("data", {}).get("orders", [])
        synced = 0
        for order_data in orders_data:
            platform_order_id = order_data.get("order_id", "")
            # Check if already exists
            existing = await self._session.execute(
                select(AffiliateOrder).where(
                    AffiliateOrder.platform_order_id == platform_order_id
                )
            )
            if existing.scalar_one_or_none():
                continue  # Skip existing, could update in future

            order = AffiliateOrder(
                workspace_id=shop.workspace_id,
                shop_id=shop.id,
                platform_order_id=platform_order_id,
                creator_id=order_data.get("creator_id", ""),
                collab_type=order_data.get("collab_type", "OPEN"),
                product_id=order_data.get("product_id", ""),
                order_amount=order_data.get("order_amount", "0"),
                commission_rate=order_data.get("commission_rate", "0"),
                commission_amount=order_data.get("commission_amount", "0"),
                detail_json=order_data,
            )
            self._session.add(order)
            synced += 1
        await self._session.flush()
        return synced

    # --- Creator Messaging (E4) ---

    async def get_creator_conversations(self, shop: Shop, page_size: int = 20) -> dict:
        """Get affiliate creator conversations."""
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        resp = await gateway.get(
            "/affiliate/202309/seller/conversations",
            params={"page_size": str(page_size)},
        )
        return resp.get("data", {})

    async def send_creator_message(
        self, shop: Shop, conversation_id: str, *, content: str
    ) -> dict:
        """Send a message to an affiliate creator conversation."""
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        resp = await gateway.post(
            f"/affiliate/202309/seller/conversations/{conversation_id}/messages",
            json_body={"content": content},
        )
        return resp.get("data", {})

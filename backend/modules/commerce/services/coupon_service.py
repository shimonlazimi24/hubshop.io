import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.commerce import Shop
from backend.db.models.coupon import Coupon
from backend.modules.commerce.services.shop_service import ShopService
from backend.tiktok.gateway import PlatformGateway
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class CouponService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _build_gateway(self, shop: Shop) -> PlatformGateway:
        shop_service = ShopService(self._session)
        return await shop_service.build_gateway_for_shop(shop)

    async def list_coupons(
        self,
        workspace_id: uuid.UUID,
        *,
        shop_id: uuid.UUID | None = None,
        status_filter: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Coupon]:
        query = select(Coupon).where(Coupon.workspace_id == workspace_id)
        count_query = select(func.count(Coupon.id)).where(
            Coupon.workspace_id == workspace_id
        )

        if shop_id:
            query = query.where(Coupon.shop_id == shop_id)
            count_query = count_query.where(Coupon.shop_id == shop_id)
        if status_filter:
            query = query.where(Coupon.status == status_filter)
            count_query = count_query.where(Coupon.status == status_filter)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(Coupon.updated_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    async def sync_coupons(self, shop: Shop) -> int:
        gateway = await self._build_gateway(shop)
        synced = 0

        resp = await gateway.get(
            "/promotion/202309/coupons",
            params={"page_size": "50"},
        )
        data = resp.get("data", {})
        coupons = data.get("coupons", [])

        for coupon_data in coupons:
            await self._upsert_coupon(shop, coupon_data)
            synced += 1

        return synced

    async def _upsert_coupon(self, shop: Shop, data: dict) -> Coupon:
        platform_id = str(data.get("coupon_id", ""))
        result = await self._session.execute(
            select(Coupon).where(Coupon.platform_coupon_id == platform_id)
        )
        coupon = result.scalar_one_or_none()

        if coupon:
            coupon.claimed_count = data.get("claimed_count", 0)
            coupon.used_count = data.get("used_count", 0)
            coupon.status = data.get("status", coupon.status)
        else:
            coupon = Coupon(
                workspace_id=shop.workspace_id,
                shop_id=shop.id,
                platform_coupon_id=platform_id,
                code=data.get("code", ""),
                discount_type=data.get("discount_type", ""),
                discount_value=str(data.get("discount_value", "0")),
                min_order_amount=(
                    str(data.get("min_order_amount"))
                    if data.get("min_order_amount")
                    else None
                ),
                total_claim_limit=data.get("claim_limit"),
                per_user_limit=data.get("per_user_limit"),
                claimed_count=data.get("claimed_count", 0),
                used_count=data.get("used_count", 0),
                status=data.get("status", "ACTIVE"),
            )
            self._session.add(coupon)
            await self._session.flush()

        return coupon

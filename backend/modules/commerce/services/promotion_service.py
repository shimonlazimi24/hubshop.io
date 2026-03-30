import logging
import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.commerce import Promotion, Shop
from backend.modules.commerce.services.shop_service import ShopService
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class PromotionService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_promotions(
        self,
        workspace_id: uuid.UUID,
        *,
        shop_id: uuid.UUID | None = None,
        status_filter: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Promotion]:
        query = select(Promotion).where(Promotion.workspace_id == workspace_id)
        count_query = select(func.count(Promotion.id)).where(
            Promotion.workspace_id == workspace_id
        )

        if shop_id:
            query = query.where(Promotion.shop_id == shop_id)
            count_query = count_query.where(Promotion.shop_id == shop_id)
        if status_filter:
            query = query.where(Promotion.status == status_filter)
            count_query = count_query.where(Promotion.status == status_filter)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(Promotion.updated_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    async def get_promotion(self, promotion_id: uuid.UUID) -> Promotion | None:
        result = await self._session.execute(
            select(Promotion).where(Promotion.id == promotion_id)
        )
        return result.scalar_one_or_none()

    async def create_promotion(
        self,
        workspace_id: uuid.UUID,
        shop: Shop,
        *,
        title: str,
        promotion_type: str,
        start_time: str | None = None,
        end_time: str | None = None,
        discount_type: str | None = None,
        discount_value: str | None = None,
        product_ids: list[str] | None = None,
    ) -> Promotion:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)

        body: dict = {
            "title": title,
            "activity_type": promotion_type,
        }
        if start_time:
            body["begin_time"] = start_time
        if end_time:
            body["end_time"] = end_time
        if product_ids:
            body["product_ids"] = product_ids

        resp = await gateway.post(
            "/promotion/202309/activities",
            json_body=body,
        )
        data = resp.get("data", {})
        platform_id = str(data.get("activity_id", ""))

        promotion = Promotion(
            workspace_id=workspace_id,
            shop_id=shop.id,
            platform_activity_id=platform_id,
            promotion_type=promotion_type,
            title=title,
            status="ACTIVE",
            discount_type=discount_type,
            discount_value=discount_value,
            detail_json=data,
        )
        if start_time:
            promotion.start_time = datetime.fromisoformat(start_time)
        if end_time:
            promotion.end_time = datetime.fromisoformat(end_time)

        self._session.add(promotion)
        await self._session.flush()
        return promotion

    async def create_flash_deal(
        self,
        workspace_id: uuid.UUID,
        shop: Shop,
        *,
        title: str,
        product_ids: list[str],
        countdown_duration_hours: int,
        price_rules: list[dict],
        max_quantity: int | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> Promotion:
        if countdown_duration_hours > 72:
            raise ValueError("Flash deal duration cannot exceed 72 hours")
        if countdown_duration_hours < 1:
            raise ValueError("Flash deal duration must be at least 1 hour")

        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)

        body: dict = {
            "title": title,
            "activity_type": "FLASH_DEAL",
            "product_ids": product_ids,
            "countdown_duration": countdown_duration_hours * 3600,
        }
        if max_quantity:
            body["quantity_limit"] = max_quantity
        if start_time:
            body["begin_time"] = start_time
        if end_time:
            body["end_time"] = end_time
        if price_rules:
            body["product_prices"] = price_rules

        resp = await gateway.post(
            "/promotion/202309/activities",
            json_body=body,
        )
        data = resp.get("data", {})
        platform_id = str(data.get("activity_id", ""))

        promotion = Promotion(
            workspace_id=workspace_id,
            shop_id=shop.id,
            platform_activity_id=platform_id,
            promotion_type="FLASH_DEAL",
            title=title,
            status="ACTIVE",
            countdown_duration_hours=countdown_duration_hours,
            max_quantity=max_quantity,
            price_rules=price_rules,
            product_count=len(product_ids),
            detail_json=data,
        )
        if start_time:
            promotion.start_time = datetime.fromisoformat(start_time)
        if end_time:
            promotion.end_time = datetime.fromisoformat(end_time)

        self._session.add(promotion)
        await self._session.flush()
        return promotion

    async def update_promotion(
        self,
        promotion: Promotion,
        shop: Shop,
        *,
        title: str | None = None,
        discount_value: str | None = None,
    ) -> Promotion:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)

        body: dict = {"activity_id": promotion.platform_activity_id}
        if title:
            body["title"] = title
            promotion.title = title
        if discount_value:
            promotion.discount_value = discount_value

        await gateway.post(
            "/promotion/202309/activities/update",
            json_body=body,
        )
        return promotion

    async def deactivate_promotion(self, promotion: Promotion, shop: Shop) -> Promotion:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)

        await gateway.post(
            "/promotion/202309/activities/deactivate",
            json_body={"activity_id": promotion.platform_activity_id},
        )
        promotion.status = "INACTIVE"
        return promotion

    async def sync_promotions(self, shop: Shop) -> int:
        shop_service = ShopService(self._session)
        gateway = await shop_service.build_gateway_for_shop(shop)
        synced = 0

        resp = await gateway.get(
            "/promotion/202309/activities",
            params={"page_size": "50"},
        )
        data = resp.get("data", {})
        activities = data.get("activities", [])

        for activity_data in activities:
            await self._upsert_promotion(shop, activity_data)
            synced += 1

        return synced

    async def _upsert_promotion(self, shop: Shop, activity_data: dict) -> Promotion:
        platform_id = str(activity_data.get("activity_id", ""))
        result = await self._session.execute(
            select(Promotion).where(Promotion.platform_activity_id == platform_id)
        )
        promotion = result.scalar_one_or_none()

        title = activity_data.get("title", "")
        promo_type = activity_data.get("activity_type", "")
        promo_status = activity_data.get("status", "ACTIVE")

        if promotion:
            promotion.title = title
            promotion.promotion_type = promo_type
            promotion.status = promo_status
            promotion.detail_json = activity_data
        else:
            promotion = Promotion(
                workspace_id=shop.workspace_id,
                shop_id=shop.id,
                platform_activity_id=platform_id,
                promotion_type=promo_type,
                title=title,
                status=promo_status,
                detail_json=activity_data,
            )
            self._session.add(promotion)
            await self._session.flush()

        return promotion

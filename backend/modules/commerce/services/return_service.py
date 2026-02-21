import json
import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.commerce import (
    Order,
    ReturnRequest,
    ReturnStatus,
    ReturnType,
    Shop,
)
from backend.modules.commerce.services.shop_service import ShopService
from backend.tiktok.rate_limiter import get_redis
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)

_RETURN_TYPE_MAP: dict[str, ReturnType] = {
    "RETURN_AND_REFUND": ReturnType.RETURN_AND_REFUND,
    "REFUND_ONLY": ReturnType.REFUND_ONLY,
}

_RETURN_STATUS_MAP: dict[str, ReturnStatus] = {
    "PENDING": ReturnStatus.PENDING,
    "APPROVED": ReturnStatus.APPROVED,
    "REJECTED": ReturnStatus.REJECTED,
    "BUYER_SHIPPED": ReturnStatus.BUYER_SHIPPED,
    "SELLER_RECEIVED": ReturnStatus.SELLER_RECEIVED,
    "REFUNDED": ReturnStatus.REFUNDED,
    "CLOSED": ReturnStatus.CLOSED,
}


class ReturnService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_returns(
        self,
        workspace_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[ReturnRequest]:
        query = select(ReturnRequest).where(
            ReturnRequest.workspace_id == workspace_id
        )
        count_query = select(func.count(ReturnRequest.id)).where(
            ReturnRequest.workspace_id == workspace_id
        )

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(ReturnRequest.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(
            items=items, total=total, page=page, page_size=page_size
        )

    async def approve_return(
        self, return_id: uuid.UUID, *, reason: str | None = None
    ) -> ReturnRequest | None:
        result = await self._session.execute(
            select(ReturnRequest).where(ReturnRequest.id == return_id)
        )
        ret = result.scalar_one_or_none()
        if not ret:
            return None

        # Call TikTok API to approve
        order = await self._get_order(ret.order_id)
        if order:
            shop = await self._get_shop(order.shop_id)
            if shop:
                try:
                    shop_service = ShopService(self._session)
                    gateway = await shop_service.build_gateway_for_shop(shop)
                    await gateway.post(
                        f"/return_refund/202309/returns/{ret.platform_return_id}/approve",
                    )
                except Exception:
                    logger.exception("Failed to approve return on TikTok API")
                    raise

        ret.status = ReturnStatus.APPROVED
        await self._publish_return_update(ret)
        return ret

    async def reject_return(
        self, return_id: uuid.UUID, *, reason: str | None = None
    ) -> ReturnRequest | None:
        result = await self._session.execute(
            select(ReturnRequest).where(ReturnRequest.id == return_id)
        )
        ret = result.scalar_one_or_none()
        if not ret:
            return None

        order = await self._get_order(ret.order_id)
        if order:
            shop = await self._get_shop(order.shop_id)
            if shop:
                try:
                    shop_service = ShopService(self._session)
                    gateway = await shop_service.build_gateway_for_shop(shop)
                    body: dict = {}
                    if reason:
                        body["reject_reason"] = reason
                    await gateway.post(
                        f"/return_refund/202309/returns/{ret.platform_return_id}/reject",
                        json_body=body if body else None,
                    )
                except Exception:
                    logger.exception("Failed to reject return on TikTok API")
                    raise

        ret.status = ReturnStatus.REJECTED
        await self._publish_return_update(ret)
        return ret

    async def upsert_return_from_webhook(
        self, payload: dict
    ) -> ReturnRequest | None:
        """Create or update a return request from a webhook payload."""
        platform_return_id = str(payload.get("return_id", ""))
        if not platform_return_id:
            return None

        result = await self._session.execute(
            select(ReturnRequest).where(
                ReturnRequest.platform_return_id == platform_return_id
            )
        )
        ret = result.scalar_one_or_none()

        raw_status = payload.get("status", "PENDING")
        new_status = _RETURN_STATUS_MAP.get(raw_status, ReturnStatus.PENDING)
        raw_type = payload.get("return_type", "RETURN_AND_REFUND")
        return_type = _RETURN_TYPE_MAP.get(raw_type, ReturnType.RETURN_AND_REFUND)

        if ret:
            ret.status = new_status
            ret.reason = payload.get("reason", ret.reason)
            ret.refund_amount = payload.get("refund_amount", ret.refund_amount)
        else:
            # Need to find the order
            platform_order_id = str(payload.get("order_id", ""))
            order_result = await self._session.execute(
                select(Order).where(
                    Order.platform_order_id == platform_order_id
                )
            )
            order = order_result.scalar_one_or_none()
            if not order:
                logger.warning(
                    "Return webhook for unknown order %s", platform_order_id
                )
                return None

            ret = ReturnRequest(
                workspace_id=order.workspace_id,
                order_id=order.id,
                platform_return_id=platform_return_id,
                return_type=return_type,
                status=new_status,
                reason=payload.get("reason"),
                refund_amount=payload.get("refund_amount"),
            )
            self._session.add(ret)
            await self._session.flush()

        await self._publish_return_update(ret)
        return ret

    async def _get_gateway(self, shop_id: uuid.UUID):
        """Build a PlatformGateway scoped to the given shop."""
        shop_service = ShopService(self._session)
        shop = await shop_service.get_shop(shop_id)
        if not shop:
            raise ValueError(f"Shop {shop_id} not found")
        return await shop_service.build_gateway_for_shop(shop)

    async def create_return(
        self,
        shop_id: uuid.UUID,
        order_id: str,
        return_type: str,
        reason: str,
    ) -> dict:
        """Create a new return request via the TikTok API."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            "/return_refund/202309/returns",
            json_body={
                "order_id": order_id,
                "return_type": return_type,
                "reason": reason,
            },
        )
        return resp.get("data", {})

    async def search_returns(
        self, shop_id: uuid.UUID, **filters: object
    ) -> list[dict]:
        """Search returns via the TikTok API with optional filters."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            "/return_refund/202309/returns/search",
            json_body=filters or {},
        )
        return resp.get("data", {}).get("returns", [])

    async def get_return_records(
        self, shop_id: uuid.UUID, return_id: str
    ) -> list[dict]:
        """Get return records for a specific return."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get(
            f"/return_refund/202309/returns/{return_id}/records"
        )
        return resp.get("data", {}).get("records", [])

    async def get_reject_reasons(self, shop_id: uuid.UUID) -> list[dict]:
        """Get available reject reasons for a shop."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.get("/return_refund/202309/reject_reasons")
        return resp.get("data", {}).get("reasons", [])

    async def calculate_refund(
        self,
        shop_id: uuid.UUID,
        order_id: str,
        items: list[dict],
    ) -> dict:
        """Calculate refund amount for given order items."""
        gateway = await self._get_gateway(shop_id)
        resp = await gateway.post(
            "/return_refund/202309/refund/calculate",
            json_body={"order_id": order_id, "items": items},
        )
        return resp.get("data", {})

    async def _get_order(self, order_id: uuid.UUID) -> Order | None:
        result = await self._session.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def _get_shop(self, shop_id: uuid.UUID) -> Shop | None:
        result = await self._session.execute(
            select(Shop).where(Shop.id == shop_id)
        )
        return result.scalar_one_or_none()

    async def _publish_return_update(self, ret: ReturnRequest) -> None:
        try:
            r = await get_redis()
            message = json.dumps(
                {
                    "type": "return_status_change",
                    "return_id": str(ret.id),
                    "platform_return_id": ret.platform_return_id,
                    "status": ret.status.value,
                }
            )
            await r.publish(
                f"commerce:ws:{ret.workspace_id}", message
            )
        except Exception:
            logger.exception("Failed to publish return update to Redis")

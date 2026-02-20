import logging
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount, Campaign
from backend.db.models.commerce import Order, Product
from backend.db.models.content import Video
from backend.db.models.creators import CreatorProfile
from backend.db.models.platform import ConnectedAccount

logger = logging.getLogger(__name__)


class UnifiedAnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_overview_kpis(
        self, workspace_id: uuid.UUID, *, days: int = 30
    ) -> dict:
        """Aggregate KPIs across all platforms."""
        since = datetime.now(tz=UTC) - timedelta(days=days)

        # Commerce KPIs
        order_stats = await self._session.execute(
            select(
                func.count(Order.id),
                func.coalesce(func.sum(func.cast(Order.total_amount, func.numeric())), 0),
            ).where(
                Order.workspace_id == workspace_id,
                Order.created_at >= since,
            )
        )
        row = order_stats.one()
        total_orders = row[0]
        total_revenue = float(row[1])

        # Product count
        product_count = (
            await self._session.execute(
                select(func.count(Product.id)).where(
                    Product.workspace_id == workspace_id
                )
            )
        ).scalar_one()

        # Ad account count
        ad_account_count = (
            await self._session.execute(
                select(func.count(AdAccount.id)).where(
                    AdAccount.workspace_id == workspace_id
                )
            )
        ).scalar_one()

        # Campaign count
        active_campaigns = (
            await self._session.execute(
                select(func.count(Campaign.id)).where(
                    Campaign.workspace_id == workspace_id,
                    Campaign.operation_status == "ENABLE",
                )
            )
        ).scalar_one()

        # Video count + total views
        video_stats = await self._session.execute(
            select(
                func.count(Video.id),
                func.coalesce(func.sum(Video.view_count), 0),
            ).where(Video.workspace_id == workspace_id)
        )
        v_row = video_stats.one()
        total_videos = v_row[0]
        total_views = int(v_row[1])

        # Creator count
        creator_count = (
            await self._session.execute(
                select(func.count(CreatorProfile.id)).where(
                    CreatorProfile.workspace_id == workspace_id
                )
            )
        ).scalar_one()

        return {
            "total_revenue": f"{total_revenue:.2f}",
            "total_orders": total_orders,
            "average_order_value": f"{total_revenue / total_orders:.2f}" if total_orders > 0 else "0.00",
            "product_count": product_count,
            "ad_account_count": ad_account_count,
            "active_campaigns": active_campaigns,
            "total_videos": total_videos,
            "total_views": total_views,
            "creator_count": creator_count,
            "period_days": days,
        }

    async def get_revenue_vs_spend(
        self, workspace_id: uuid.UUID, *, days: int = 30
    ) -> list[dict]:
        """Timeseries of commerce revenue (daily aggregation)."""
        since = datetime.now(tz=UTC) - timedelta(days=days)

        result = await self._session.execute(
            select(
                func.date_trunc("day", Order.created_at).label("day"),
                func.count(Order.id).label("order_count"),
                func.coalesce(
                    func.sum(func.cast(Order.total_amount, func.numeric())), 0
                ).label("revenue"),
            )
            .where(
                Order.workspace_id == workspace_id,
                Order.created_at >= since,
            )
            .group_by("day")
            .order_by("day")
        )
        rows = result.all()

        return [
            {
                "date": row.day.strftime("%Y-%m-%d") if row.day else "",
                "revenue": f"{float(row.revenue):.2f}",
                "order_count": row.order_count,
            }
            for row in rows
        ]

    async def get_content_performance(
        self, workspace_id: uuid.UUID
    ) -> list[dict]:
        """Video performance: top videos by views."""
        result = await self._session.execute(
            select(Video)
            .where(Video.workspace_id == workspace_id)
            .order_by(Video.view_count.desc())
            .limit(20)
        )
        videos = result.scalars().all()

        return [
            {
                "video_id": str(v.id),
                "title": v.title or "",
                "views": v.view_count,
                "likes": v.like_count,
                "comments": v.comment_count,
                "shares": v.share_count,
                "engagement_rate": round(
                    (v.like_count + v.comment_count + v.share_count) / max(v.view_count, 1) * 100,
                    2,
                ),
            }
            for v in videos
        ]

    async def get_platform_health(
        self, workspace_id: uuid.UUID
    ) -> list[dict]:
        """Check status of all connected platform accounts."""
        result = await self._session.execute(
            select(ConnectedAccount)
            .where(ConnectedAccount.workspace_id == workspace_id)
            .order_by(ConnectedAccount.platform)
        )
        accounts = result.scalars().all()

        return [
            {
                "id": str(a.id),
                "platform": a.platform.value,
                "account_name": a.platform_account_name or a.platform_account_id,
                "status": a.status.value,
                "connected_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in accounts
        ]

    async def get_top_performers(
        self, workspace_id: uuid.UUID, *, limit: int = 5
    ) -> dict:
        """Top products, videos, and campaigns."""
        # Top products by order count — simple approach
        top_products = await self._session.execute(
            select(Product)
            .where(Product.workspace_id == workspace_id)
            .order_by(Product.updated_at.desc())
            .limit(limit)
        )
        products = [
            {
                "id": str(p.id),
                "title": p.title,
                "status": p.status.value if hasattr(p.status, "value") else p.status,
                "image_url": p.main_image_url,
            }
            for p in top_products.scalars().all()
        ]

        # Top videos by views
        top_videos = await self._session.execute(
            select(Video)
            .where(Video.workspace_id == workspace_id)
            .order_by(Video.view_count.desc())
            .limit(limit)
        )
        videos = [
            {
                "id": str(v.id),
                "title": v.title or "",
                "views": v.view_count,
                "likes": v.like_count,
            }
            for v in top_videos.scalars().all()
        ]

        # Top campaigns
        top_campaigns = await self._session.execute(
            select(Campaign)
            .where(
                Campaign.workspace_id == workspace_id,
                Campaign.operation_status == "ENABLE",
            )
            .order_by(Campaign.updated_at.desc())
            .limit(limit)
        )
        campaigns = [
            {
                "id": str(c.id),
                "name": c.campaign_name,
                "objective": c.objective_type,
                "budget": c.budget,
            }
            for c in top_campaigns.scalars().all()
        ]

        return {
            "top_products": products,
            "top_videos": videos,
            "top_campaigns": campaigns,
        }

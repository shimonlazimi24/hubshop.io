import logging
import uuid
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import Campaign
from backend.db.models.analytics import UnifiedKpiSnapshot
from backend.db.models.commerce import Order
from backend.db.models.content import Video
from backend.db.models.creators import CreatorProfile

logger = logging.getLogger(__name__)


class KpiService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_overview(self, workspace_id: uuid.UUID) -> dict:
        """Get current KPI overview aggregated from all modules."""
        order_count = (
            await self._session.execute(
                select(func.count(Order.id)).where(Order.workspace_id == workspace_id)
            )
        ).scalar_one()

        campaign_count = (
            await self._session.execute(
                select(func.count(Campaign.id)).where(
                    Campaign.workspace_id == workspace_id,
                    Campaign.operation_status == "ENABLE",
                )
            )
        ).scalar_one()

        video_count = (
            await self._session.execute(
                select(func.count(Video.id)).where(Video.workspace_id == workspace_id)
            )
        ).scalar_one()

        total_views = (
            await self._session.execute(
                select(func.coalesce(func.sum(Video.view_count), 0)).where(
                    Video.workspace_id == workspace_id
                )
            )
        ).scalar_one()

        saved_creators = (
            await self._session.execute(
                select(func.count(CreatorProfile.id)).where(
                    CreatorProfile.workspace_id == workspace_id,
                    CreatorProfile.is_saved.is_(True),
                )
            )
        ).scalar_one()

        return {
            "total_orders": order_count,
            "active_campaigns": campaign_count,
            "total_videos": video_count,
            "total_views": int(total_views),
            "saved_creators": saved_creators,
        }

    async def get_timeseries(
        self, workspace_id: uuid.UUID, *, days: int = 30
    ) -> list[dict]:
        """Get KPI timeseries from snapshots."""
        from_date = date.today() - timedelta(days=days)
        result = await self._session.execute(
            select(UnifiedKpiSnapshot)
            .where(
                UnifiedKpiSnapshot.workspace_id == workspace_id,
                UnifiedKpiSnapshot.date >= from_date,
            )
            .order_by(UnifiedKpiSnapshot.date.asc())
        )
        snapshots = result.scalars().all()
        return [
            {
                "date": str(s.date),
                "total_orders": s.total_orders,
                "total_revenue": s.total_revenue,
                "active_campaigns": s.active_campaigns,
                "total_views": s.total_views,
            }
            for s in snapshots
        ]

    async def take_snapshot(self, workspace_id: uuid.UUID) -> UnifiedKpiSnapshot:
        """Take a daily KPI snapshot for the workspace."""
        overview = await self.get_overview(workspace_id)
        today = date.today()

        result = await self._session.execute(
            select(UnifiedKpiSnapshot).where(
                UnifiedKpiSnapshot.workspace_id == workspace_id,
                UnifiedKpiSnapshot.date == today,
            )
        )
        snapshot = result.scalar_one_or_none()

        if snapshot:
            snapshot.total_orders = overview["total_orders"]
            snapshot.active_campaigns = overview["active_campaigns"]
            snapshot.total_videos = overview["total_videos"]
            snapshot.total_views = overview["total_views"]
            snapshot.saved_creators = overview["saved_creators"]
        else:
            snapshot = UnifiedKpiSnapshot(
                workspace_id=workspace_id,
                date=today,
                total_orders=overview["total_orders"],
                active_campaigns=overview["active_campaigns"],
                total_videos=overview["total_videos"],
                total_views=overview["total_views"],
                saved_creators=overview["saved_creators"],
            )
            self._session.add(snapshot)
            await self._session.flush()

        return snapshot

    async def get_drill_down(self, workspace_id: uuid.UUID, module: str) -> dict:
        """Get detailed KPIs for a specific module."""
        if module == "commerce":
            order_count = (
                await self._session.execute(
                    select(func.count(Order.id)).where(
                        Order.workspace_id == workspace_id
                    )
                )
            ).scalar_one()
            return {"module": "commerce", "stats": {"total_orders": order_count}}
        elif module == "advertising":
            campaign_count = (
                await self._session.execute(
                    select(func.count(Campaign.id)).where(
                        Campaign.workspace_id == workspace_id
                    )
                )
            ).scalar_one()
            return {
                "module": "advertising",
                "stats": {"total_campaigns": campaign_count},
            }
        elif module == "content":
            video_count = (
                await self._session.execute(
                    select(func.count(Video.id)).where(
                        Video.workspace_id == workspace_id
                    )
                )
            ).scalar_one()
            return {"module": "content", "stats": {"total_videos": video_count}}
        elif module == "creators":
            creator_count = (
                await self._session.execute(
                    select(func.count(CreatorProfile.id)).where(
                        CreatorProfile.workspace_id == workspace_id
                    )
                )
            ).scalar_one()
            return {"module": "creators", "stats": {"total_creators": creator_count}}
        return {"module": module, "stats": {}}

"""Competitor tracking service - tracks and analyzes competitor content."""

import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.intelligence import CompetitorContent, CompetitorTracker

logger = logging.getLogger(__name__)


class CompetitorService:
    """Tracks and analyzes competitor content using Research API."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_competitor(
        self,
        workspace_id: uuid.UUID,
        tiktok_username: str,
        research_client: Any,
    ) -> dict[str, Any]:
        """Add a competitor to track, fetch profile via research API.

        Returns the created tracker as a dict.
        """
        user_resp = await research_client.query_user_info(tiktok_username)
        user_data = user_resp.get("data", {})

        tracker = CompetitorTracker(
            workspace_id=workspace_id,
            username=tiktok_username,
            display_name=user_data.get("display_name"),
            platform_user_id=user_data.get("user_id"),
            profile_data=user_data,
            last_synced_at=datetime.now(tz=UTC),
        )
        self._session.add(tracker)
        await self._session.flush()

        logger.info(
            "Added competitor %s for workspace %s", tiktok_username, workspace_id
        )
        return {
            "id": str(tracker.id),
            "username": tracker.username,
            "display_name": tracker.display_name,
            "profile_data": tracker.profile_data,
            "last_synced_at": (
                tracker.last_synced_at.isoformat() if tracker.last_synced_at else None
            ),
        }

    async def remove_competitor(
        self,
        workspace_id: uuid.UUID,
        competitor_id: uuid.UUID,
    ) -> bool:
        """Remove competitor tracking. Returns True if deleted."""
        result = await self._session.execute(
            select(CompetitorTracker).where(
                CompetitorTracker.id == competitor_id,
                CompetitorTracker.workspace_id == workspace_id,
            )
        )
        tracker = result.scalar_one_or_none()
        if not tracker:
            return False
        await self._session.delete(tracker)
        await self._session.flush()
        logger.info("Removed competitor %s", competitor_id)
        return True

    async def list_competitors(
        self,
        workspace_id: uuid.UUID,
    ) -> list[dict[str, Any]]:
        """List all tracked competitors for a workspace."""
        result = await self._session.execute(
            select(CompetitorTracker)
            .where(CompetitorTracker.workspace_id == workspace_id)
            .order_by(CompetitorTracker.created_at.desc())
        )
        trackers = result.scalars().all()
        return [
            {
                "id": str(t.id),
                "username": t.username,
                "display_name": t.display_name,
                "profile_data": t.profile_data,
                "last_synced_at": (
                    t.last_synced_at.isoformat() if t.last_synced_at else None
                ),
            }
            for t in trackers
        ]

    async def sync_all_competitors(
        self,
        workspace_id: uuid.UUID,
        research_client: Any,
    ) -> int:
        """Sync content for all tracked competitors.

        Returns total number of content items synced.
        """
        result = await self._session.execute(
            select(CompetitorTracker).where(
                CompetitorTracker.workspace_id == workspace_id
            )
        )
        trackers = result.scalars().all()

        now = datetime.now(tz=UTC)
        end_date = now.strftime("%Y%m%d")
        start_date = (now - timedelta(days=30)).strftime("%Y%m%d")

        total_synced = 0
        for tracker in trackers:
            video_resp = await research_client.query_videos(
                username=tracker.username,
                start_date=start_date,
                end_date=end_date,
                max_count=50,
            )
            videos = video_resp.get("data", {}).get("videos", [])

            for video in videos:
                video_id = str(video.get("id", ""))
                # Check if content already exists
                existing = await self._session.execute(
                    select(CompetitorContent).where(
                        CompetitorContent.tracker_id == tracker.id,
                        CompetitorContent.video_id == video_id,
                    )
                )
                content = existing.scalar_one_or_none()

                metrics = {
                    "like_count": video.get("like_count", 0),
                    "comment_count": video.get("comment_count", 0),
                    "share_count": video.get("share_count", 0),
                    "view_count": video.get("view_count", 0),
                }

                if content:
                    content.metrics = metrics
                    content.description = video.get("video_description")
                    content.hashtags = video.get("hashtag_names")
                else:
                    content = CompetitorContent(
                        tracker_id=tracker.id,
                        video_id=video_id,
                        description=video.get("video_description"),
                        metrics=metrics,
                        hashtags=video.get("hashtag_names"),
                        published_at=(
                            datetime.fromtimestamp(video["create_time"], tz=UTC)
                            if video.get("create_time")
                            else None
                        ),
                    )
                    self._session.add(content)
                    total_synced += 1

            tracker.last_synced_at = now

        await self._session.flush()
        logger.info(
            "Synced %d content items across %d competitors for workspace %s",
            total_synced,
            len(trackers),
            workspace_id,
        )
        return total_synced

    async def get_competitor_detail(
        self,
        workspace_id: uuid.UUID,
        competitor_id: uuid.UUID,
    ) -> dict[str, Any] | None:
        """Get competitor with latest content."""
        result = await self._session.execute(
            select(CompetitorTracker).where(
                CompetitorTracker.id == competitor_id,
                CompetitorTracker.workspace_id == workspace_id,
            )
        )
        tracker = result.scalar_one_or_none()
        if not tracker:
            return None

        content_result = await self._session.execute(
            select(CompetitorContent)
            .where(CompetitorContent.tracker_id == tracker.id)
            .order_by(CompetitorContent.published_at.desc())
            .limit(20)
        )
        content_items = content_result.scalars().all()

        return {
            "id": str(tracker.id),
            "username": tracker.username,
            "display_name": tracker.display_name,
            "profile_data": tracker.profile_data,
            "last_synced_at": (
                tracker.last_synced_at.isoformat() if tracker.last_synced_at else None
            ),
            "content": [
                {
                    "id": str(c.id),
                    "video_id": c.video_id,
                    "description": c.description,
                    "metrics": c.metrics,
                    "hashtags": c.hashtags,
                    "published_at": (
                        c.published_at.isoformat() if c.published_at else None
                    ),
                }
                for c in content_items
            ],
        }

    async def compare_competitors(
        self,
        workspace_id: uuid.UUID,
        competitor_ids: list[uuid.UUID],
    ) -> list[dict[str, Any]]:
        """Compare metrics across multiple competitors.

        Returns a list of competitor summaries with aggregated metrics.
        """
        comparisons: list[dict[str, Any]] = []

        for comp_id in competitor_ids:
            result = await self._session.execute(
                select(CompetitorTracker).where(
                    CompetitorTracker.id == comp_id,
                    CompetitorTracker.workspace_id == workspace_id,
                )
            )
            tracker = result.scalar_one_or_none()
            if not tracker:
                continue

            content_result = await self._session.execute(
                select(CompetitorContent).where(
                    CompetitorContent.tracker_id == tracker.id
                )
            )
            content_items = content_result.scalars().all()

            total_likes = sum(c.metrics.get("like_count", 0) for c in content_items)
            total_comments = sum(
                c.metrics.get("comment_count", 0) for c in content_items
            )
            total_shares = sum(c.metrics.get("share_count", 0) for c in content_items)
            total_views = sum(c.metrics.get("view_count", 0) for c in content_items)
            video_count = len(content_items)

            comparisons.append(
                {
                    "id": str(tracker.id),
                    "username": tracker.username,
                    "display_name": tracker.display_name,
                    "video_count": video_count,
                    "total_likes": total_likes,
                    "total_comments": total_comments,
                    "total_shares": total_shares,
                    "total_views": total_views,
                    "avg_engagement": (total_likes + total_comments + total_shares)
                    / max(video_count, 1),
                }
            )

        return comparisons

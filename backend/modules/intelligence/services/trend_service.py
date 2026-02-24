"""Trend analysis service - fetches and queries trending content."""

import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.intelligence import TrendSnapshot, TrendType

logger = logging.getLogger(__name__)


class TrendService:
    """Analyzes trending hashtags, sounds, and products from Research API."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def sync_trends(
        self,
        workspace_id: uuid.UUID,
        research_client: Any,
    ) -> int:
        """Fetch trending hashtags via research API and upsert into DB.

        Queries the Research API for popular videos, extracts hashtag names,
        and creates TrendSnapshot records scored by total engagement.

        Returns the number of trend snapshots created.
        """
        now = datetime.now(tz=UTC)
        end_date = now.strftime("%Y%m%d")
        start_date = (now - timedelta(days=7)).strftime("%Y%m%d")

        response = await research_client.query_videos(
            keyword="trending",
            start_date=start_date,
            end_date=end_date,
            max_count=100,
        )

        videos = response.get("data", {}).get("videos", [])
        hashtag_scores: dict[str, float] = {}

        for video in videos:
            hashtag_names = video.get("hashtag_names", []) or []
            engagement = (
                video.get("like_count", 0)
                + video.get("comment_count", 0)
                + video.get("share_count", 0)
                + video.get("view_count", 0)
            )
            for tag in hashtag_names:
                hashtag_scores[tag] = hashtag_scores.get(tag, 0) + engagement

        created = 0
        for name, score in hashtag_scores.items():
            snapshot = TrendSnapshot(
                workspace_id=workspace_id,
                trend_type=TrendType.HASHTAG.value,
                name=name,
                engagement_score=score,
                captured_at=now,
            )
            self._session.add(snapshot)
            created += 1

        await self._session.flush()
        logger.info("Synced %d hashtag trends for workspace %s", created, workspace_id)
        return created

    async def get_trending_hashtags(
        self,
        workspace_id: uuid.UUID,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Return latest trending hashtags ordered by engagement score."""
        result = await self._session.execute(
            select(TrendSnapshot)
            .where(
                TrendSnapshot.workspace_id == workspace_id,
                TrendSnapshot.trend_type == TrendType.HASHTAG.value,
            )
            .order_by(
                TrendSnapshot.captured_at.desc(), TrendSnapshot.engagement_score.desc()
            )
            .limit(limit)
        )
        snapshots = result.scalars().all()
        return [
            {
                "id": str(s.id),
                "name": s.name,
                "engagement_score": s.engagement_score,
                "region": s.region,
                "captured_at": s.captured_at.isoformat() if s.captured_at else None,
                "metadata": s.metadata_json,
            }
            for s in snapshots
        ]

    async def get_trending_sounds(
        self,
        workspace_id: uuid.UUID,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Return latest trending sounds ordered by engagement score."""
        result = await self._session.execute(
            select(TrendSnapshot)
            .where(
                TrendSnapshot.workspace_id == workspace_id,
                TrendSnapshot.trend_type == TrendType.SOUND.value,
            )
            .order_by(
                TrendSnapshot.captured_at.desc(), TrendSnapshot.engagement_score.desc()
            )
            .limit(limit)
        )
        snapshots = result.scalars().all()
        return [
            {
                "id": str(s.id),
                "name": s.name,
                "engagement_score": s.engagement_score,
                "region": s.region,
                "captured_at": s.captured_at.isoformat() if s.captured_at else None,
                "metadata": s.metadata_json,
            }
            for s in snapshots
        ]

    async def get_trend_history(
        self,
        workspace_id: uuid.UUID,
        hashtag: str,
        days: int = 30,
    ) -> list[dict[str, Any]]:
        """Return time-series data for a specific hashtag over the given days."""
        cutoff = datetime.now(tz=UTC) - timedelta(days=days)
        result = await self._session.execute(
            select(TrendSnapshot)
            .where(
                TrendSnapshot.workspace_id == workspace_id,
                TrendSnapshot.trend_type == TrendType.HASHTAG.value,
                TrendSnapshot.name == hashtag,
                TrendSnapshot.captured_at >= cutoff,
            )
            .order_by(TrendSnapshot.captured_at.asc())
        )
        snapshots = result.scalars().all()
        return [
            {
                "date": s.captured_at.isoformat() if s.captured_at else None,
                "engagement_score": s.engagement_score,
            }
            for s in snapshots
        ]

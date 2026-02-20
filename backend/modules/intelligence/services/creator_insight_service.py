"""Creator insight service - discovers and analyzes creators via Research API."""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.intelligence import ResearchQuery

logger = logging.getLogger(__name__)


class CreatorInsightService:
    """Discovers and analyzes creators using the Research API."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def discover_creators(
        self,
        workspace_id: uuid.UUID,
        research_client: Any,
        *,
        keyword: str | None = None,
        hashtag: str | None = None,
        min_followers: int = 0,
        max_count: int = 50,
    ) -> list[dict[str, Any]]:
        """Search creators via research API based on filters.

        Queries videos matching the given criteria and extracts unique
        creator usernames with aggregated engagement metrics.
        """
        now = datetime.now(tz=timezone.utc)
        end_date = now.strftime("%Y%m%d")
        start_date = (now - timedelta(days=30)).strftime("%Y%m%d")

        response = await research_client.query_videos(
            keyword=keyword,
            hashtag_name=hashtag,
            start_date=start_date,
            end_date=end_date,
            max_count=max_count,
        )

        videos = response.get("data", {}).get("videos", [])
        creator_map: dict[str, dict[str, Any]] = {}

        for video in videos:
            username = video.get("username")
            if not username:
                continue

            if username not in creator_map:
                creator_map[username] = {
                    "username": username,
                    "video_count": 0,
                    "total_likes": 0,
                    "total_comments": 0,
                    "total_shares": 0,
                    "total_views": 0,
                }

            entry = creator_map[username]
            entry["video_count"] += 1
            entry["total_likes"] += video.get("like_count", 0)
            entry["total_comments"] += video.get("comment_count", 0)
            entry["total_shares"] += video.get("share_count", 0)
            entry["total_views"] += video.get("view_count", 0)

        creators = list(creator_map.values())

        # Enrich with profile data where possible
        for creator in creators:
            total_engagement = (
                creator["total_likes"]
                + creator["total_comments"]
                + creator["total_shares"]
            )
            creator["avg_engagement"] = total_engagement / max(
                creator["video_count"], 1
            )

        # Sort by avg_engagement descending
        creators.sort(key=lambda c: c["avg_engagement"], reverse=True)

        logger.info(
            "Discovered %d creators for workspace %s", len(creators), workspace_id
        )
        return creators

    async def get_creator_insight(
        self,
        workspace_id: uuid.UUID,
        creator_username: str,
        research_client: Any,
    ) -> dict[str, Any]:
        """Get detailed creator analytics by fetching profile and recent videos."""
        user_resp = await research_client.query_user_info(creator_username)
        user_data = user_resp.get("data", {})

        now = datetime.now(tz=timezone.utc)
        end_date = now.strftime("%Y%m%d")
        start_date = (now - timedelta(days=30)).strftime("%Y%m%d")

        videos_resp = await research_client.query_videos(
            username=creator_username,
            start_date=start_date,
            end_date=end_date,
            max_count=50,
        )
        videos = videos_resp.get("data", {}).get("videos", [])

        total_likes = sum(v.get("like_count", 0) for v in videos)
        total_comments = sum(v.get("comment_count", 0) for v in videos)
        total_shares = sum(v.get("share_count", 0) for v in videos)
        total_views = sum(v.get("view_count", 0) for v in videos)
        video_count = len(videos)

        return {
            "username": creator_username,
            "profile": user_data,
            "video_count": video_count,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "total_views": total_views,
            "avg_engagement": (total_likes + total_comments + total_shares)
            / max(video_count, 1),
        }

    async def save_insight(
        self,
        workspace_id: uuid.UUID,
        creator_data: dict[str, Any],
        user_id: uuid.UUID,
    ) -> dict[str, Any]:
        """Save a creator insight as a ResearchQuery for future reference."""
        query = ResearchQuery(
            workspace_id=workspace_id,
            name=f"Creator Insight: {creator_data.get('username', 'unknown')}",
            query_params=creator_data,
            created_by=user_id,
            last_run_at=datetime.now(tz=timezone.utc),
        )
        self._session.add(query)
        await self._session.flush()

        logger.info(
            "Saved creator insight for %s in workspace %s",
            creator_data.get("username"),
            workspace_id,
        )
        return {
            "id": str(query.id),
            "name": query.name,
            "query_params": query.query_params,
            "last_run_at": query.last_run_at.isoformat()
            if query.last_run_at
            else None,
        }

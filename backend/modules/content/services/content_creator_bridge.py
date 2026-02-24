import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.content import Video
from backend.db.models.creators import ContentAuthorization, CreatorProfile

logger = logging.getLogger(__name__)


class ContentCreatorBridge:
    """Bridge service linking content videos to creator Spark Ads flows."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_video_with_creator(
        self, video_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> dict:
        """Get video details along with associated creator profile."""
        # Get the video
        result = await self._session.execute(
            select(Video).where(
                Video.id == video_id,
                Video.workspace_id == workspace_id,
            )
        )
        video = result.scalar_one_or_none()
        if not video:
            return {}

        # Try to find a creator profile that matches via platform_video_id in authorizations
        creator_data = None
        auth_result = await self._session.execute(
            select(ContentAuthorization).where(
                ContentAuthorization.workspace_id == workspace_id,
                ContentAuthorization.platform_video_id == video.platform_video_id,
            )
        )
        auth = auth_result.scalar_one_or_none()
        if auth:
            creator_result = await self._session.execute(
                select(CreatorProfile).where(
                    CreatorProfile.id == auth.creator_id,
                    CreatorProfile.workspace_id == workspace_id,
                )
            )
            creator = creator_result.scalar_one_or_none()
            if creator:
                creator_data = {
                    "creator_id": str(creator.id),
                    "username": creator.username,
                    "display_name": creator.display_name,
                    "avatar_url": creator.avatar_url,
                    "tier": creator.tier,
                }

        return {
            "video": {
                "video_id": str(video.id),
                "platform_video_id": video.platform_video_id,
                "title": video.title,
                "view_count": video.view_count,
                "like_count": video.like_count,
                "comment_count": video.comment_count,
                "share_count": video.share_count,
            },
            "creator": creator_data,
            "authorization": (
                {
                    "status": auth.status,
                    "authorization_code": auth.authorization_code,
                }
                if auth
                else None
            ),
        }

    async def request_spark_ad_for_video(
        self,
        workspace_id: uuid.UUID,
        video_id: uuid.UUID,
        creator_id: uuid.UUID,
    ) -> ContentAuthorization:
        """Create Spark Ads request for a specific video-creator pair."""
        # Get the video to extract the platform_video_id
        result = await self._session.execute(
            select(Video).where(
                Video.id == video_id,
                Video.workspace_id == workspace_id,
            )
        )
        video = result.scalar_one_or_none()
        if not video:
            raise ValueError(f"Video {video_id} not found")

        # Check for existing pending/approved authorization
        existing_result = await self._session.execute(
            select(ContentAuthorization).where(
                ContentAuthorization.workspace_id == workspace_id,
                ContentAuthorization.creator_id == creator_id,
                ContentAuthorization.platform_video_id == video.platform_video_id,
                ContentAuthorization.status.in_(["PENDING", "APPROVED"]),
            )
        )
        if existing_result.scalar_one_or_none():
            raise ValueError(
                f"Authorization already exists for video {video_id} and creator {creator_id}"
            )

        # Create authorization request
        auth = ContentAuthorization(
            workspace_id=workspace_id,
            creator_id=creator_id,
            platform_video_id=video.platform_video_id,
            status="PENDING",
        )
        self._session.add(auth)
        await self._session.flush()
        return auth

    async def get_creator_content_summary(
        self,
        workspace_id: uuid.UUID,
        creator_id: uuid.UUID,
    ) -> dict:
        """Get summary of a creator's content + authorization status."""
        # Get creator profile
        result = await self._session.execute(
            select(CreatorProfile).where(
                CreatorProfile.id == creator_id,
                CreatorProfile.workspace_id == workspace_id,
            )
        )
        creator = result.scalar_one_or_none()
        if not creator:
            return {}

        # Get all authorizations for this creator
        auth_result = await self._session.execute(
            select(ContentAuthorization).where(
                ContentAuthorization.workspace_id == workspace_id,
                ContentAuthorization.creator_id == creator_id,
            )
        )
        authorizations = list(auth_result.scalars().all())

        total_auths = len(authorizations)
        approved = sum(1 for a in authorizations if a.status == "APPROVED")
        pending = sum(1 for a in authorizations if a.status == "PENDING")

        return {
            "creator": {
                "creator_id": str(creator.id),
                "username": creator.username,
                "display_name": creator.display_name,
                "follower_count": creator.follower_count,
                "tier": creator.tier,
            },
            "authorizations": {
                "total": total_auths,
                "approved": approved,
                "pending": pending,
            },
            "authorized_video_ids": [
                a.platform_video_id
                for a in authorizations
                if a.status == "APPROVED" and a.platform_video_id
            ],
        }

import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.creators import CreatorProfile
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class CreatorProfileService:
    """Service for managing locally-stored creator profiles."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_creators(
        self,
        workspace_id: uuid.UUID,
        *,
        is_saved: bool | None = None,
        tier: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[CreatorProfile]:
        query = select(CreatorProfile).where(
            CreatorProfile.workspace_id == workspace_id
        )
        count_query = select(func.count(CreatorProfile.id)).where(
            CreatorProfile.workspace_id == workspace_id
        )

        if is_saved is not None:
            query = query.where(CreatorProfile.is_saved == is_saved)
            count_query = count_query.where(CreatorProfile.is_saved == is_saved)
        if tier:
            query = query.where(CreatorProfile.tier == tier)
            count_query = count_query.where(CreatorProfile.tier == tier)
        if search:
            pattern = f"%{search}%"
            query = query.where(
                CreatorProfile.display_name.ilike(pattern)
                | CreatorProfile.username.ilike(pattern)
            )
            count_query = count_query.where(
                CreatorProfile.display_name.ilike(pattern)
                | CreatorProfile.username.ilike(pattern)
            )

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(CreatorProfile.follower_count.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(
            items=items, total=total, page=page, page_size=page_size
        )

    async def get_creator(
        self, creator_id: uuid.UUID
    ) -> CreatorProfile | None:
        result = await self._session.execute(
            select(CreatorProfile).where(CreatorProfile.id == creator_id)
        )
        return result.scalar_one_or_none()

    async def save_creator(
        self, creator_id: uuid.UUID, is_saved: bool
    ) -> CreatorProfile | None:
        creator = await self.get_creator(creator_id)
        if creator:
            creator.is_saved = is_saved
        return creator

    async def upsert_creator_from_api(
        self, workspace_id: uuid.UUID, creator_data: dict
    ) -> CreatorProfile:
        """Create or update a creator profile from API response data."""
        platform_creator_id = str(creator_data.get("creator_id", ""))

        result = await self._session.execute(
            select(CreatorProfile).where(
                CreatorProfile.workspace_id == workspace_id,
                CreatorProfile.platform_creator_id == platform_creator_id,
            )
        )
        creator = result.scalar_one_or_none()

        username = creator_data.get("username")
        display_name = creator_data.get("display_name") or creator_data.get("nickname")
        avatar_url = creator_data.get("avatar_url") or creator_data.get("profile_image")
        bio = creator_data.get("bio") or creator_data.get("bio_description")
        follower_count = creator_data.get("follower_count", 0)
        following_count = creator_data.get("following_count", 0)
        likes_count = creator_data.get("likes_count", 0)
        video_count = creator_data.get("video_count", 0)
        engagement_rate = creator_data.get("engagement_rate")
        categories = creator_data.get("categories")
        audience_demographics = creator_data.get("audience_demographics")
        tier = self._compute_tier(follower_count)

        if creator:
            creator.username = username or creator.username
            creator.display_name = display_name or creator.display_name
            creator.avatar_url = avatar_url or creator.avatar_url
            creator.bio = bio or creator.bio
            creator.follower_count = follower_count
            creator.following_count = following_count
            creator.likes_count = likes_count
            creator.video_count = video_count
            creator.engagement_rate = str(engagement_rate) if engagement_rate else creator.engagement_rate
            creator.categories = categories or creator.categories
            creator.audience_demographics = audience_demographics or creator.audience_demographics
            creator.tier = tier
            creator.detail_json = creator_data
        else:
            creator = CreatorProfile(
                workspace_id=workspace_id,
                platform_creator_id=platform_creator_id,
                username=username,
                display_name=display_name,
                avatar_url=avatar_url,
                bio=bio,
                follower_count=follower_count,
                following_count=following_count,
                likes_count=likes_count,
                video_count=video_count,
                tier=tier,
                categories=categories,
                audience_demographics=audience_demographics,
                engagement_rate=str(engagement_rate) if engagement_rate else None,
                is_saved=False,
                detail_json=creator_data,
            )
            self._session.add(creator)
            await self._session.flush()

        return creator

    @staticmethod
    def _compute_tier(follower_count: int) -> str:
        """Compute creator tier based on follower count."""
        if follower_count >= 1_000_000:
            return "MEGA"
        if follower_count >= 500_000:
            return "MACRO"
        if follower_count >= 100_000:
            return "MID"
        if follower_count >= 10_000:
            return "MICRO"
        return "NANO"

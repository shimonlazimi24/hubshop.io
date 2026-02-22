import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.creators import CreatorProfile
from backend.db.models.platform import (
    AccountStatus,
    ConnectedAccount,
    Platform,
    TokenVault,
)
from backend.tiktok.developer.client import TikTokDeveloperClient
from backend.tiktok.gateway import PlatformGateway
from backend.utils.crypto import decrypt_token
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class CreatorService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search_creators(
        self,
        workspace_id: uuid.UUID,
        *,
        search: str | None = None,
        tier: str | None = None,
        is_saved: bool | None = None,
        min_followers: int | None = None,
        max_followers: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[CreatorProfile]:
        query = select(CreatorProfile).where(
            CreatorProfile.workspace_id == workspace_id
        )
        count_query = select(func.count(CreatorProfile.id)).where(
            CreatorProfile.workspace_id == workspace_id
        )

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
        if tier:
            query = query.where(CreatorProfile.tier == tier)
            count_query = count_query.where(CreatorProfile.tier == tier)
        if is_saved is not None:
            query = query.where(CreatorProfile.is_saved == is_saved)
            count_query = count_query.where(CreatorProfile.is_saved == is_saved)
        if min_followers is not None:
            query = query.where(CreatorProfile.follower_count >= min_followers)
            count_query = count_query.where(
                CreatorProfile.follower_count >= min_followers
            )
        if max_followers is not None:
            query = query.where(CreatorProfile.follower_count <= max_followers)
            count_query = count_query.where(
                CreatorProfile.follower_count <= max_followers
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

    async def get_creator(self, creator_id: uuid.UUID) -> CreatorProfile | None:
        result = await self._session.execute(
            select(CreatorProfile).where(CreatorProfile.id == creator_id)
        )
        return result.scalar_one_or_none()

    async def save_creator(
        self, creator_id: uuid.UUID, *, saved: bool = True
    ) -> CreatorProfile | None:
        creator = await self.get_creator(creator_id)
        if creator:
            creator.is_saved = saved
        return creator

    async def get_creator_videos(
        self, workspace_id: uuid.UUID, creator: CreatorProfile
    ) -> list[dict]:
        """Fetch creator's videos via Developer API."""
        _, gateway = await self._get_developer_gateway(workspace_id)

        resp = await gateway.post(
            "/video/list/",
            json_body={"max_count": 20},
            params={
                "fields": "id,title,video_description,cover_image_url,duration,create_time,like_count,comment_count,share_count,view_count"
            },
        )
        return resp.get("data", {}).get("videos", [])

    async def sync_creator_metrics(
        self, creator: CreatorProfile, workspace_id: uuid.UUID
    ) -> CreatorProfile:
        """Refresh creator metrics from Developer API."""
        _, gateway = await self._get_developer_gateway(workspace_id)

        resp = await gateway.get(
            "/research/user/info/",
            params={"username": creator.username or creator.display_name or ""},
        )
        data = resp.get("data", {}).get("user", {})

        if data:
            creator.follower_count = data.get("follower_count", creator.follower_count)
            creator.following_count = data.get("following_count", creator.following_count)
            creator.likes_count = data.get("likes_count", creator.likes_count)
            creator.video_count = data.get("video_count", creator.video_count)
            creator.bio = data.get("bio_description", creator.bio)
            creator.avatar_url = data.get("avatar_url", creator.avatar_url)
            creator.detail_json = data

        return creator

    async def sync_creator_to_workspace(
        self, workspace_id: uuid.UUID, creator_data: dict
    ) -> CreatorProfile:
        """Save a creator from TTCM discovery results into the workspace."""
        from backend.modules.creators.services.creator_profile_service import (
            CreatorProfileService,
        )
        profile_service = CreatorProfileService(self._session)
        return await profile_service.upsert_creator_from_api(workspace_id, creator_data)

    async def get_creator_performance(
        self, creator_id: uuid.UUID
    ) -> dict:
        """Get performance metrics for a saved creator."""
        creator = await self.get_creator(creator_id)
        if not creator:
            return {}

        engagement_rate = float(creator.engagement_rate) if creator.engagement_rate else 0.0
        avg_likes = (
            creator.likes_count / creator.video_count
            if creator.video_count > 0
            else 0.0
        )

        return {
            "creator_id": str(creator.id),
            "username": creator.username,
            "display_name": creator.display_name,
            "follower_count": creator.follower_count,
            "following_count": creator.following_count,
            "likes_count": creator.likes_count,
            "video_count": creator.video_count,
            "tier": creator.tier,
            "engagement_rate": engagement_rate,
            "avg_likes_per_video": round(avg_likes, 2),
        }

    async def _get_developer_gateway(
        self, workspace_id: uuid.UUID
    ) -> tuple[ConnectedAccount, PlatformGateway]:
        result = await self._session.execute(
            select(ConnectedAccount).where(
                ConnectedAccount.workspace_id == workspace_id,
                ConnectedAccount.platform == Platform.DEVELOPER,
                ConnectedAccount.status == AccountStatus.ACTIVE,
            )
        )
        account = result.scalars().first()
        if not account:
            raise ValueError("No active Developer account found")

        result = await self._session.execute(
            select(TokenVault).where(
                TokenVault.connected_account_id == account.id
            )
        )
        vault = result.scalar_one_or_none()
        if not vault:
            raise ValueError(f"No token vault for account {account.id}")

        access_token = decrypt_token(vault.encrypted_access_token)
        client = TikTokDeveloperClient(access_token=access_token)
        gateway = PlatformGateway(
            platform=Platform.DEVELOPER,
            account_id=str(account.id),
            client=client,
        )
        return account, gateway

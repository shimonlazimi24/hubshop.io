import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.platform import Platform, TokenVault
from backend.tiktok.gateway import PlatformGateway
from backend.tiktok.marketing.client import TikTokMarketingClient
from backend.utils.crypto import decrypt_token

logger = logging.getLogger(__name__)


class MentionsService:
    """Service for brand mention monitoring — posts, comments, keywords, hashtags."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _build_gateway(self, connected_account_id: uuid.UUID) -> PlatformGateway:
        """Build a PlatformGateway from the token vault for the given connected account."""
        result = await self._session.execute(
            select(TokenVault).where(
                TokenVault.connected_account_id == connected_account_id
            )
        )
        token = result.scalar_one_or_none()
        if not token:
            raise ValueError("No token found for connected account")

        access_token = decrypt_token(token.encrypted_access_token)
        client = TikTokMarketingClient(access_token=access_token)
        return PlatformGateway(
            platform=Platform.MARKETING,
            account_id=str(connected_account_id),
            client=client,
        )

    async def get_top_mentions(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
    ) -> dict:
        """Get top posts that mention the brand."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.get("/mentions/posts/top/")
        return resp.get("data", {})

    async def get_mention_detail(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        *,
        post_id: str,
    ) -> dict:
        """Get detailed information about a specific mention post."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.get(
            "/mentions/posts/detail/",
            params={"post_id": post_id},
        )
        return resp.get("data", {})

    async def get_frequent_keywords(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
    ) -> dict:
        """Get frequently used keywords in brand mentions."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.get("/mentions/keywords/frequent/")
        return resp.get("data", {})

    async def get_frequent_hashtags(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
    ) -> dict:
        """Get frequently used hashtags in brand mentions."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.get("/mentions/hashtags/frequent/")
        return resp.get("data", {})

    async def get_top_comment_mentions(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
    ) -> dict:
        """Get top comments that mention the brand."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.get("/mentions/comments/top/")
        return resp.get("data", {})

    async def reply_to_mention(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        *,
        comment_id: str,
        text: str,
    ) -> dict:
        """Reply to a brand mention comment."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.post(
            "/mentions/comments/reply/",
            json_body={
                "comment_id": comment_id,
                "text": text,
            },
        )
        return resp.get("data", {})

    async def enable_brand_hashtag(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        *,
        hashtag: str,
    ) -> dict:
        """Enable a brand hashtag for monitoring."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.post(
            "/mentions/brand_hashtag/enable/",
            json_body={"hashtag": hashtag},
        )
        return resp.get("data", {})

    async def list_enabled_hashtags(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
    ) -> dict:
        """List all enabled brand hashtags."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.get("/mentions/brand_hashtag/enabled/")
        return resp.get("data", {})

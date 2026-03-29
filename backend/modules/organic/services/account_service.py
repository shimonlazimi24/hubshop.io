import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.platform import Platform, TokenVault
from backend.tiktok.gateway import PlatformGateway
from backend.tiktok.marketing.client import TikTokMarketingClient
from backend.utils.crypto import decrypt_token

logger = logging.getLogger(__name__)


class OrganicAccountService:
    """Service for organic account operations — profile, posts, publishing, hashtags."""

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

    async def get_profile(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
    ) -> dict:
        """Get the organic account profile."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.get("/business/account/profile/")
        return resp.get("data", {})

    async def get_posts(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List posts for the organic account."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.get(
            "/business/account/posts/",
            params={
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def get_benchmarks(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        *,
        category: str | None = None,
    ) -> dict:
        """Get performance benchmarks for the organic account."""
        gateway = await self._build_gateway(connected_account_id)
        params: dict[str, str] = {}
        if category:
            params["category"] = category
        # NOTE: /business/account/benchmarks/ is undocumented in TikTok's
        # official API docs and may not work in production.
        resp = await gateway.get("/business/account/benchmarks/", params=params or None)
        return resp.get("data", {})

    async def publish_video(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        *,
        video_config: dict,
    ) -> dict:
        """Publish a video to the organic account."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.post(
            "/business/account/posts/video/publish/",
            json_body=video_config,
        )
        return resp.get("data", {})

    async def publish_photo(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        *,
        photo_config: dict,
    ) -> dict:
        """Publish a photo to the organic account."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.post(
            "/business/account/posts/photo/publish/",
            json_body=photo_config,
        )
        return resp.get("data", {})

    async def get_publish_status(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        *,
        publish_id: str,
    ) -> dict:
        """Get the status of a publish operation."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.get(
            "/business/account/posts/status/",
            params={"publish_id": publish_id},
        )
        return resp.get("data", {})

    async def recommend_hashtags(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        *,
        text: str,
    ) -> dict:
        """Get recommended hashtags based on the given text."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.get(
            "/business/account/posts/hashtags/recommend/",
            params={"text": text},
        )
        return resp.get("data", {})

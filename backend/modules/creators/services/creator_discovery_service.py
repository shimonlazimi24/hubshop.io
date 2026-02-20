import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.platform import (
    AccountStatus,
    ConnectedAccount,
    Platform,
    TokenVault,
)
from backend.tiktok.gateway import PlatformGateway
from backend.tiktok.marketing.client import TikTokMarketingClient
from backend.utils.crypto import decrypt_token

logger = logging.getLogger(__name__)


class CreatorDiscoveryService:
    """Service for discovering creators via TikTok Creator Marketplace (TTCM) API."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search_creators(
        self,
        workspace_id: uuid.UUID,
        *,
        query: str | None = None,
        min_followers: int | None = None,
        max_followers: int | None = None,
        categories: list[str] | None = None,
    ) -> list[dict]:
        """Search creators via TTCM API through the marketing gateway.

        Returns raw search results from the API.
        """
        gateway = await self._get_marketing_gateway(workspace_id)

        body: dict = {}
        if query:
            body["keyword"] = query
        if min_followers is not None:
            body["min_follower"] = min_followers
        if max_followers is not None:
            body["max_follower"] = max_followers
        if categories:
            body["creator_category"] = categories

        resp = await gateway.get(
            "/tt_video/creator_marketplace/creator/search/",
            params={k: str(v) for k, v in body.items() if v is not None},
        )
        data = resp.get("data", {})
        return data.get("creators", [])

    async def get_creator_info(
        self, workspace_id: uuid.UUID, creator_username: str
    ) -> dict:
        """Get detailed creator info from TTCM API."""
        gateway = await self._get_marketing_gateway(workspace_id)

        resp = await gateway.get(
            "/tt_video/creator_marketplace/creator/get/",
            params={"creator_username": creator_username},
        )
        return resp.get("data", {})

    async def get_creator_audience(
        self, workspace_id: uuid.UUID, creator_username: str
    ) -> dict:
        """Get audience demographics from TTCM API."""
        gateway = await self._get_marketing_gateway(workspace_id)

        resp = await gateway.get(
            "/tt_video/creator_marketplace/creator/audience/",
            params={"creator_username": creator_username},
        )
        return resp.get("data", {})

    async def _get_marketing_gateway(
        self, workspace_id: uuid.UUID
    ) -> PlatformGateway:
        """Get the first active Marketing account and build a gateway."""
        result = await self._session.execute(
            select(ConnectedAccount).where(
                ConnectedAccount.workspace_id == workspace_id,
                ConnectedAccount.platform == Platform.MARKETING,
                ConnectedAccount.status == AccountStatus.ACTIVE,
            )
        )
        account = result.scalars().first()
        if not account:
            raise ValueError("No active Marketing account found")

        result = await self._session.execute(
            select(TokenVault).where(
                TokenVault.connected_account_id == account.id
            )
        )
        vault = result.scalar_one_or_none()
        if not vault:
            raise ValueError(f"No token vault for account {account.id}")

        access_token = decrypt_token(vault.encrypted_access_token)
        client = TikTokMarketingClient(access_token=access_token)
        return PlatformGateway(
            platform=Platform.MARKETING,
            account_id=str(account.id),
            client=client,
        )

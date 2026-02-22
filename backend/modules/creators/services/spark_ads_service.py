import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.creators import ContentAuthorization
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


class SparkAdsService:
    """Service for Spark Ads content authorization management."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def request_authorization(
        self,
        workspace_id: uuid.UUID,
        creator_id: uuid.UUID,
        platform_video_id: str,
    ) -> ContentAuthorization:
        """Create a pending authorization record for a Spark Ads request."""
        auth = ContentAuthorization(
            workspace_id=workspace_id,
            creator_id=creator_id,
            platform_video_id=platform_video_id,
            status="PENDING",
        )
        self._session.add(auth)
        await self._session.flush()
        return auth

    async def list_authorizations(
        self,
        workspace_id: uuid.UUID,
        *,
        creator_id: uuid.UUID | None = None,
        status_filter: str | None = None,
    ) -> list[ContentAuthorization]:
        query = select(ContentAuthorization).where(
            ContentAuthorization.workspace_id == workspace_id
        )

        if creator_id is not None:
            query = query.where(ContentAuthorization.creator_id == creator_id)
        if status_filter:
            query = query.where(ContentAuthorization.status == status_filter)

        result = await self._session.execute(
            query.order_by(ContentAuthorization.created_at.desc())
        )
        return list(result.scalars().all())

    async def check_authorization_status(
        self, authorization_id: uuid.UUID
    ) -> ContentAuthorization | None:
        """Check and update authorization status from the Marketing API."""
        result = await self._session.execute(
            select(ContentAuthorization).where(
                ContentAuthorization.id == authorization_id
            )
        )
        auth = result.scalar_one_or_none()
        if not auth:
            return None

        if auth.status != "PENDING":
            return auth

        try:
            gateway = await self._get_marketing_gateway(auth.workspace_id)
            resp = await gateway.get(
                "/creative/spark_ads/authorize/status/",
                params={"video_id": auth.platform_video_id or ""},
            )
            data = resp.get("data", {})
            api_status = data.get("status", "").upper()
            if api_status in ("APPROVED", "REJECTED", "EXPIRED", "REVOKED"):
                auth.status = api_status
                auth.authorization_code = data.get("authorization_code")
        except Exception:
            logger.exception(
                "Failed to check authorization status for %s",
                authorization_id,
            )

        return auth

    async def cancel_authorization(
        self, authorization_id: uuid.UUID
    ) -> ContentAuthorization | None:
        """Cancel/revoke a pending authorization."""
        result = await self._session.execute(
            select(ContentAuthorization).where(
                ContentAuthorization.id == authorization_id
            )
        )
        auth = result.scalar_one_or_none()
        if auth and auth.status == "PENDING":
            auth.status = "REVOKED"
        return auth

    async def get_authorization_code(
        self, authorization_id: uuid.UUID
    ) -> str | None:
        """Get the Spark Ads authorization code for an approved auth."""
        result = await self._session.execute(
            select(ContentAuthorization).where(
                ContentAuthorization.id == authorization_id
            )
        )
        auth = result.scalar_one_or_none()
        if auth and auth.status == "APPROVED":
            return auth.authorization_code
        return None

    async def list_authorized_videos(
        self, workspace_id: uuid.UUID
    ) -> list[ContentAuthorization]:
        """List all approved authorizations with valid codes."""
        result = await self._session.execute(
            select(ContentAuthorization)
            .where(
                ContentAuthorization.workspace_id == workspace_id,
                ContentAuthorization.status == "APPROVED",
            )
            .order_by(ContentAuthorization.created_at.desc())
        )
        return list(result.scalars().all())

    async def _get_marketing_gateway(
        self, workspace_id: uuid.UUID
    ) -> PlatformGateway:
        """Build a PlatformGateway for a Marketing account."""
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

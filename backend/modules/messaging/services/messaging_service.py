"""Business Messaging service — conversations, messages, and auto-messages via TikTok Marketing API."""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.platform import Platform, TokenVault
from backend.tiktok.gateway import PlatformGateway
from backend.tiktok.marketing.client import TikTokMarketingClient
from backend.utils.crypto import decrypt_token

logger = logging.getLogger(__name__)


class MessagingService:
    """Proxy for TikTok Business Messaging API endpoints.

    Builds a PlatformGateway lazily from the connected account's token vault
    and delegates all calls to the Marketing API messaging surface.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _build_gateway(self, connected_account_id: uuid.UUID) -> PlatformGateway:
        """Build a PlatformGateway from a connected account's marketing token."""
        result = await self._session.execute(
            select(TokenVault).where(
                TokenVault.connected_account_id == connected_account_id,
            )
        )
        token_vault = result.scalar_one_or_none()
        if not token_vault:
            raise ValueError(
                f"No token vault found for connected account {connected_account_id}"
            )

        access_token = decrypt_token(token_vault.encrypted_access_token)
        client = TikTokMarketingClient(access_token=access_token)
        return PlatformGateway(
            platform=Platform.MARKETING,
            account_id=str(connected_account_id),
            client=client,
        )

    # ------------------------------------------------------------------ #
    #  Conversations
    # ------------------------------------------------------------------ #

    async def list_conversations(
        self,
        connected_account_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List business messaging conversations."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.get(
            "/business/message/conversation/list/",
            params={
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def list_messages(
        self,
        connected_account_id: uuid.UUID,
        conversation_id: str,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List messages in a specific conversation."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.get(
            "/business/message/list/",
            params={
                "conversation_id": conversation_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def send_message(
        self,
        connected_account_id: uuid.UUID,
        conversation_id: str,
        content: str,
        *,
        media_url: str | None = None,
    ) -> dict:
        """Send a message in a conversation."""
        gateway = await self._build_gateway(connected_account_id)
        body: dict = {
            "conversation_id": conversation_id,
            "content": content,
        }
        if media_url is not None:
            body["media_url"] = media_url
        resp = await gateway.post(
            "/business/message/send/",
            json_body=body,
        )
        return resp.get("data", {})

    # ------------------------------------------------------------------ #
    #  Capability & Comment-to-Message
    # ------------------------------------------------------------------ #

    async def check_capability(self, connected_account_id: uuid.UUID) -> dict:
        """Check business messaging capability for the account."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.get(
            "/business/message/capability/check/",
        )
        return resp.get("data", {})

    async def toggle_comment_to_message(
        self,
        connected_account_id: uuid.UUID,
        *,
        enabled: bool,
    ) -> dict:
        """Toggle the comment-to-message feature."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.post(
            "/business/message/comment_to_message/update/",
            json_body={"enabled": enabled},
        )
        return resp.get("data", {})

    async def get_comment_to_message_setting(
        self, connected_account_id: uuid.UUID
    ) -> dict:
        """Get the current comment-to-message setting."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.get(
            "/business/message/comment_to_message/setting/",
        )
        return resp.get("data", {})

    # ------------------------------------------------------------------ #
    #  Auto-Messages
    # ------------------------------------------------------------------ #

    async def create_auto_message(
        self,
        connected_account_id: uuid.UUID,
        *,
        message_type: str,
        content: str,
    ) -> dict:
        """Create a new auto-message."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.post(
            "/business/message/auto/create/",
            json_body={
                "message_type": message_type,
                "content": content,
            },
        )
        return resp.get("data", {})

    async def list_auto_messages(self, connected_account_id: uuid.UUID) -> dict:
        """List all auto-messages for the account."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.get(
            "/business/message/auto/list/",
        )
        return resp.get("data", {})

    async def update_auto_message(
        self,
        connected_account_id: uuid.UUID,
        *,
        auto_message_id: str,
        content: str,
    ) -> dict:
        """Update an existing auto-message's content."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.post(
            "/business/message/auto/update/",
            json_body={
                "auto_message_id": auto_message_id,
                "content": content,
            },
        )
        return resp.get("data", {})

    async def toggle_auto_message(
        self,
        connected_account_id: uuid.UUID,
        *,
        auto_message_id: str,
        enabled: bool,
    ) -> dict:
        """Toggle an auto-message on or off."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.post(
            "/business/message/auto/toggle/",
            json_body={
                "auto_message_id": auto_message_id,
                "enabled": enabled,
            },
        )
        return resp.get("data", {})

    async def delete_auto_message(
        self,
        connected_account_id: uuid.UUID,
        *,
        auto_message_id: str,
    ) -> dict:
        """Delete an auto-message."""
        gateway = await self._build_gateway(connected_account_id)
        resp = await gateway.request(
            "DELETE",
            "/business/message/auto/delete/",
            json_body={"auto_message_id": auto_message_id},
        )
        return resp.get("data", {})

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount
from backend.modules.advertising.services.ad_account_service import AdAccountService

logger = logging.getLogger(__name__)


class CommentService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, ad_account: AdAccount):
        account_service = AdAccountService(self._session)
        return await account_service.build_gateway_for_ad_account(ad_account)

    async def list_comments(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        ad_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List comments on an ad."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/ad/comment/list/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "ad_id": ad_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def reply_to_comment(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        comment_id: str,
        text: str,
    ) -> dict:
        """Reply to a comment on an ad."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/ad/comment/reply/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "comment_id": comment_id,
                "text": text,
            },
        )
        return resp.get("data", {})

    async def hide_comment(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        comment_id: str,
    ) -> dict:
        """Hide a comment on an ad."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/ad/comment/hide/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "comment_id": comment_id,
            },
        )
        return resp.get("data", {})

    async def delete_comment(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        comment_id: str,
    ) -> dict:
        """Delete a comment on an ad."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/ad/comment/delete/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "comment_id": comment_id,
            },
        )
        return resp.get("data", {})

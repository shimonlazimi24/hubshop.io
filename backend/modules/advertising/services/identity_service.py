import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount
from backend.modules.advertising.services.ad_account_service import AdAccountService

logger = logging.getLogger(__name__)


class IdentityService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, ad_account: AdAccount):
        account_service = AdAccountService(self._session)
        return await account_service.build_gateway_for_ad_account(ad_account)

    async def create_identity(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        identity_config: dict,
    ) -> dict:
        """Create a new identity for an ad account."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            **identity_config,
        }
        resp = await gateway.post(
            "/identity/create/",
            json_body=body,
        )
        return resp.get("data", {})

    async def delete_identity(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        identity_id: str,
    ) -> dict:
        """Delete an identity."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/identity/delete/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "identity_id": identity_id,
            },
        )
        return resp.get("data", {})

    async def list_identities(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List identities for an ad account."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/identity/list/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def get_identity_detail(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        identity_id: str,
    ) -> dict:
        """Get details for a specific identity."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/identity/detail/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "identity_id": identity_id,
            },
        )
        return resp.get("data", {})

    async def get_identity_posts(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        identity_id: str,
    ) -> dict:
        """Get posts associated with a specific identity."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/identity/posts/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "identity_id": identity_id,
            },
        )
        return resp.get("data", {})

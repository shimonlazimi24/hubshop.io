import logging

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.tiktok.gateway import PlatformGateway

logger = logging.getLogger(__name__)


class StoreService:
    """Access TikTok Store products and Showcase products via Marketing API."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, ad_account: AdAccount) -> PlatformGateway:
        account_service = AdAccountService(self._session)
        return await account_service.build_gateway_for_ad_account(ad_account)

    async def list_stores(
        self,
        ad_account: AdAccount,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List stores linked to an advertiser account."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/store/get/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def get_store_products(
        self,
        ad_account: AdAccount,
        store_id: str,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List products within a specific store."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/store/product/get/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "store_id": store_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def get_showcase_identities(
        self,
        ad_account: AdAccount,
    ) -> dict:
        """Get showcase identities for an advertiser account."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/showcase/identity/get/",
            params={"advertiser_id": ad_account.advertiser_id},
        )
        return resp.get("data", {})

    async def get_showcase_products(
        self,
        ad_account: AdAccount,
        identity_id: str,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List products within a showcase identity."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/showcase/product/get/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "identity_id": identity_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

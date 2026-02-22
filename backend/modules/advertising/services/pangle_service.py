import logging

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount
from backend.modules.advertising.services.ad_account_service import AdAccountService

logger = logging.getLogger(__name__)


class PangleService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, ad_account: AdAccount):
        account_service = AdAccountService(self._session)
        return await account_service.build_gateway_for_ad_account(ad_account)

    async def get_block_list(
        self,
        ad_account: AdAccount,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Retrieve the Pangle block list for an ad account."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/pangle/block_list/get/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def update_block_list(
        self,
        ad_account: AdAccount,
        *,
        block_list: list[str],
        action: str,
    ) -> dict:
        """Add or remove entries from the Pangle block list.

        Args:
            ad_account: The ad account to update.
            block_list: List of app/placement IDs to add or remove.
            action: Either "ADD" or "REMOVE".
        """
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/pangle/block_list/update/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "block_list": block_list,
                "action": action,
            },
        )
        return resp.get("data", {})

    async def get_audience_packages(
        self,
        ad_account: AdAccount,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Retrieve Pangle audience packages for an ad account."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/pangle/audience_package/get/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

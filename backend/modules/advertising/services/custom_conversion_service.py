import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount
from backend.modules.advertising.services.ad_account_service import AdAccountService

logger = logging.getLogger(__name__)


class CustomConversionService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, ad_account: AdAccount):
        account_service = AdAccountService(self._session)
        return await account_service.build_gateway_for_ad_account(ad_account)

    async def list_conversions(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        pixel_id: str,
    ) -> dict:
        """List custom conversions for a pixel."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/custom_conversion/list/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "pixel_id": pixel_id,
            },
        )
        return resp.get("data", {})

    async def get_conversion_detail(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        custom_conversion_id: str,
    ) -> dict:
        """Get details of a specific custom conversion."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/custom_conversion/detail/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "custom_conversion_id": custom_conversion_id,
            },
        )
        return resp.get("data", {})

    async def create_conversion(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        conversion_config: dict,
    ) -> dict:
        """Create a new custom conversion."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            **conversion_config,
        }
        resp = await gateway.post(
            "/custom_conversion/create/",
            json_body=body,
        )
        return resp.get("data", {})

    async def update_conversion(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        custom_conversion_id: str,
        updates: dict,
    ) -> dict:
        """Update an existing custom conversion."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "custom_conversion_id": custom_conversion_id,
            **updates,
        }
        resp = await gateway.post(
            "/custom_conversion/update/",
            json_body=body,
        )
        return resp.get("data", {})

    async def delete_conversion(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        custom_conversion_id: str,
    ) -> dict:
        """Delete a custom conversion."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/custom_conversion/delete/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "custom_conversion_id": custom_conversion_id,
            },
        )
        return resp.get("data", {})

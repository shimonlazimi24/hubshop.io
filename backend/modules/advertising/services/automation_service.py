import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount
from backend.modules.advertising.services.ad_account_service import AdAccountService

logger = logging.getLogger(__name__)


class AutomationService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, ad_account: AdAccount):
        account_service = AdAccountService(self._session)
        return await account_service.build_gateway_for_ad_account(ad_account)

    async def list_rules(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List automation rules for an ad account."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/auto_rules/list/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def create_rule(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        rule_config: dict,
    ) -> dict:
        """Create a new automation rule."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            **rule_config,
        }
        resp = await gateway.post(
            "/auto_rules/create/",
            json_body=body,
        )
        return resp.get("data", {})

    async def update_rule(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        rule_id: str,
        updates: dict,
    ) -> dict:
        """Update an existing automation rule."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "rule_id": rule_id,
            **updates,
        }
        resp = await gateway.post(
            "/auto_rules/update/",
            json_body=body,
        )
        return resp.get("data", {})

    async def delete_rule(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        rule_id: str,
    ) -> dict:
        """Delete an automation rule."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/auto_rules/delete/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "rule_id": rule_id,
            },
        )
        return resp.get("data", {})

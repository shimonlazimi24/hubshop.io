import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount
from backend.modules.advertising.services.ad_account_service import AdAccountService

logger = logging.getLogger(__name__)


class SplitTestService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, ad_account: AdAccount):
        account_service = AdAccountService(self._session)
        return await account_service.build_gateway_for_ad_account(ad_account)

    async def create_split_test(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        test_config: dict,
    ) -> dict:
        """Create a new split test."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            **test_config,
        }
        resp = await gateway.post(
            "/split_test/create/",
            json_body=body,
        )
        return resp.get("data", {})

    async def update_test_time(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        split_test_id: str,
        updates: dict,
    ) -> dict:
        """Update the time settings of a split test."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "split_test_id": split_test_id,
            **updates,
        }
        resp = await gateway.post(
            "/split_test/time/update/",
            json_body=body,
        )
        return resp.get("data", {})

    async def end_split_test(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        split_test_id: str,
    ) -> dict:
        """End a running split test."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/split_test/end/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "split_test_id": split_test_id,
            },
        )
        return resp.get("data", {})

    async def get_results(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        split_test_id: str,
    ) -> dict:
        """Get the results of a split test."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/split_test/results/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "split_test_id": split_test_id,
            },
        )
        return resp.get("data", {})

    async def apply_winner(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        split_test_id: str,
    ) -> dict:
        """Apply the winning variant of a split test."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/split_test/winner/apply/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "split_test_id": split_test_id,
            },
        )
        return resp.get("data", {})

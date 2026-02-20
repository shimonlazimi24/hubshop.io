import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount
from backend.modules.advertising.services.ad_account_service import AdAccountService

logger = logging.getLogger(__name__)


class LeadService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, ad_account: AdAccount):
        account_service = AdAccountService(self._session)
        return await account_service.build_gateway_for_ad_account(ad_account)

    async def create_test_lead(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        form_id: str,
        lead_data: dict,
    ) -> dict:
        """Create a test lead for a lead generation form."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "form_id": form_id,
            **lead_data,
        }
        resp = await gateway.post(
            "/leads/test/create/",
            json_body=body,
        )
        return resp.get("data", {})

    async def get_test_lead(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        test_lead_id: str,
    ) -> dict:
        """Get details of a test lead."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/leads/test/get/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "test_lead_id": test_lead_id,
            },
        )
        return resp.get("data", {})

    async def create_download_task(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        form_id: str,
        start_date: str,
        end_date: str,
    ) -> dict:
        """Create a task to download leads for a form."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "form_id": form_id,
            "start_date": start_date,
            "end_date": end_date,
        }
        resp = await gateway.post(
            "/leads/download/create/",
            json_body=body,
        )
        return resp.get("data", {})

    async def download_leads(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        task_id: str,
    ) -> dict:
        """Download leads for a completed download task."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/leads/download/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "task_id": task_id,
            },
        )
        return resp.get("data", {})

    async def get_form_libraries(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
    ) -> dict:
        """Get available form libraries for the ad account."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/leads/form/libraries/",
            params={
                "advertiser_id": ad_account.advertiser_id,
            },
        )
        return resp.get("data", {})

    async def get_form_fields(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        form_id: str,
    ) -> dict:
        """Get fields for a specific lead generation form."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/leads/form/fields/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "form_id": form_id,
            },
        )
        return resp.get("data", {})

    async def get_leads(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        form_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Get leads for a specific form."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/leads/get/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "form_id": form_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

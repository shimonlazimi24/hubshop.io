import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount
from backend.modules.advertising.services.ad_account_service import AdAccountService

logger = logging.getLogger(__name__)


class ChangeLogService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, ad_account: AdAccount):
        account_service = AdAccountService(self._session)
        return await account_service.build_gateway_for_ad_account(ad_account)

    async def create_download_task(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        object_type: str,
        start_date: str,
        end_date: str,
    ) -> dict:
        """Create a task to download change log data."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "object_type": object_type,
            "start_date": start_date,
            "end_date": end_date,
        }
        resp = await gateway.post(
            "/change_log/download/create/",
            json_body=body,
        )
        return resp.get("data", {})

    async def get_task_status(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        task_id: str,
    ) -> dict:
        """Get the status of a change log download task."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/change_log/download/status/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "task_id": task_id,
            },
        )
        return resp.get("data", {})

    async def download_file(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        task_id: str,
    ) -> dict:
        """Download the change log file for a completed task."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/change_log/download/file/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "task_id": task_id,
            },
        )
        return resp.get("data", {})

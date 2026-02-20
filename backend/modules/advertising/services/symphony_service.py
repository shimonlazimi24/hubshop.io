import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount
from backend.modules.advertising.services.ad_account_service import AdAccountService

logger = logging.getLogger(__name__)


class SymphonyService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, ad_account: AdAccount):
        account_service = AdAccountService(self._session)
        return await account_service.build_gateway_for_ad_account(ad_account)

    async def get_smart_creative_materials(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        ad_id: str,
    ) -> dict:
        """Get smart creative materials for an ad."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/smart_creative/material/get/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "ad_id": ad_id,
            },
        )
        return resp.get("data", {})

    async def create_smart_creative_ad(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        ad_config: dict,
    ) -> dict:
        """Create a smart creative ad via Symphony."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            **ad_config,
        }
        resp = await gateway.post(
            "/smart_creative/ad/create/",
            json_body=body,
        )
        return resp.get("data", {})

    async def update_smart_creative_materials(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        ad_id: str,
        materials: list[dict],
    ) -> dict:
        """Update smart creative materials for an ad."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "ad_id": ad_id,
            "materials": materials,
        }
        resp = await gateway.post(
            "/smart_creative/material/update/",
            json_body=body,
        )
        return resp.get("data", {})

    async def recommend_smart_text(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        ad_text: str,
    ) -> dict:
        """Get smart text recommendations for ad copy."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/creative/smart_text/recommend/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "ad_text": ad_text,
            },
        )
        return resp.get("data", {})

    async def recommend_cta(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        objective: str,
    ) -> dict:
        """Get CTA recommendations based on campaign objective."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/creative/cta/recommend/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "objective": objective,
            },
        )
        return resp.get("data", {})

    async def create_smart_fix(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        creative_id: str,
    ) -> dict:
        """Create a smart fix task for a creative."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/creative/smart_fix/create/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "creative_id": creative_id,
            },
        )
        return resp.get("data", {})

    async def get_smart_fix_result(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        task_id: str,
    ) -> dict:
        """Get the result of a smart fix task."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/creative/smart_fix/result/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "task_id": task_id,
            },
        )
        return resp.get("data", {})

    async def detect_fatigue(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        ad_ids: list[str],
    ) -> dict:
        """Detect creative fatigue for given ads."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/creative/fatigue/detect/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "ad_ids": ad_ids,
            },
        )
        return resp.get("data", {})

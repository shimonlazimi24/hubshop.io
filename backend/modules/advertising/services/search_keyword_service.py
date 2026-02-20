import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount
from backend.modules.advertising.services.ad_account_service import AdAccountService

logger = logging.getLogger(__name__)


class SearchKeywordService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, ad_account: AdAccount):
        account_service = AdAccountService(self._session)
        return await account_service.build_gateway_for_ad_account(ad_account)

    async def recommend_keywords(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Get keyword recommendations based on a seed keyword."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/tool/keyword/recommend/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "keyword": keyword,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def discover_keywords(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        keyword: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Discover related keywords from TikTok keyword tool."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/tool/keyword/discover/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "keyword": keyword,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def list_negative_keywords(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        ad_group_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List negative keywords for an ad group."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/negative_keywords/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "ad_group_id": ad_group_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def create_negative_keyword(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        ad_group_id: str,
        keyword: str,
        match_type: str = "EXACT",
    ) -> dict:
        """Create a negative keyword for an ad group."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "ad_group_id": ad_group_id,
            "keyword": keyword,
            "match_type": match_type,
        }
        resp = await gateway.post(
            "/negative_keywords/create/",
            json_body=body,
        )
        return resp.get("data", {})

    async def update_negative_keyword(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        keyword_id: str,
        updates: dict,
    ) -> dict:
        """Update an existing negative keyword."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "keyword_id": keyword_id,
            **updates,
        }
        resp = await gateway.post(
            "/negative_keywords/update/",
            json_body=body,
        )
        return resp.get("data", {})

    async def delete_negative_keyword(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        keyword_ids: list[str],
    ) -> dict:
        """Delete negative keywords by their IDs."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/negative_keywords/delete/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "keyword_ids": keyword_ids,
            },
        )
        return resp.get("data", {})

    async def get_campaign_health(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        campaign_id: str,
    ) -> dict:
        """Get search ads health metrics for a campaign."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/tool/search_ads/health/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "campaign_id": campaign_id,
            },
        )
        return resp.get("data", {})

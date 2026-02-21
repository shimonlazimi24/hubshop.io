import json
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount
from backend.modules.advertising.services.ad_account_service import AdAccountService

logger = logging.getLogger(__name__)


class CreativeService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_gateway(self, ad_account: AdAccount):
        account_service = AdAccountService(self._session)
        return await account_service.build_gateway_for_ad_account(ad_account)

    async def list_portfolios(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """List creative portfolios for an ad account."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/creative/portfolio/list/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def create_portfolio(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        name: str,
    ) -> dict:
        """Create a new creative portfolio."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.post(
            "/creative/portfolio/create/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "portfolio_name": name,
            },
        )
        return resp.get("data", {})

    async def generate_smart_text(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        params: dict,
    ) -> dict:
        """Generate smart text suggestions for ad creatives."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            **params,
        }
        resp = await gateway.post(
            "/creative/smart_text/generate/",
            json_body=body,
        )
        return resp.get("data", {})

    async def get_trending_hashtags(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
    ) -> dict:
        """Get trending hashtags for the ad account's region."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/creative/trending_hashtags/",
            params={
                "advertiser_id": ad_account.advertiser_id,
            },
        )
        return resp.get("data", {})

    # --- Creative Upload & Management ---

    async def upload_video(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        video_url: str,
        video_name: str | None = None,
    ) -> dict:
        """Upload a video to the ad account by URL."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "upload_type": "UPLOAD_BY_URL",
            "video_url": video_url,
        }
        if video_name is not None:
            body["file_name"] = video_name
        resp = await gateway.post(
            "/file/video/ad/upload/",
            json_body=body,
        )
        return resp.get("data", {})

    async def get_video_info(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        video_ids: list[str],
    ) -> dict:
        """Get info for one or more ad videos."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/file/video/ad/info/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "video_ids": json.dumps(video_ids),
            },
        )
        return resp.get("data", {})

    async def upload_image(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        image_url: str,
        image_name: str | None = None,
    ) -> dict:
        """Upload an image to the ad account by URL."""
        gateway = await self._get_gateway(ad_account)
        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "upload_type": "UPLOAD_BY_URL",
            "image_url": image_url,
        }
        if image_name is not None:
            body["file_name"] = image_name
        resp = await gateway.post(
            "/file/image/ad/upload/",
            json_body=body,
        )
        return resp.get("data", {})

    async def get_image_info(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        image_ids: list[str],
    ) -> dict:
        """Get info for one or more ad images."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/file/image/ad/info/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "image_ids": json.dumps(image_ids),
            },
        )
        return resp.get("data", {})

    async def search_music(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        query: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Search the music library for ad creatives."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/creative/music/search/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "query": query,
                "page": str(page),
                "page_size": str(page_size),
            },
        )
        return resp.get("data", {})

    async def get_ad_creative_info(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        ad_ids: list[str],
    ) -> dict:
        """Get creative details for one or more ads."""
        gateway = await self._get_gateway(ad_account)
        resp = await gateway.get(
            "/creative/ads/info/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "ad_ids": json.dumps(ad_ids),
            },
        )
        return resp.get("data", {})

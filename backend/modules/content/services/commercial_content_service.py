import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.platform import (
    AccountStatus,
    ConnectedAccount,
    Platform,
    TokenVault,
)
from backend.tiktok.developer.client import TikTokDeveloperClient
from backend.tiktok.gateway import PlatformGateway
from backend.utils.crypto import decrypt_token

logger = logging.getLogger(__name__)


class CommercialContentService:
    """Service for querying TikTok's Ad Library and commercial content."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search_ads(
        self,
        workspace_id: uuid.UUID,
        *,
        search_term: str | None = None,
        date_range: dict,
        country_code: str = "ALL",
        advertiser_business_ids: list[str] | None = None,
        max_count: int = 20,
        search_id: str | None = None,
    ) -> dict:
        """Search ads via the Ad Library API."""
        _, gateway = await self._get_developer_gateway(workspace_id)

        filters: dict = {
            "ad_published_date_range": date_range,
            "country_code": country_code,
        }
        if advertiser_business_ids:
            filters["advertiser_business_ids"] = advertiser_business_ids

        body: dict = {
            "filters": filters,
            "max_count": max_count,
        }
        if search_term:
            body["search_term"] = search_term
        if search_id:
            body["search_id"] = search_id

        resp = await gateway.post(
            "/research/adlib/ad/query/",
            json_body=body,
            params={
                "fields": "ad.id,ad.first_shown_date,ad.last_shown_date,ad.status,ad.videos,ad.image_urls,ad.reach,advertiser.business_id,advertiser.business_name"
            },
        )
        return resp.get("data", {})

    async def search_advertisers(
        self,
        workspace_id: uuid.UUID,
        *,
        search_term: str,
        max_count: int = 20,
    ) -> dict:
        """Search advertisers via the Ad Library API."""
        _, gateway = await self._get_developer_gateway(workspace_id)

        resp = await gateway.post(
            "/research/adlib/advertiser/query/",
            json_body={
                "search_term": search_term,
                "max_count": max_count,
            },
            params={"fields": "business_name,business_id,country_code"},
        )
        return resp.get("data", {})

    async def get_ad_detail(
        self,
        workspace_id: uuid.UUID,
        *,
        ad_id: int,
    ) -> dict:
        """Get detailed information about a specific ad."""
        _, gateway = await self._get_developer_gateway(workspace_id)

        resp = await gateway.post(
            "/research/adlib/ad/detail/",
            json_body={"ad_id": ad_id},
            params={
                "fields": "ad.id,ad.first_shown_date,ad.last_shown_date,ad.status,ad.videos,ad.image_urls,ad.reach,advertiser.business_id,advertiser.business_name"
            },
        )
        return resp.get("data", {})

    async def get_ad_report(
        self,
        workspace_id: uuid.UUID,
        *,
        date_range: dict,
        country_code: str = "ALL",
        advertiser_business_ids: list[str] | None = None,
    ) -> dict:
        """Get ad report with time series data by country."""
        _, gateway = await self._get_developer_gateway(workspace_id)

        filters: dict = {
            "ad_published_date_range": date_range,
            "country_code": country_code,
        }
        if advertiser_business_ids:
            filters["advertiser_business_ids"] = advertiser_business_ids

        resp = await gateway.post(
            "/research/adlib/ad/report/",
            json_body={"filters": filters},
            params={"fields": "count_time_series_by_country"},
        )
        return resp.get("data", {})

    async def search_commercial_content(
        self,
        workspace_id: uuid.UUID,
        *,
        date_range: dict,
        creator_usernames: list[str] | None = None,
        creator_country_code: str | None = None,
        max_count: int = 20,
        search_id: str | None = None,
    ) -> dict:
        """Search branded/commercial content via the Ad Library API."""
        _, gateway = await self._get_developer_gateway(workspace_id)

        filters: dict = {
            "content_published_date_range": date_range,
        }
        if creator_country_code:
            filters["creator_country_code"] = creator_country_code
        if creator_usernames:
            filters["creator_usernames"] = creator_usernames

        body: dict = {
            "filters": filters,
            "max_count": max_count,
        }
        if search_id:
            body["search_id"] = search_id

        resp = await gateway.post(
            "/research/adlib/commercial_content/query/",
            json_body=body,
            params={
                "fields": "id,create_timestamp,create_date,label,brand_names,creator,videos"
            },
        )
        return resp.get("data", {})

    async def _get_developer_gateway(
        self, workspace_id: uuid.UUID
    ) -> tuple[ConnectedAccount, PlatformGateway]:
        """Get the first active Developer account and its gateway."""
        result = await self._session.execute(
            select(ConnectedAccount).where(
                ConnectedAccount.workspace_id == workspace_id,
                ConnectedAccount.platform == Platform.DEVELOPER,
                ConnectedAccount.status == AccountStatus.ACTIVE,
            )
        )
        account = result.scalars().first()
        if not account:
            raise ValueError("No active Developer account found")

        result = await self._session.execute(
            select(TokenVault).where(
                TokenVault.connected_account_id == account.id
            )
        )
        vault = result.scalar_one_or_none()
        if not vault:
            raise ValueError(f"No token vault for account {account.id}")

        access_token = decrypt_token(vault.encrypted_access_token)
        client = TikTokDeveloperClient(access_token=access_token)
        gateway = PlatformGateway(
            platform=Platform.DEVELOPER,
            account_id=str(account.id),
            client=client,
        )
        return account, gateway

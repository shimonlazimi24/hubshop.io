import logging
import uuid
from datetime import UTC, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount, Campaign
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class CampaignService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_campaigns(
        self,
        workspace_id: uuid.UUID,
        *,
        ad_account_id: uuid.UUID | None = None,
        objective: str | None = None,
        status_filter: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Campaign]:
        query = select(Campaign).where(Campaign.workspace_id == workspace_id)
        count_query = select(func.count(Campaign.id)).where(
            Campaign.workspace_id == workspace_id
        )

        if ad_account_id:
            query = query.where(Campaign.ad_account_id == ad_account_id)
            count_query = count_query.where(Campaign.ad_account_id == ad_account_id)
        if objective:
            query = query.where(Campaign.objective_type == objective)
            count_query = count_query.where(Campaign.objective_type == objective)
        if status_filter:
            query = query.where(Campaign.operation_status == status_filter)
            count_query = count_query.where(
                Campaign.operation_status == status_filter
            )
        if search:
            query = query.where(Campaign.campaign_name.ilike(f"%{search}%"))
            count_query = count_query.where(
                Campaign.campaign_name.ilike(f"%{search}%")
            )

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(Campaign.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(
            items=items, total=total, page=page, page_size=page_size
        )

    async def get_campaign(self, campaign_id: uuid.UUID) -> Campaign | None:
        result = await self._session.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        return result.scalar_one_or_none()

    async def create_campaign(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        *,
        campaign_name: str,
        objective_type: str,
        budget_mode: str,
        budget: str | None = None,
    ) -> Campaign:
        """Proxy create to TikTok Marketing API then store locally."""
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "campaign_name": campaign_name,
            "objective_type": objective_type,
            "budget_mode": budget_mode,
        }
        if budget is not None:
            body["budget"] = float(budget)

        resp = await gateway.post("/campaign/create/", json_body=body)
        data = resp.get("data", {})
        platform_campaign_id = str(data.get("campaign_id", ""))

        campaign = Campaign(
            workspace_id=workspace_id,
            ad_account_id=ad_account.id,
            platform_campaign_id=platform_campaign_id,
            campaign_name=campaign_name,
            objective_type=objective_type,
            budget_mode=budget_mode,
            budget=budget,
            operation_status="ENABLE",
            detail_json=data,
        )
        self._session.add(campaign)
        await self._session.flush()
        return campaign

    async def update_campaign(
        self,
        campaign: Campaign,
        ad_account: AdAccount,
        *,
        campaign_name: str | None = None,
        budget_mode: str | None = None,
        budget: str | None = None,
    ) -> Campaign:
        """Proxy update to TikTok Marketing API then update locally."""
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "campaign_id": campaign.platform_campaign_id,
        }
        if campaign_name is not None:
            body["campaign_name"] = campaign_name
            campaign.campaign_name = campaign_name
        if budget_mode is not None:
            body["budget_mode"] = budget_mode
            campaign.budget_mode = budget_mode
        if budget is not None:
            body["budget"] = float(budget)
            campaign.budget = budget

        await gateway.post("/campaign/update/", json_body=body)
        return campaign

    async def update_campaign_status(
        self,
        campaign: Campaign,
        ad_account: AdAccount,
        *,
        operation_status: str,
    ) -> Campaign:
        """Update campaign operation status via TikTok API."""
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        await gateway.post(
            "/campaign/status/update/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "campaign_ids": [campaign.platform_campaign_id],
                "opt_status": operation_status,
            },
        )
        campaign.operation_status = operation_status
        return campaign

    async def sync_campaigns(self, ad_account: AdAccount) -> int:
        """Paginate /v1.3/campaign/get/ and upsert locally."""
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)
        synced = 0
        page = 1
        page_size = 100

        while True:
            resp = await gateway.get(
                "/campaign/get/",
                params={
                    "advertiser_id": ad_account.advertiser_id,
                    "page": str(page),
                    "page_size": str(page_size),
                },
            )
            data = resp.get("data", {})
            campaign_list = data.get("list", [])

            for campaign_data in campaign_list:
                await self.upsert_campaign_from_api(
                    ad_account=ad_account, campaign_data=campaign_data
                )
                synced += 1

            total_page = data.get("page_info", {}).get("total_page", 1)
            if page >= total_page or not campaign_list:
                break
            page += 1

        ad_account.last_sync_at = datetime.now(tz=UTC)
        return synced

    async def upsert_campaign_from_api(
        self, *, ad_account: AdAccount, campaign_data: dict
    ) -> Campaign:
        platform_id = str(campaign_data.get("campaign_id", ""))
        result = await self._session.execute(
            select(Campaign).where(Campaign.platform_campaign_id == platform_id)
        )
        campaign = result.scalar_one_or_none()

        name = campaign_data.get("campaign_name", "")
        objective = campaign_data.get("objective_type")
        budget_mode = campaign_data.get("budget_mode")
        budget = str(campaign_data["budget"]) if "budget" in campaign_data else None
        op_status = campaign_data.get("operation_status", "ENABLE")
        secondary = campaign_data.get("secondary_status")

        if campaign:
            campaign.campaign_name = name
            campaign.objective_type = objective
            campaign.budget_mode = budget_mode
            campaign.budget = budget
            campaign.operation_status = op_status
            campaign.secondary_status = secondary
            campaign.detail_json = campaign_data
        else:
            campaign = Campaign(
                workspace_id=ad_account.workspace_id,
                ad_account_id=ad_account.id,
                platform_campaign_id=platform_id,
                campaign_name=name,
                objective_type=objective,
                budget_mode=budget_mode,
                budget=budget,
                operation_status=op_status,
                secondary_status=secondary,
                detail_json=campaign_data,
            )
            self._session.add(campaign)
            await self._session.flush()

        return campaign

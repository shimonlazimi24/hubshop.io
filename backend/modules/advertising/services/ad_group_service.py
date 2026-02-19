import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount, AdGroup, Campaign
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class AdGroupService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_ad_groups(
        self,
        workspace_id: uuid.UUID,
        *,
        campaign_id: uuid.UUID | None = None,
        ad_account_id: uuid.UUID | None = None,
        status_filter: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[AdGroup]:
        query = select(AdGroup).where(AdGroup.workspace_id == workspace_id)
        count_query = select(func.count(AdGroup.id)).where(
            AdGroup.workspace_id == workspace_id
        )

        if campaign_id:
            query = query.where(AdGroup.campaign_id == campaign_id)
            count_query = count_query.where(AdGroup.campaign_id == campaign_id)
        if ad_account_id:
            query = query.where(AdGroup.ad_account_id == ad_account_id)
            count_query = count_query.where(
                AdGroup.ad_account_id == ad_account_id
            )
        if status_filter:
            query = query.where(AdGroup.operation_status == status_filter)
            count_query = count_query.where(
                AdGroup.operation_status == status_filter
            )

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(AdGroup.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(
            items=items, total=total, page=page, page_size=page_size
        )

    async def get_ad_group(self, adgroup_id: uuid.UUID) -> AdGroup | None:
        result = await self._session.execute(
            select(AdGroup).where(AdGroup.id == adgroup_id)
        )
        return result.scalar_one_or_none()

    async def create_ad_group(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        campaign: Campaign,
        *,
        adgroup_name: str,
        placement_type: str = "PLACEMENT_TYPE_AUTOMATIC",
        bid_type: str | None = None,
        bid_amount: str | None = None,
        budget: str | None = None,
        optimization_goal: str | None = None,
        targeting: dict | None = None,
    ) -> AdGroup:
        """Proxy create to TikTok Marketing API then store locally."""
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "campaign_id": campaign.platform_campaign_id,
            "adgroup_name": adgroup_name,
            "placement_type": placement_type,
        }
        if bid_type:
            body["bid_type"] = bid_type
        if bid_amount:
            body["bid"] = float(bid_amount)
        if budget:
            body["budget"] = float(budget)
        if optimization_goal:
            body["optimization_goal"] = optimization_goal
        if targeting:
            body.update(targeting)

        resp = await gateway.post("/adgroup/create/", json_body=body)
        data = resp.get("data", {})
        platform_adgroup_id = str(data.get("adgroup_id", ""))

        ad_group = AdGroup(
            workspace_id=workspace_id,
            ad_account_id=ad_account.id,
            campaign_id=campaign.id,
            platform_adgroup_id=platform_adgroup_id,
            adgroup_name=adgroup_name,
            placement_type=placement_type,
            bid_type=bid_type,
            bid_amount=bid_amount,
            budget=budget,
            optimization_goal=optimization_goal,
            targeting_json=targeting,
            operation_status="ENABLE",
            detail_json=data,
        )
        self._session.add(ad_group)
        await self._session.flush()
        return ad_group

    async def update_ad_group(
        self,
        ad_group: AdGroup,
        ad_account: AdAccount,
        *,
        adgroup_name: str | None = None,
        bid_type: str | None = None,
        bid_amount: str | None = None,
        budget: str | None = None,
        optimization_goal: str | None = None,
        targeting: dict | None = None,
    ) -> AdGroup:
        """Proxy update to TikTok Marketing API then update locally."""
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "adgroup_id": ad_group.platform_adgroup_id,
        }
        if adgroup_name is not None:
            body["adgroup_name"] = adgroup_name
            ad_group.adgroup_name = adgroup_name
        if bid_type is not None:
            body["bid_type"] = bid_type
            ad_group.bid_type = bid_type
        if bid_amount is not None:
            body["bid"] = float(bid_amount)
            ad_group.bid_amount = bid_amount
        if budget is not None:
            body["budget"] = float(budget)
            ad_group.budget = budget
        if optimization_goal is not None:
            body["optimization_goal"] = optimization_goal
            ad_group.optimization_goal = optimization_goal
        if targeting is not None:
            body.update(targeting)
            ad_group.targeting_json = targeting

        await gateway.post("/adgroup/update/", json_body=body)
        return ad_group

    async def update_ad_group_status(
        self,
        ad_group: AdGroup,
        ad_account: AdAccount,
        *,
        operation_status: str,
    ) -> AdGroup:
        """Update ad group operation status via TikTok API."""
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        await gateway.post(
            "/adgroup/status/update/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "adgroup_ids": [ad_group.platform_adgroup_id],
                "opt_status": operation_status,
            },
        )
        ad_group.operation_status = operation_status
        return ad_group

    async def sync_ad_groups(self, ad_account: AdAccount) -> int:
        """Paginate /v1.3/adgroup/get/ and upsert locally."""
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        # First, load all campaigns for FK resolution
        campaign_result = await self._session.execute(
            select(Campaign).where(Campaign.ad_account_id == ad_account.id)
        )
        campaign_map: dict[str, Campaign] = {
            c.platform_campaign_id: c for c in campaign_result.scalars().all()
        }

        synced = 0
        page = 1
        page_size = 100

        while True:
            resp = await gateway.get(
                "/adgroup/get/",
                params={
                    "advertiser_id": ad_account.advertiser_id,
                    "page": str(page),
                    "page_size": str(page_size),
                },
            )
            data = resp.get("data", {})
            adgroup_list = data.get("list", [])

            for adgroup_data in adgroup_list:
                campaign_id_str = str(adgroup_data.get("campaign_id", ""))
                campaign = campaign_map.get(campaign_id_str)
                if not campaign:
                    logger.warning(
                        "Skipping ad group %s: campaign %s not found locally",
                        adgroup_data.get("adgroup_id"),
                        campaign_id_str,
                    )
                    continue

                await self.upsert_ad_group_from_api(
                    ad_account=ad_account,
                    campaign=campaign,
                    adgroup_data=adgroup_data,
                )
                synced += 1

            total_page = data.get("page_info", {}).get("total_page", 1)
            if page >= total_page or not adgroup_list:
                break
            page += 1

        return synced

    async def upsert_ad_group_from_api(
        self,
        *,
        ad_account: AdAccount,
        campaign: Campaign,
        adgroup_data: dict,
    ) -> AdGroup:
        platform_id = str(adgroup_data.get("adgroup_id", ""))
        result = await self._session.execute(
            select(AdGroup).where(AdGroup.platform_adgroup_id == platform_id)
        )
        ad_group = result.scalar_one_or_none()

        name = adgroup_data.get("adgroup_name", "")
        placement = adgroup_data.get("placement_type")
        bid_type = adgroup_data.get("bid_type")
        bid_amount = (
            str(adgroup_data["bid"]) if "bid" in adgroup_data else None
        )
        budget = (
            str(adgroup_data["budget"]) if "budget" in adgroup_data else None
        )
        opt_goal = adgroup_data.get("optimization_goal")
        op_status = adgroup_data.get("operation_status", "ENABLE")

        if ad_group:
            ad_group.adgroup_name = name
            ad_group.placement_type = placement
            ad_group.bid_type = bid_type
            ad_group.bid_amount = bid_amount
            ad_group.budget = budget
            ad_group.optimization_goal = opt_goal
            ad_group.operation_status = op_status
            ad_group.targeting_json = adgroup_data.get("targeting")
            ad_group.detail_json = adgroup_data
        else:
            ad_group = AdGroup(
                workspace_id=ad_account.workspace_id,
                ad_account_id=ad_account.id,
                campaign_id=campaign.id,
                platform_adgroup_id=platform_id,
                adgroup_name=name,
                placement_type=placement,
                bid_type=bid_type,
                bid_amount=bid_amount,
                budget=budget,
                optimization_goal=opt_goal,
                operation_status=op_status,
                targeting_json=adgroup_data.get("targeting"),
                detail_json=adgroup_data,
            )
            self._session.add(ad_group)
            await self._session.flush()

        return ad_group

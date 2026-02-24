import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import Ad, AdAccount, AdGroup
from backend.modules.advertising.services.ad_account_service import AdAccountService
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class AdService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_ads(
        self,
        workspace_id: uuid.UUID,
        *,
        adgroup_id: uuid.UUID | None = None,
        ad_account_id: uuid.UUID | None = None,
        status_filter: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Ad]:
        query = select(Ad).where(Ad.workspace_id == workspace_id)
        count_query = select(func.count(Ad.id)).where(Ad.workspace_id == workspace_id)

        if adgroup_id:
            query = query.where(Ad.adgroup_id == adgroup_id)
            count_query = count_query.where(Ad.adgroup_id == adgroup_id)
        if ad_account_id:
            query = query.where(Ad.ad_account_id == ad_account_id)
            count_query = count_query.where(Ad.ad_account_id == ad_account_id)
        if status_filter:
            query = query.where(Ad.operation_status == status_filter)
            count_query = count_query.where(Ad.operation_status == status_filter)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(Ad.updated_at.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    async def get_ad(self, ad_id: uuid.UUID) -> Ad | None:
        result = await self._session.execute(select(Ad).where(Ad.id == ad_id))
        return result.scalar_one_or_none()

    async def create_ad(
        self,
        workspace_id: uuid.UUID,
        ad_account: AdAccount,
        ad_group: AdGroup,
        *,
        ad_name: str,
        ad_format: str | None = None,
        ad_text: str | None = None,
        call_to_action: str | None = None,
        landing_page_url: str | None = None,
    ) -> Ad:
        """Proxy create to TikTok Marketing API then store locally."""
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "adgroup_id": ad_group.platform_adgroup_id,
            "ad_name": ad_name,
        }
        if ad_format:
            body["ad_format"] = ad_format
        if ad_text:
            body["ad_text"] = ad_text
        if call_to_action:
            body["call_to_action"] = call_to_action
        if landing_page_url:
            body["landing_page_url"] = landing_page_url

        resp = await gateway.post("/ad/create/", json_body=body)
        data = resp.get("data", {})
        platform_ad_id = str(data.get("ad_id", ""))

        ad = Ad(
            workspace_id=workspace_id,
            ad_account_id=ad_account.id,
            adgroup_id=ad_group.id,
            platform_ad_id=platform_ad_id,
            ad_name=ad_name,
            ad_format=ad_format,
            ad_text=ad_text,
            call_to_action=call_to_action,
            landing_page_url=landing_page_url,
            operation_status="ENABLE",
            detail_json=data,
        )
        self._session.add(ad)
        await self._session.flush()
        return ad

    async def update_ad(
        self,
        ad: Ad,
        ad_account: AdAccount,
        *,
        ad_name: str | None = None,
        ad_text: str | None = None,
        call_to_action: str | None = None,
        landing_page_url: str | None = None,
    ) -> Ad:
        """Proxy update to TikTok Marketing API then update locally."""
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "ad_id": ad.platform_ad_id,
        }
        if ad_name is not None:
            body["ad_name"] = ad_name
            ad.ad_name = ad_name
        if ad_text is not None:
            body["ad_text"] = ad_text
            ad.ad_text = ad_text
        if call_to_action is not None:
            body["call_to_action"] = call_to_action
            ad.call_to_action = call_to_action
        if landing_page_url is not None:
            body["landing_page_url"] = landing_page_url
            ad.landing_page_url = landing_page_url

        await gateway.post("/ad/update/", json_body=body)
        return ad

    async def update_ad_status(
        self,
        ad: Ad,
        ad_account: AdAccount,
        *,
        operation_status: str,
    ) -> Ad:
        """Update ad operation status via TikTok API."""
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        await gateway.post(
            "/ad/status/update/",
            json_body={
                "advertiser_id": ad_account.advertiser_id,
                "ad_ids": [ad.platform_ad_id],
                "opt_status": operation_status,
            },
        )
        ad.operation_status = operation_status
        return ad

    async def sync_ads(self, ad_account: AdAccount) -> int:
        """Paginate /v1.3/ad/get/ and upsert locally."""
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        # Load ad groups for FK resolution
        adgroup_result = await self._session.execute(
            select(AdGroup).where(AdGroup.ad_account_id == ad_account.id)
        )
        adgroup_map: dict[str, AdGroup] = {
            ag.platform_adgroup_id: ag for ag in adgroup_result.scalars().all()
        }

        synced = 0
        page = 1
        page_size = 100

        while True:
            resp = await gateway.get(
                "/ad/get/",
                params={
                    "advertiser_id": ad_account.advertiser_id,
                    "page": str(page),
                    "page_size": str(page_size),
                },
            )
            data = resp.get("data", {})
            ad_list = data.get("list", [])

            for ad_data in ad_list:
                adgroup_id_str = str(ad_data.get("adgroup_id", ""))
                ad_group = adgroup_map.get(adgroup_id_str)
                if not ad_group:
                    logger.warning(
                        "Skipping ad %s: ad group %s not found locally",
                        ad_data.get("ad_id"),
                        adgroup_id_str,
                    )
                    continue

                await self.upsert_ad_from_api(
                    ad_account=ad_account,
                    ad_group=ad_group,
                    ad_data=ad_data,
                )
                synced += 1

            total_page = data.get("page_info", {}).get("total_page", 1)
            if page >= total_page or not ad_list:
                break
            page += 1

        return synced

    async def upsert_ad_from_api(
        self,
        *,
        ad_account: AdAccount,
        ad_group: AdGroup,
        ad_data: dict,
    ) -> Ad:
        platform_id = str(ad_data.get("ad_id", ""))
        result = await self._session.execute(
            select(Ad).where(Ad.platform_ad_id == platform_id)
        )
        ad = result.scalar_one_or_none()

        name = ad_data.get("ad_name", "")
        ad_format = ad_data.get("ad_format")
        ad_text = ad_data.get("ad_text")
        cta = ad_data.get("call_to_action")
        landing_url = ad_data.get("landing_page_url")
        image_url = ad_data.get("image_url") or ad_data.get("avatar_icon_web_uri")
        op_status = ad_data.get("operation_status", "ENABLE")

        if ad:
            ad.ad_name = name
            ad.ad_format = ad_format
            ad.ad_text = ad_text
            ad.call_to_action = cta
            ad.landing_page_url = landing_url
            ad.image_url = image_url
            ad.operation_status = op_status
            ad.detail_json = ad_data
        else:
            ad = Ad(
                workspace_id=ad_account.workspace_id,
                ad_account_id=ad_account.id,
                adgroup_id=ad_group.id,
                platform_ad_id=platform_id,
                ad_name=name,
                ad_format=ad_format,
                ad_text=ad_text,
                call_to_action=cta,
                landing_page_url=landing_url,
                image_url=image_url,
                operation_status=op_status,
                detail_json=ad_data,
            )
            self._session.add(ad)
            await self._session.flush()

        return ad

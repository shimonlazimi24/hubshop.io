import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.advertising import AdAccount, ReportCache
from backend.modules.advertising.services.ad_account_service import AdAccountService

logger = logging.getLogger(__name__)

_CACHE_TTL = timedelta(hours=1)


class ReportService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_sync_report(
        self,
        ad_account: AdAccount,
        *,
        report_type: str = "BASIC",
        data_level: str = "AUCTION_CAMPAIGN",
        date_start: str,
        date_end: str,
        metrics: list[str] | None = None,
        dimensions: list[str] | None = None,
    ) -> dict:
        """Check cache, then call /v1.3/report/integrated/get/ if miss."""
        now = datetime.now(tz=timezone.utc)

        # Check cache
        cache = await self._find_cache(
            ad_account_id=ad_account.id,
            report_type=report_type,
            data_level=data_level,
            date_start=date_start,
            date_end=date_end,
        )
        if cache and cache.expires_at > now:
            return cache.report_data or {}

        # Call API
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "report_type": report_type,
            "data_level": data_level,
            "dimensions": dimensions or ["stat_time_day"],
            "metrics": metrics
            or [
                "spend",
                "impressions",
                "clicks",
                "ctr",
                "cpc",
                "cpm",
                "conversions",
                "cost_per_conversion",
            ],
            "start_date": date_start,
            "end_date": date_end,
            "page_size": 1000,
        }

        resp = await gateway.post("/report/integrated/get/", json_body=body)
        data = resp.get("data", {})
        rows = data.get("list", [])
        report_data = {"rows": rows, "total_rows": len(rows)}

        # Update cache
        if cache:
            cache.report_data = report_data
            cache.expires_at = now + _CACHE_TTL
        else:
            cache = ReportCache(
                ad_account_id=ad_account.id,
                report_type=report_type,
                data_level=data_level,
                date_range_start=date_start,
                date_range_end=date_end,
                report_data=report_data,
                expires_at=now + _CACHE_TTL,
            )
            self._session.add(cache)

        return report_data

    async def create_async_report(
        self,
        ad_account: AdAccount,
        *,
        report_type: str = "BASIC",
        data_level: str = "AUCTION_CAMPAIGN",
        date_start: str,
        date_end: str,
        metrics: list[str] | None = None,
        dimensions: list[str] | None = None,
    ) -> str:
        """Create an async report task. Returns task_id."""
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        body: dict = {
            "advertiser_id": ad_account.advertiser_id,
            "report_type": report_type,
            "data_level": data_level,
            "dimensions": dimensions or ["stat_time_day"],
            "metrics": metrics
            or [
                "spend",
                "impressions",
                "clicks",
                "ctr",
                "cpc",
                "cpm",
                "conversions",
                "cost_per_conversion",
            ],
            "start_date": date_start,
            "end_date": date_end,
        }

        resp = await gateway.post("/report/task/create/", json_body=body)
        data = resp.get("data", {})
        return str(data.get("task_id", ""))

    async def check_async_report(
        self, ad_account: AdAccount, task_id: str
    ) -> dict:
        """Check async report status."""
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        resp = await gateway.get(
            "/report/task/check/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "task_id": task_id,
            },
        )
        data = resp.get("data", {})
        return {
            "task_id": task_id,
            "status": data.get("status", "UNKNOWN"),
            "download_url": data.get("download_url"),
        }

    async def download_async_report(
        self, ad_account: AdAccount, task_id: str
    ) -> dict:
        """Download async report results."""
        account_service = AdAccountService(self._session)
        gateway = await account_service.build_gateway_for_ad_account(ad_account)

        resp = await gateway.get(
            "/report/task/download/",
            params={
                "advertiser_id": ad_account.advertiser_id,
                "task_id": task_id,
            },
        )
        return resp.get("data", {})

    async def _find_cache(
        self,
        ad_account_id: uuid.UUID,
        report_type: str,
        data_level: str,
        date_start: str,
        date_end: str,
    ) -> ReportCache | None:
        result = await self._session.execute(
            select(ReportCache).where(
                ReportCache.ad_account_id == ad_account_id,
                ReportCache.report_type == report_type,
                ReportCache.data_level == data_level,
                ReportCache.date_range_start == date_start,
                ReportCache.date_range_end == date_end,
            )
        )
        return result.scalar_one_or_none()

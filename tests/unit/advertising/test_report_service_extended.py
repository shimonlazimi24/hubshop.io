"""Tests for ReportService extended methods — cancel async, GMV Max report."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.advertising.services.report_service import ReportService


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock()
    return session


@pytest.fixture
def sample_ad_account() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        advertiser_id="111222333",
        connected_account_id=uuid.uuid4(),
    )


class TestCancelAsyncReport:
    @pytest.mark.asyncio
    async def test_cancel_async_report_calls_api(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {"data": {}}

        with patch(
            "backend.modules.advertising.services.report_service.AdAccountService"
        ) as mock_acct_cls:
            mock_acct = AsyncMock()
            mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
            mock_acct_cls.return_value = mock_acct

            service = ReportService(mock_session)
            result = await service.cancel_async_report(sample_ad_account, "task_abc")

        assert result["task_id"] == "task_abc"
        assert result["cancelled"] is True
        mock_gateway.post.assert_called_once_with(
            "/report/task/cancel/",
            json_body={
                "advertiser_id": sample_ad_account.advertiser_id,
                "task_id": "task_abc",
            },
        )

    @pytest.mark.asyncio
    async def test_cancel_returns_api_data(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {"data": {"message": "cancelled"}}

        with patch(
            "backend.modules.advertising.services.report_service.AdAccountService"
        ) as mock_acct_cls:
            mock_acct = AsyncMock()
            mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
            mock_acct_cls.return_value = mock_acct

            service = ReportService(mock_session)
            result = await service.cancel_async_report(sample_ad_account, "task_xyz")

        assert result["data"] == {"message": "cancelled"}


class TestGetGmvMaxReport:
    @pytest.mark.asyncio
    async def test_gmv_max_report_basic(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {
                        "dimensions": {"stat_time_day": "2025-01-01"},
                        "metrics": {"gmv": "1000.00", "roas": "3.5"},
                    }
                ]
            }
        }

        with patch(
            "backend.modules.advertising.services.report_service.AdAccountService"
        ) as mock_acct_cls:
            mock_acct = AsyncMock()
            mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
            mock_acct_cls.return_value = mock_acct

            service = ReportService(mock_session)
            result = await service.get_gmv_max_report(
                sample_ad_account,
                date_start="2025-01-01",
                date_end="2025-01-31",
            )

        assert result["total_rows"] == 1
        assert result["rows"][0]["metrics"]["gmv"] == "1000.00"

    @pytest.mark.asyncio
    async def test_gmv_max_report_with_params(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {"data": {"list": []}}

        with patch(
            "backend.modules.advertising.services.report_service.AdAccountService"
        ) as mock_acct_cls:
            mock_acct = AsyncMock()
            mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
            mock_acct_cls.return_value = mock_acct

            service = ReportService(mock_session)
            result = await service.get_gmv_max_report(
                sample_ad_account,
                date_start="2025-01-01",
                date_end="2025-01-31",
                metrics=["gmv", "roas"],
                dimensions=["stat_time_day"],
                campaign_ids=["camp_1", "camp_2"],
            )

        assert result["total_rows"] == 0
        assert result["rows"] == []

        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id
        assert call_params["start_date"] == "2025-01-01"
        assert call_params["end_date"] == "2025-01-31"

    @pytest.mark.asyncio
    async def test_gmv_max_report_empty_data(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {"data": {}}

        with patch(
            "backend.modules.advertising.services.report_service.AdAccountService"
        ) as mock_acct_cls:
            mock_acct = AsyncMock()
            mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
            mock_acct_cls.return_value = mock_acct

            service = ReportService(mock_session)
            result = await service.get_gmv_max_report(
                sample_ad_account,
                date_start="2025-01-01",
                date_end="2025-01-31",
            )

        assert result == {"rows": [], "total_rows": 0}

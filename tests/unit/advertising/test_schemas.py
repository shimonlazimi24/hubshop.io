"""Tests for advertising Pydantic schemas - validation and serialization."""

from datetime import datetime, timezone

import pytest

from backend.modules.advertising.schemas import (
    AdAccountResponse,
    AdDetailResponse,
    AdGroupDetailResponse,
    AdGroupSummaryResponse,
    AdSummaryResponse,
    AsyncReportStatusResponse,
    AsyncReportTaskResponse,
    CampaignDetailResponse,
    CampaignSummaryResponse,
    CreateAdGroupRequest,
    CreateAdRequest,
    CreateCampaignRequest,
    ReportRequest,
    ReportResponse,
    ReportRowResponse,
    StatusUpdateRequest,
    UpdateAdGroupRequest,
    UpdateAdRequest,
    UpdateCampaignRequest,
)


class TestAdAccountResponse:
    def test_from_attributes(self) -> None:
        now = datetime.now(tz=timezone.utc)
        resp = AdAccountResponse.model_validate(
            {
                "id": "abc-123",
                "advertiser_id": "111222333",
                "advertiser_name": "Test Advertiser",
                "currency": "USD",
                "timezone": "America/New_York",
                "last_sync_at": now,
                "created_at": now,
            }
        )
        assert resp.advertiser_id == "111222333"
        assert resp.currency == "USD"

    def test_nullable_fields(self) -> None:
        now = datetime.now(tz=timezone.utc)
        resp = AdAccountResponse.model_validate(
            {
                "id": "abc-123",
                "advertiser_id": "111222333",
                "advertiser_name": "Test",
                "currency": None,
                "timezone": None,
                "last_sync_at": None,
                "created_at": now,
            }
        )
        assert resp.currency is None
        assert resp.timezone is None
        assert resp.last_sync_at is None


class TestCampaignSchemas:
    def test_summary_response(self) -> None:
        now = datetime.now(tz=timezone.utc)
        resp = CampaignSummaryResponse.model_validate(
            {
                "id": "camp-1",
                "platform_campaign_id": "12345",
                "campaign_name": "Test Campaign",
                "objective_type": "TRAFFIC",
                "budget_mode": "BUDGET_MODE_DAY",
                "budget": "100.00",
                "operation_status": "ENABLE",
                "secondary_status": "CAMPAIGN_STATUS_BUDGET_EXCEED",
                "created_at": now,
                "updated_at": now,
            }
        )
        assert resp.campaign_name == "Test Campaign"
        assert resp.budget == "100.00"

    def test_detail_includes_json(self) -> None:
        now = datetime.now(tz=timezone.utc)
        resp = CampaignDetailResponse.model_validate(
            {
                "id": "camp-1",
                "platform_campaign_id": "12345",
                "campaign_name": "Test",
                "operation_status": "ENABLE",
                "detail_json": {"extra": "data"},
                "created_at": now,
                "updated_at": now,
            }
        )
        assert resp.detail_json == {"extra": "data"}

    def test_create_request_required_fields(self) -> None:
        req = CreateCampaignRequest(
            ad_account_id="111",
            campaign_name="New Campaign",
            objective_type="CONVERSIONS",
            budget_mode="BUDGET_MODE_TOTAL",
        )
        assert req.budget is None

    def test_create_request_with_budget(self) -> None:
        req = CreateCampaignRequest(
            ad_account_id="111",
            campaign_name="Budget Campaign",
            objective_type="TRAFFIC",
            budget_mode="BUDGET_MODE_DAY",
            budget="50.00",
        )
        assert req.budget == "50.00"

    def test_update_request_partial(self) -> None:
        req = UpdateCampaignRequest(campaign_name="Updated Name")
        assert req.campaign_name == "Updated Name"
        assert req.budget_mode is None
        assert req.budget is None


class TestAdGroupSchemas:
    def test_summary_response(self) -> None:
        now = datetime.now(tz=timezone.utc)
        resp = AdGroupSummaryResponse.model_validate(
            {
                "id": "ag-1",
                "platform_adgroup_id": "67890",
                "adgroup_name": "Test Ad Group",
                "placement_type": "PLACEMENT_TYPE_AUTOMATIC",
                "bid_type": "BID_TYPE_CUSTOM",
                "bid_amount": "2.50",
                "budget": "500.00",
                "optimization_goal": "CLICK",
                "operation_status": "ENABLE",
                "created_at": now,
                "updated_at": now,
            }
        )
        assert resp.bid_amount == "2.50"
        assert resp.optimization_goal == "CLICK"

    def test_detail_includes_targeting(self) -> None:
        now = datetime.now(tz=timezone.utc)
        targeting = {"location_ids": [123], "age_groups": ["AGE_25_34"]}
        resp = AdGroupDetailResponse.model_validate(
            {
                "id": "ag-1",
                "platform_adgroup_id": "67890",
                "adgroup_name": "Test",
                "operation_status": "ENABLE",
                "targeting_json": targeting,
                "detail_json": {"raw": True},
                "created_at": now,
                "updated_at": now,
            }
        )
        assert resp.targeting_json == targeting

    def test_create_request_defaults(self) -> None:
        req = CreateAdGroupRequest(
            ad_account_id="111",
            campaign_id="222",
            adgroup_name="New Ad Group",
        )
        assert req.placement_type == "PLACEMENT_TYPE_AUTOMATIC"
        assert req.bid_type is None

    def test_update_request_partial(self) -> None:
        targeting = {"location_ids": [456]}
        req = UpdateAdGroupRequest(targeting=targeting, budget="300.00")
        assert req.targeting == targeting
        assert req.adgroup_name is None


class TestAdSchemas:
    def test_summary_response(self) -> None:
        now = datetime.now(tz=timezone.utc)
        resp = AdSummaryResponse.model_validate(
            {
                "id": "ad-1",
                "platform_ad_id": "99999",
                "ad_name": "Test Ad",
                "ad_format": "SINGLE_VIDEO",
                "ad_text": "Buy now!",
                "call_to_action": "SHOP_NOW",
                "landing_page_url": "https://example.com",
                "image_url": "https://example.com/img.jpg",
                "operation_status": "ENABLE",
                "created_at": now,
                "updated_at": now,
            }
        )
        assert resp.ad_format == "SINGLE_VIDEO"
        assert resp.call_to_action == "SHOP_NOW"

    def test_detail_includes_json(self) -> None:
        now = datetime.now(tz=timezone.utc)
        resp = AdDetailResponse.model_validate(
            {
                "id": "ad-1",
                "platform_ad_id": "99999",
                "ad_name": "Test",
                "operation_status": "ENABLE",
                "detail_json": {"creative": "data"},
                "created_at": now,
                "updated_at": now,
            }
        )
        assert resp.detail_json == {"creative": "data"}

    def test_create_request_minimal(self) -> None:
        req = CreateAdRequest(
            ad_account_id="111",
            adgroup_id="222",
            ad_name="New Ad",
        )
        assert req.ad_format is None
        assert req.ad_text is None

    def test_update_request_partial(self) -> None:
        req = UpdateAdRequest(ad_text="Updated text")
        assert req.ad_text == "Updated text"
        assert req.ad_name is None


class TestStatusUpdateRequest:
    def test_basic(self) -> None:
        req = StatusUpdateRequest(operation_status="DISABLE")
        assert req.operation_status == "DISABLE"


class TestReportSchemas:
    def test_report_request(self) -> None:
        req = ReportRequest(
            ad_account_id="111",
            date_start="2026-01-01",
            date_end="2026-01-31",
        )
        assert req.report_type == "BASIC"
        assert req.data_level == "AUCTION_CAMPAIGN"
        assert req.metrics == []

    def test_report_request_custom_metrics(self) -> None:
        req = ReportRequest(
            ad_account_id="111",
            date_start="2026-01-01",
            date_end="2026-01-31",
            metrics=["spend", "clicks"],
            dimensions=["stat_time_day"],
        )
        assert len(req.metrics) == 2

    def test_report_row_response(self) -> None:
        row = ReportRowResponse(
            dimensions={"stat_time_day": "2026-01-15"},
            metrics={"spend": "100.00", "clicks": 50},
        )
        assert row.dimensions["stat_time_day"] == "2026-01-15"

    def test_report_response(self) -> None:
        row = ReportRowResponse(
            dimensions={"stat_time_day": "2026-01-15"},
            metrics={"spend": "100.00"},
        )
        resp = ReportResponse(rows=[row], total_rows=1)
        assert resp.total_rows == 1
        assert len(resp.rows) == 1

    def test_async_report_task(self) -> None:
        resp = AsyncReportTaskResponse(task_id="task-abc-123")
        assert resp.task_id == "task-abc-123"

    def test_async_report_status(self) -> None:
        resp = AsyncReportStatusResponse(
            task_id="task-abc-123",
            status="COMPLETED",
            download_url="https://example.com/download",
        )
        assert resp.status == "COMPLETED"
        assert resp.download_url is not None

    def test_async_report_status_pending(self) -> None:
        resp = AsyncReportStatusResponse(
            task_id="task-abc-123",
            status="PROCESSING",
        )
        assert resp.download_url is None

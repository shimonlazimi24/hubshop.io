"""Tests for advertising schemas with source_platform field."""

from datetime import UTC, datetime

from backend.modules.advertising.schemas import (
    CampaignDetailResponse,
    CampaignSummaryResponse,
)


class TestCampaignSummarySourcePlatform:
    def test_source_platform_defaults_to_marketing(self) -> None:
        data = {
            "id": "abc",
            "platform_campaign_id": "camp_1",
            "campaign_name": "Test",
            "operation_status": "ENABLE",
            "created_at": datetime.now(tz=UTC),
            "updated_at": datetime.now(tz=UTC),
        }
        response = CampaignSummaryResponse(**data)
        assert response.source_platform == "marketing"

    def test_source_platform_can_be_set_to_shop(self) -> None:
        data = {
            "id": "abc",
            "platform_campaign_id": "camp_1",
            "campaign_name": "Test",
            "operation_status": "ENABLE",
            "source_platform": "shop",
            "created_at": datetime.now(tz=UTC),
            "updated_at": datetime.now(tz=UTC),
        }
        response = CampaignSummaryResponse(**data)
        assert response.source_platform == "shop"


class TestCampaignDetailSourcePlatform:
    def test_source_platform_defaults_to_marketing(self) -> None:
        data = {
            "id": "abc",
            "platform_campaign_id": "camp_1",
            "campaign_name": "Test",
            "operation_status": "ENABLE",
            "created_at": datetime.now(tz=UTC),
            "updated_at": datetime.now(tz=UTC),
        }
        response = CampaignDetailResponse(**data)
        assert response.source_platform == "marketing"

    def test_source_platform_can_be_set_to_shop(self) -> None:
        data = {
            "id": "abc",
            "platform_campaign_id": "camp_1",
            "campaign_name": "Test",
            "operation_status": "ENABLE",
            "source_platform": "shop",
            "detail_json": {"some": "data"},
            "created_at": datetime.now(tz=UTC),
            "updated_at": datetime.now(tz=UTC),
        }
        response = CampaignDetailResponse(**data)
        assert response.source_platform == "shop"

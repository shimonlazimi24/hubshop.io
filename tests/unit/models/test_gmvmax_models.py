"""Tests for GMV Max DB models."""

from backend.db.models.gmvmax import (
    CampaignType,
    DraftStatus,
    GmvMaxDraft,
    GmvMaxReport,
)


class TestCampaignTypeEnum:
    """Test CampaignType enum values."""

    def test_product_value(self) -> None:
        assert CampaignType.PRODUCT.value == "PRODUCT"

    def test_live_value(self) -> None:
        assert CampaignType.LIVE.value == "LIVE"

    def test_member_count(self) -> None:
        assert len(CampaignType) == 2


class TestDraftStatusEnum:
    """Test DraftStatus enum values."""

    def test_draft_value(self) -> None:
        assert DraftStatus.DRAFT.value == "DRAFT"

    def test_submitted_value(self) -> None:
        assert DraftStatus.SUBMITTED.value == "SUBMITTED"

    def test_linked_value(self) -> None:
        assert DraftStatus.LINKED.value == "LINKED"

    def test_archived_value(self) -> None:
        assert DraftStatus.ARCHIVED.value == "ARCHIVED"

    def test_member_count(self) -> None:
        assert len(DraftStatus) == 4


class TestGmvMaxDraft:
    """Test GmvMaxDraft model schema."""

    def test_tablename(self) -> None:
        assert GmvMaxDraft.__tablename__ == "gmvmax_drafts"

    def test_columns(self) -> None:
        columns = GmvMaxDraft.__table__.columns.keys()
        expected = [
            "id",
            "workspace_id",
            "campaign_type",
            "product_ids",
            "daily_budget",
            "roi_target",
            "status",
            "ads_manager_campaign_id",
            "created_by",
            "notes",
            "created_at",
            "updated_at",
        ]
        for col in expected:
            assert col in columns, f"Missing column: {col}"

    def test_workspace_id_indexed(self) -> None:
        col = GmvMaxDraft.__table__.columns["workspace_id"]
        assert col.index is True

    def test_status_default_is_draft(self) -> None:
        col = GmvMaxDraft.__table__.columns["status"]
        assert col.default is not None
        assert col.default.arg == DraftStatus.DRAFT

    def test_ads_manager_campaign_id_nullable(self) -> None:
        col = GmvMaxDraft.__table__.columns["ads_manager_campaign_id"]
        assert col.nullable is True

    def test_has_composite_index(self) -> None:
        indexes = GmvMaxDraft.__table__.indexes
        index_names = {idx.name for idx in indexes}
        assert "ix_gmvmax_drafts_workspace_status" in index_names


class TestGmvMaxReport:
    """Test GmvMaxReport model schema."""

    def test_tablename(self) -> None:
        assert GmvMaxReport.__tablename__ == "gmvmax_reports"

    def test_columns(self) -> None:
        columns = GmvMaxReport.__table__.columns.keys()
        expected = [
            "id",
            "workspace_id",
            "campaign_id",
            "draft_id",
            "report_date",
            "spend",
            "total_gmv",
            "paid_gmv",
            "organic_gmv",
            "orders",
            "roi",
            "impressions",
            "clicks",
            "created_at",
            "updated_at",
        ]
        for col in expected:
            assert col in columns, f"Missing column: {col}"

    def test_workspace_id_indexed(self) -> None:
        col = GmvMaxReport.__table__.columns["workspace_id"]
        assert col.index is True

    def test_draft_id_nullable(self) -> None:
        col = GmvMaxReport.__table__.columns["draft_id"]
        assert col.nullable is True

    def test_has_composite_index(self) -> None:
        indexes = GmvMaxReport.__table__.indexes
        index_names = {idx.name for idx in indexes}
        assert "ix_gmvmax_reports_workspace_date" in index_names


class TestGmvMaxModelsInInit:
    """Verify models are exported from backend.db.models."""

    def test_draft_importable(self) -> None:
        from backend.db.models import GmvMaxDraft  # noqa: F401

    def test_report_importable(self) -> None:
        from backend.db.models import GmvMaxReport  # noqa: F401

    def test_campaign_type_importable(self) -> None:
        from backend.db.models import CampaignType  # noqa: F401

    def test_draft_status_importable(self) -> None:
        from backend.db.models import DraftStatus  # noqa: F401

"""Tests for Shop Health DB models — SpsSnapshot, ViolationRecord, HealthAlert, UnifiedDailyMetrics."""

from backend.db.models.shop_health import (
    HealthAlert,
    SpsSnapshot,
    UnifiedDailyMetrics,
    ViolationRecord,
)


class TestSpsSnapshot:
    """Test SpsSnapshot model schema."""

    def test_tablename(self) -> None:
        assert SpsSnapshot.__tablename__ == "sps_snapshots"

    def test_columns(self) -> None:
        columns = SpsSnapshot.__table__.columns.keys()
        expected = [
            "id",
            "workspace_id",
            "shop_id",
            "date",
            "estimated_score",
            "return_rate",
            "cancellation_rate",
            "otdr",
            "im_dissatisfaction_rate",
            "after_sales_handling_hours",
            "review_rate",
            "settlement_tier_eligible",
            "created_at",
            "updated_at",
        ]
        for col in expected:
            assert col in columns, f"Missing column: {col}"

    def test_workspace_id_indexed(self) -> None:
        col = SpsSnapshot.__table__.columns["workspace_id"]
        assert col.index is True or any(
            col.name in [c.name for c in idx.columns]
            for idx in SpsSnapshot.__table__.indexes
        )

    def test_shop_id_indexed(self) -> None:
        col = SpsSnapshot.__table__.columns["shop_id"]
        assert col.index is True or any(
            col.name in [c.name for c in idx.columns]
            for idx in SpsSnapshot.__table__.indexes
        )

    def test_has_composite_index(self) -> None:
        indexes = SpsSnapshot.__table__.indexes
        index_names = {idx.name for idx in indexes}
        assert "ix_sps_snapshots_workspace_date" in index_names

    def test_nullable_fields(self) -> None:
        table = SpsSnapshot.__table__
        assert table.columns["return_rate"].nullable is True
        assert table.columns["cancellation_rate"].nullable is True
        assert table.columns["otdr"].nullable is True
        assert table.columns["im_dissatisfaction_rate"].nullable is True
        assert table.columns["after_sales_handling_hours"].nullable is True
        assert table.columns["review_rate"].nullable is True
        assert table.columns["settlement_tier_eligible"].nullable is True

    def test_non_nullable_fields(self) -> None:
        table = SpsSnapshot.__table__
        assert table.columns["workspace_id"].nullable is False
        assert table.columns["shop_id"].nullable is False
        assert table.columns["date"].nullable is False
        assert table.columns["estimated_score"].nullable is False


class TestViolationRecord:
    """Test ViolationRecord model schema."""

    def test_tablename(self) -> None:
        assert ViolationRecord.__tablename__ == "violation_records"

    def test_columns(self) -> None:
        columns = ViolationRecord.__table__.columns.keys()
        expected = [
            "id",
            "workspace_id",
            "shop_id",
            "violation_type",
            "points",
            "description",
            "occurred_at",
            "expires_at",
            "resolved",
            "source",
            "detail_json",
            "created_at",
            "updated_at",
        ]
        for col in expected:
            assert col in columns, f"Missing column: {col}"

    def test_has_composite_index(self) -> None:
        indexes = ViolationRecord.__table__.indexes
        index_names = {idx.name for idx in indexes}
        assert "ix_violations_workspace_resolved" in index_names

    def test_nullable_fields(self) -> None:
        table = ViolationRecord.__table__
        assert table.columns["detail_json"].nullable is True

    def test_non_nullable_fields(self) -> None:
        table = ViolationRecord.__table__
        assert table.columns["workspace_id"].nullable is False
        assert table.columns["shop_id"].nullable is False
        assert table.columns["violation_type"].nullable is False
        assert table.columns["points"].nullable is False
        assert table.columns["description"].nullable is False
        assert table.columns["occurred_at"].nullable is False
        assert table.columns["expires_at"].nullable is False
        assert table.columns["resolved"].nullable is False
        assert table.columns["source"].nullable is False

    def test_resolved_default_false(self) -> None:
        col = ViolationRecord.__table__.columns["resolved"]
        assert col.default is not None


class TestHealthAlert:
    """Test HealthAlert model schema."""

    def test_tablename(self) -> None:
        assert HealthAlert.__tablename__ == "health_alerts"

    def test_columns(self) -> None:
        columns = HealthAlert.__table__.columns.keys()
        expected = [
            "id",
            "workspace_id",
            "shop_id",
            "alert_type",
            "severity",
            "message",
            "metric_name",
            "current_value",
            "threshold_value",
            "triggered_at",
            "acknowledged_at",
            "created_at",
            "updated_at",
        ]
        for col in expected:
            assert col in columns, f"Missing column: {col}"

    def test_has_composite_index(self) -> None:
        indexes = HealthAlert.__table__.indexes
        index_names = {idx.name for idx in indexes}
        assert "ix_health_alerts_workspace_severity" in index_names

    def test_nullable_fields(self) -> None:
        table = HealthAlert.__table__
        assert table.columns["acknowledged_at"].nullable is True

    def test_non_nullable_fields(self) -> None:
        table = HealthAlert.__table__
        assert table.columns["workspace_id"].nullable is False
        assert table.columns["shop_id"].nullable is False
        assert table.columns["alert_type"].nullable is False
        assert table.columns["severity"].nullable is False
        assert table.columns["message"].nullable is False
        assert table.columns["metric_name"].nullable is False
        assert table.columns["current_value"].nullable is False
        assert table.columns["threshold_value"].nullable is False
        assert table.columns["triggered_at"].nullable is False


class TestUnifiedDailyMetrics:
    """Test UnifiedDailyMetrics model schema."""

    def test_tablename(self) -> None:
        assert UnifiedDailyMetrics.__tablename__ == "unified_daily_metrics"

    def test_columns(self) -> None:
        columns = UnifiedDailyMetrics.__table__.columns.keys()
        expected = [
            "id",
            "workspace_id",
            "shop_id",
            "date",
            "total_gmv",
            "order_count",
            "return_count",
            "cancellation_count",
            "avg_order_value",
            "affiliate_gmv",
            "paid_gmv",
            "organic_gmv",
            "cs_response_rate",
            "active_promotions",
            "active_campaigns",
            "created_at",
            "updated_at",
        ]
        for col in expected:
            assert col in columns, f"Missing column: {col}"

    def test_has_unique_composite_index(self) -> None:
        indexes = UnifiedDailyMetrics.__table__.indexes
        found = False
        for idx in indexes:
            if idx.name == "ix_unified_metrics_workspace_date":
                found = True
                assert idx.unique is True
        assert found, "Missing unique composite index ix_unified_metrics_workspace_date"

    def test_nullable_fields(self) -> None:
        table = UnifiedDailyMetrics.__table__
        assert table.columns["avg_order_value"].nullable is True
        assert table.columns["affiliate_gmv"].nullable is True
        assert table.columns["paid_gmv"].nullable is True
        assert table.columns["organic_gmv"].nullable is True
        assert table.columns["cs_response_rate"].nullable is True

    def test_non_nullable_fields(self) -> None:
        table = UnifiedDailyMetrics.__table__
        assert table.columns["workspace_id"].nullable is False
        assert table.columns["shop_id"].nullable is False
        assert table.columns["date"].nullable is False
        assert table.columns["total_gmv"].nullable is False
        assert table.columns["order_count"].nullable is False
        assert table.columns["return_count"].nullable is False
        assert table.columns["cancellation_count"].nullable is False

    def test_default_values(self) -> None:
        table = UnifiedDailyMetrics.__table__
        assert table.columns["active_promotions"].default is not None
        assert table.columns["active_campaigns"].default is not None


class TestImportsFromInit:
    """Verify models are exported from backend.db.models.__init__."""

    def test_sps_snapshot_importable(self) -> None:
        from backend.db.models import SpsSnapshot as imported

        assert imported is SpsSnapshot

    def test_violation_record_importable(self) -> None:
        from backend.db.models import ViolationRecord as imported

        assert imported is ViolationRecord

    def test_health_alert_importable(self) -> None:
        from backend.db.models import HealthAlert as imported

        assert imported is HealthAlert

    def test_unified_daily_metrics_importable(self) -> None:
        from backend.db.models import UnifiedDailyMetrics as imported

        assert imported is UnifiedDailyMetrics

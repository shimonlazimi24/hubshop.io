"""Tests for Settlement model — Phase B1 fields."""

from backend.db.models.finance import Settlement


class TestSettlementModel:
    """Test Settlement model schema has Phase B1 columns."""

    def test_tablename(self) -> None:
        assert Settlement.__tablename__ == "settlements"

    def test_original_columns_present(self) -> None:
        columns = Settlement.__table__.columns.keys()
        original = [
            "id",
            "workspace_id",
            "shop_id",
            "platform_settlement_id",
            "amount",
            "currency",
            "status",
            "period_start",
            "period_end",
            "detail_json",
            "created_at",
            "updated_at",
        ]
        for col in original:
            assert col in columns, f"Missing original column: {col}"

    def test_net_sales_column(self) -> None:
        columns = Settlement.__table__.columns.keys()
        assert "net_sales" in columns

    def test_shipping_total_column(self) -> None:
        columns = Settlement.__table__.columns.keys()
        assert "shipping_total" in columns

    def test_fees_total_column(self) -> None:
        columns = Settlement.__table__.columns.keys()
        assert "fees_total" in columns

    def test_adjustments_total_column(self) -> None:
        columns = Settlement.__table__.columns.keys()
        assert "adjustments_total" in columns

    def test_payout_amount_column(self) -> None:
        columns = Settlement.__table__.columns.keys()
        assert "payout_amount" in columns

    def test_settlement_tier_column(self) -> None:
        columns = Settlement.__table__.columns.keys()
        assert "settlement_tier" in columns

    def test_new_columns_are_nullable(self) -> None:
        """New columns should be nullable so existing rows are not broken."""
        table = Settlement.__table__
        for col_name in [
            "net_sales",
            "shipping_total",
            "fees_total",
            "adjustments_total",
            "payout_amount",
            "settlement_tier",
        ]:
            col = table.columns[col_name]
            assert col.nullable is True, f"{col_name} should be nullable"

    def test_composite_index_exists(self) -> None:
        indexes = Settlement.__table__.indexes
        index_names = {idx.name for idx in indexes}
        assert "ix_settlements_workspace_status" in index_names

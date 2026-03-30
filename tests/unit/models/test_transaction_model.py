"""Tests for Transaction model — Phase B2 fields."""

from backend.db.models.finance import Transaction


class TestTransactionModel:
    """Test Transaction model schema has Phase B2 columns."""

    def test_tablename(self) -> None:
        assert Transaction.__tablename__ == "transactions"

    def test_original_columns_present(self) -> None:
        columns = Transaction.__table__.columns.keys()
        original = [
            "id",
            "workspace_id",
            "shop_id",
            "platform_transaction_id",
            "transaction_type",
            "amount",
            "currency",
            "order_id",
            "detail_json",
            "created_at",
            "updated_at",
        ]
        for col in original:
            assert col in columns, f"Missing original column: {col}"

    def test_fee_breakdown_column(self) -> None:
        columns = Transaction.__table__.columns.keys()
        assert "fee_breakdown" in columns

    def test_fee_breakdown_is_jsonb(self) -> None:
        col = Transaction.__table__.columns["fee_breakdown"]
        assert "JSON" in str(col.type)

    def test_net_amount_column(self) -> None:
        columns = Transaction.__table__.columns.keys()
        assert "net_amount" in columns

    def test_sku_id_column(self) -> None:
        columns = Transaction.__table__.columns.keys()
        assert "sku_id" in columns

    def test_new_columns_are_nullable(self) -> None:
        """New columns should be nullable so existing rows are not broken."""
        table = Transaction.__table__
        for col_name in ["fee_breakdown", "net_amount", "sku_id"]:
            col = table.columns[col_name]
            assert col.nullable is True, f"{col_name} should be nullable"

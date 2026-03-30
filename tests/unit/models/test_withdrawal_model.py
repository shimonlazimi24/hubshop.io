"""Tests for Withdrawal model — Phase B3."""

from backend.db.models.finance import Withdrawal


class TestWithdrawalModel:
    """Test Withdrawal model schema."""

    def test_tablename(self) -> None:
        assert Withdrawal.__tablename__ == "withdrawals"

    def test_columns(self) -> None:
        columns = Withdrawal.__table__.columns.keys()
        expected = [
            "id",
            "workspace_id",
            "shop_id",
            "platform_withdrawal_id",
            "amount",
            "currency",
            "status",
            "requested_at",
            "completed_at",
            "detail_json",
            "created_at",
            "updated_at",
        ]
        for col in expected:
            assert col in columns, f"Missing column: {col}"

    def test_platform_withdrawal_id_is_unique(self) -> None:
        col = Withdrawal.__table__.columns["platform_withdrawal_id"]
        assert col.unique is True

    def test_workspace_id_is_indexed(self) -> None:
        col = Withdrawal.__table__.columns["workspace_id"]
        assert col.index is True

    def test_shop_id_is_indexed(self) -> None:
        col = Withdrawal.__table__.columns["shop_id"]
        assert col.index is True

    def test_requested_at_is_nullable(self) -> None:
        col = Withdrawal.__table__.columns["requested_at"]
        assert col.nullable is True

    def test_completed_at_is_nullable(self) -> None:
        col = Withdrawal.__table__.columns["completed_at"]
        assert col.nullable is True

    def test_detail_json_is_nullable(self) -> None:
        col = Withdrawal.__table__.columns["detail_json"]
        assert col.nullable is True

    def test_status_not_nullable(self) -> None:
        col = Withdrawal.__table__.columns["status"]
        assert col.nullable is False


class TestWithdrawalImportFromInit:
    """Test Withdrawal is importable from the models package."""

    def test_import_from_package(self) -> None:
        from backend.db.models import Withdrawal as W

        assert W is Withdrawal

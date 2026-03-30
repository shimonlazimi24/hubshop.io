"""Tests for FinanceAnalyticsService — Phase B4."""

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.modules.commerce.services.finance_analytics import (
    FinanceAnalyticsService,
)


class TestGetRevenueSummary:
    @pytest.mark.asyncio
    async def test_calculates_totals(self) -> None:
        workspace_id = uuid.uuid4()
        session = AsyncMock()

        # Query 1: settlement rows
        settlement_result = MagicMock()
        settlement_result.all.return_value = [
            SimpleNamespace(payout_amount="1000.00", currency="USD"),
            SimpleNamespace(payout_amount="500.00", currency="USD"),
        ]

        # Query 2: transaction count
        txn_count_result = MagicMock()
        txn_count_result.scalar_one.return_value = 25

        # Query 3: total transaction amount
        txn_sum_result = MagicMock()
        txn_sum_result.all.return_value = [("200.00",), ("150.00",), ("50.00",)]

        call_count = 0

        async def mock_execute(query):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return settlement_result
            elif call_count == 2:
                return txn_count_result
            else:
                return txn_sum_result

        session.execute = mock_execute

        service = FinanceAnalyticsService(session)
        result = await service.get_revenue_summary(
            workspace_id,
            period_start=datetime(2026, 1, 1, tzinfo=UTC),
            period_end=datetime(2026, 1, 31, tzinfo=UTC),
        )

        assert result["total_payout"] == "1500.00"
        assert result["total_transactions"] == 25
        assert result["total_transaction_amount"] == "400.00"
        assert "period_start" in result
        assert "period_end" in result

    @pytest.mark.asyncio
    async def test_handles_no_data(self) -> None:
        workspace_id = uuid.uuid4()
        session = AsyncMock()

        settlement_result = MagicMock()
        settlement_result.all.return_value = []

        txn_count_result = MagicMock()
        txn_count_result.scalar_one.return_value = 0

        txn_sum_result = MagicMock()
        txn_sum_result.all.return_value = []

        call_count = 0

        async def mock_execute(query):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return settlement_result
            elif call_count == 2:
                return txn_count_result
            else:
                return txn_sum_result

        session.execute = mock_execute

        service = FinanceAnalyticsService(session)
        result = await service.get_revenue_summary(
            workspace_id,
            period_start=datetime(2026, 1, 1, tzinfo=UTC),
            period_end=datetime(2026, 1, 31, tzinfo=UTC),
        )

        assert result["total_payout"] == "0.00"
        assert result["total_transactions"] == 0
        assert result["total_transaction_amount"] == "0.00"


class TestGetFeeBreakdown:
    @pytest.mark.asyncio
    async def test_aggregates_fees(self) -> None:
        workspace_id = uuid.uuid4()
        session = AsyncMock()

        mock_result = MagicMock()
        mock_result.all.return_value = [
            SimpleNamespace(transaction_type="COMMISSION", total="120.50", count=10),
            SimpleNamespace(transaction_type="SHIPPING_FEE", total="45.00", count=5),
            SimpleNamespace(transaction_type="PLATFORM_FEE", total="30.00", count=8),
        ]
        session.execute.return_value = mock_result

        service = FinanceAnalyticsService(session)
        result = await service.get_fee_breakdown(
            workspace_id,
            period_start=datetime(2026, 1, 1, tzinfo=UTC),
            period_end=datetime(2026, 1, 31, tzinfo=UTC),
        )

        assert len(result) == 3
        assert result[0]["transaction_type"] == "COMMISSION"
        assert result[0]["total"] == "120.50"
        assert result[0]["count"] == 10

    @pytest.mark.asyncio
    async def test_handles_empty(self) -> None:
        workspace_id = uuid.uuid4()
        session = AsyncMock()

        mock_result = MagicMock()
        mock_result.all.return_value = []
        session.execute.return_value = mock_result

        service = FinanceAnalyticsService(session)
        result = await service.get_fee_breakdown(
            workspace_id,
            period_start=datetime(2026, 1, 1, tzinfo=UTC),
            period_end=datetime(2026, 1, 31, tzinfo=UTC),
        )

        assert result == []

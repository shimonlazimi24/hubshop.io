"""Tests for CommerceAnalyticsService - aggregation queries with mock data."""

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.modules.commerce.services.analytics_service import CommerceAnalyticsService


class TestGetRevenueSummary:
    @pytest.mark.asyncio
    async def test_calculates_summary(self) -> None:
        workspace_id = uuid.uuid4()
        session = AsyncMock()

        # Mock: total_orders=10 (result.one() returns a row with .total_orders)
        count_result = MagicMock()
        count_result.one.return_value = SimpleNamespace(total_orders=10, raw_total=None)

        # Mock: amounts (result.all() returns list of tuples)
        amounts_result = MagicMock()
        amounts_result.all.return_value = [("100.00",), ("200.00",), ("50.00",)]

        # Mock: return count=1
        return_count_result = MagicMock()
        return_count_result.scalar_one.return_value = 1

        # Mock: all orders=10
        all_orders_result = MagicMock()
        all_orders_result.scalar_one.return_value = 10

        call_count = 0

        async def mock_execute(query):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return count_result
            elif call_count == 2:
                return amounts_result
            elif call_count == 3:
                return return_count_result
            else:
                return all_orders_result

        session.execute = mock_execute

        service = CommerceAnalyticsService(session)
        result = await service.get_revenue_summary(
            workspace_id,
            period_start=datetime(2026, 1, 1, tzinfo=timezone.utc),
            period_end=datetime(2026, 1, 31, tzinfo=timezone.utc),
        )

        assert result["total_revenue"] == "350.00"
        assert result["return_rate"] == 0.1

    @pytest.mark.asyncio
    async def test_handles_zero_orders(self) -> None:
        workspace_id = uuid.uuid4()
        session = AsyncMock()

        count_result = MagicMock()
        count_result.one.return_value = SimpleNamespace(total_orders=0, raw_total=None)

        amounts_result = MagicMock()
        amounts_result.all.return_value = []

        return_count_result = MagicMock()
        return_count_result.scalar_one.return_value = 0

        all_orders_result = MagicMock()
        all_orders_result.scalar_one.return_value = 0

        call_count = 0

        async def mock_execute(query):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return count_result
            elif call_count == 2:
                return amounts_result
            elif call_count == 3:
                return return_count_result
            else:
                return all_orders_result

        session.execute = mock_execute

        service = CommerceAnalyticsService(session)
        result = await service.get_revenue_summary(
            workspace_id,
            period_start=datetime(2026, 1, 1, tzinfo=timezone.utc),
            period_end=datetime(2026, 1, 31, tzinfo=timezone.utc),
        )

        assert result["total_revenue"] == "0.00"
        assert result["total_orders"] == 0
        assert result["average_order_value"] == "0.00"
        assert result["return_rate"] == 0.0


class TestGetOrderStatusDistribution:
    @pytest.mark.asyncio
    async def test_calculates_distribution(self) -> None:
        workspace_id = uuid.uuid4()
        session = AsyncMock()

        # Mock rows with .status and .count attributes
        mock_result = MagicMock()
        mock_result.all.return_value = [
            SimpleNamespace(status="completed", count=50),
            SimpleNamespace(status="in_transit", count=30),
            SimpleNamespace(status="cancelled", count=20),
        ]
        session.execute.return_value = mock_result

        service = CommerceAnalyticsService(session)
        result = await service.get_order_status_distribution(workspace_id)

        assert len(result) == 3
        assert result[0]["status"] == "completed"
        assert result[0]["count"] == 50
        assert result[0]["percentage"] == 50.0
        assert result[1]["percentage"] == 30.0
        assert result[2]["percentage"] == 20.0

    @pytest.mark.asyncio
    async def test_handles_empty(self) -> None:
        workspace_id = uuid.uuid4()
        session = AsyncMock()

        mock_result = MagicMock()
        mock_result.all.return_value = []
        session.execute.return_value = mock_result

        service = CommerceAnalyticsService(session)
        result = await service.get_order_status_distribution(workspace_id)

        assert result == []

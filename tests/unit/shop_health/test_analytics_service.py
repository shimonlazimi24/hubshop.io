"""Tests for UnifiedAnalyticsService — daily metrics calculation and history."""

import uuid
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.modules.shop_health.services.analytics_service import (
    UnifiedAnalyticsService,
)


class TestCalculateDailyMetrics:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.fixture
    def shop_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_returns_metrics_object(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> None:
        """calculate_daily_metrics should return a UnifiedDailyMetrics instance."""
        session = AsyncMock()
        session.add = MagicMock()
        session.merge = AsyncMock()

        # Mock query results: gmv, order_count, return_count, cancel_count,
        # active_promotions, active_campaigns
        gmv_result = MagicMock()
        gmv_result.scalar_one.return_value = "12500.00"

        order_count_result = MagicMock()
        order_count_result.scalar_one.return_value = 150

        return_count_result = MagicMock()
        return_count_result.scalar_one.return_value = 5

        cancel_count_result = MagicMock()
        cancel_count_result.scalar_one.return_value = 3

        promo_count_result = MagicMock()
        promo_count_result.scalar_one.return_value = 2

        campaign_count_result = MagicMock()
        campaign_count_result.scalar_one.return_value = 4

        session.execute = AsyncMock(
            side_effect=[
                gmv_result,
                order_count_result,
                return_count_result,
                cancel_count_result,
                promo_count_result,
                campaign_count_result,
            ]
        )

        service = UnifiedAnalyticsService(session)
        metrics = await service.calculate_daily_metrics(
            workspace_id, shop_id, date(2026, 3, 30)
        )

        assert metrics.workspace_id == workspace_id
        assert metrics.shop_id == shop_id
        assert metrics.date == date(2026, 3, 30)
        assert metrics.total_gmv == "12500.00"
        assert metrics.order_count == 150
        assert metrics.return_count == 5
        assert metrics.cancellation_count == 3
        assert metrics.active_promotions == 2
        assert metrics.active_campaigns == 4

    @pytest.mark.asyncio
    async def test_calculates_avg_order_value(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> None:
        """avg_order_value should be total_gmv / order_count when orders > 0."""
        session = AsyncMock()
        session.add = MagicMock()
        session.merge = AsyncMock()

        gmv_result = MagicMock()
        gmv_result.scalar_one.return_value = "1000.00"

        order_count_result = MagicMock()
        order_count_result.scalar_one.return_value = 10

        return_count_result = MagicMock()
        return_count_result.scalar_one.return_value = 0

        cancel_count_result = MagicMock()
        cancel_count_result.scalar_one.return_value = 0

        promo_count_result = MagicMock()
        promo_count_result.scalar_one.return_value = 0

        campaign_count_result = MagicMock()
        campaign_count_result.scalar_one.return_value = 0

        session.execute = AsyncMock(
            side_effect=[
                gmv_result,
                order_count_result,
                return_count_result,
                cancel_count_result,
                promo_count_result,
                campaign_count_result,
            ]
        )

        service = UnifiedAnalyticsService(session)
        metrics = await service.calculate_daily_metrics(
            workspace_id, shop_id, date(2026, 3, 30)
        )

        assert metrics.avg_order_value == "100.00"

    @pytest.mark.asyncio
    async def test_zero_orders_avg_order_value_none(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> None:
        """avg_order_value should be None when order_count is 0."""
        session = AsyncMock()
        session.add = MagicMock()
        session.merge = AsyncMock()

        gmv_result = MagicMock()
        gmv_result.scalar_one.return_value = "0.00"

        order_count_result = MagicMock()
        order_count_result.scalar_one.return_value = 0

        return_count_result = MagicMock()
        return_count_result.scalar_one.return_value = 0

        cancel_count_result = MagicMock()
        cancel_count_result.scalar_one.return_value = 0

        promo_count_result = MagicMock()
        promo_count_result.scalar_one.return_value = 0

        campaign_count_result = MagicMock()
        campaign_count_result.scalar_one.return_value = 0

        session.execute = AsyncMock(
            side_effect=[
                gmv_result,
                order_count_result,
                return_count_result,
                cancel_count_result,
                promo_count_result,
                campaign_count_result,
            ]
        )

        service = UnifiedAnalyticsService(session)
        metrics = await service.calculate_daily_metrics(
            workspace_id, shop_id, date(2026, 3, 30)
        )

        assert metrics.avg_order_value is None

    @pytest.mark.asyncio
    async def test_persists_to_session(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> None:
        """calculate_daily_metrics should add the metrics to the session."""
        session = AsyncMock()
        session.add = MagicMock()
        session.merge = AsyncMock()

        generic_result = MagicMock()
        generic_result.scalar_one.return_value = 0
        session.execute = AsyncMock(return_value=generic_result)

        service = UnifiedAnalyticsService(session)
        await service.calculate_daily_metrics(workspace_id, shop_id, date(2026, 3, 30))

        session.add.assert_called_once()


class TestGetMetricsHistory:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_returns_list(self, workspace_id: uuid.UUID) -> None:
        """get_metrics_history should return a list of UnifiedDailyMetrics."""
        session = AsyncMock()

        m1 = SimpleNamespace(date=date(2026, 3, 1), total_gmv="500.00", order_count=10)
        m2 = SimpleNamespace(date=date(2026, 3, 2), total_gmv="600.00", order_count=12)

        result = MagicMock()
        result.scalars.return_value.all.return_value = [m1, m2]
        session.execute = AsyncMock(return_value=result)

        service = UnifiedAnalyticsService(session)
        history = await service.get_metrics_history(workspace_id, days=30)

        assert len(history) == 2
        assert history[0].total_gmv == "500.00"

    @pytest.mark.asyncio
    async def test_with_shop_filter(self, workspace_id: uuid.UUID) -> None:
        """get_metrics_history should accept optional shop_id filter."""
        session = AsyncMock()
        shop_id = uuid.uuid4()

        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=result)

        service = UnifiedAnalyticsService(session)
        history = await service.get_metrics_history(
            workspace_id, shop_id=shop_id, days=7
        )

        assert history == []
        session.execute.assert_awaited_once()

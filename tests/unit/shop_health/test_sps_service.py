"""Tests for SpsEstimationService — SPS calculation, snapshots, history."""

import uuid
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.modules.shop_health.services.sps_service import SpsEstimationService


class TestCalculateEstimatedSps:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.fixture
    def shop_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_perfect_shop_returns_score_5(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> None:
        """Shop with zero cancellations, zero returns, 100% on-time => score 5.0."""
        session = AsyncMock()
        # Query responses: total_orders, cancellations, returns, total_shipped, on_time_shipped
        total_orders_result = MagicMock()
        total_orders_result.scalar_one.return_value = 100

        cancellations_result = MagicMock()
        cancellations_result.scalar_one.return_value = 0

        returns_result = MagicMock()
        returns_result.scalar_one.return_value = 0

        total_shipped_result = MagicMock()
        total_shipped_result.scalar_one.return_value = 100

        on_time_result = MagicMock()
        on_time_result.scalar_one.return_value = 100

        session.execute = AsyncMock(
            side_effect=[
                total_orders_result,
                cancellations_result,
                returns_result,
                total_shipped_result,
                on_time_result,
            ]
        )

        service = SpsEstimationService(session)
        metrics = await service.calculate_estimated_sps(workspace_id, shop_id)

        assert float(metrics["estimated_score"]) == 5.0
        assert float(metrics["cancellation_rate"]) == 0.0
        assert float(metrics["return_rate"]) == 0.0
        assert float(metrics["otdr"]) == 100.0

    @pytest.mark.asyncio
    async def test_problematic_shop_returns_low_score(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> None:
        """Shop with high cancellations and returns => low score."""
        session = AsyncMock()

        total_orders_result = MagicMock()
        total_orders_result.scalar_one.return_value = 100

        cancellations_result = MagicMock()
        cancellations_result.scalar_one.return_value = 30  # 30%

        returns_result = MagicMock()
        returns_result.scalar_one.return_value = 20  # 20%

        total_shipped_result = MagicMock()
        total_shipped_result.scalar_one.return_value = 70

        on_time_result = MagicMock()
        on_time_result.scalar_one.return_value = 35  # 50% OTDR

        session.execute = AsyncMock(
            side_effect=[
                total_orders_result,
                cancellations_result,
                returns_result,
                total_shipped_result,
                on_time_result,
            ]
        )

        service = SpsEstimationService(session)
        metrics = await service.calculate_estimated_sps(workspace_id, shop_id)

        score = float(metrics["estimated_score"])
        assert score < 3.5
        assert score >= 0.0

    @pytest.mark.asyncio
    async def test_no_orders_returns_default_score(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> None:
        """No orders in the period => default score of 5.0."""
        session = AsyncMock()

        total_orders_result = MagicMock()
        total_orders_result.scalar_one.return_value = 0

        cancellations_result = MagicMock()
        cancellations_result.scalar_one.return_value = 0

        returns_result = MagicMock()
        returns_result.scalar_one.return_value = 0

        total_shipped_result = MagicMock()
        total_shipped_result.scalar_one.return_value = 0

        on_time_result = MagicMock()
        on_time_result.scalar_one.return_value = 0

        session.execute = AsyncMock(
            side_effect=[
                total_orders_result,
                cancellations_result,
                returns_result,
                total_shipped_result,
                on_time_result,
            ]
        )

        service = SpsEstimationService(session)
        metrics = await service.calculate_estimated_sps(workspace_id, shop_id)

        assert float(metrics["estimated_score"]) == 5.0

    @pytest.mark.asyncio
    async def test_metrics_dict_has_all_keys(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> None:
        """Returned dict must contain all expected metric keys."""
        session = AsyncMock()

        for_result = MagicMock()
        for_result.scalar_one.return_value = 50

        session.execute = AsyncMock(return_value=for_result)

        service = SpsEstimationService(session)
        metrics = await service.calculate_estimated_sps(workspace_id, shop_id)

        expected_keys = {
            "estimated_score",
            "return_rate",
            "cancellation_rate",
            "otdr",
            "total_orders",
            "total_shipped",
        }
        assert expected_keys.issubset(set(metrics.keys()))

    @pytest.mark.asyncio
    async def test_score_clamped_to_0_5(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> None:
        """Score must always be in the 0-5 range."""
        session = AsyncMock()

        # Extreme values
        total_orders_result = MagicMock()
        total_orders_result.scalar_one.return_value = 10

        cancellations_result = MagicMock()
        cancellations_result.scalar_one.return_value = 10  # 100%

        returns_result = MagicMock()
        returns_result.scalar_one.return_value = 10  # 100%

        total_shipped_result = MagicMock()
        total_shipped_result.scalar_one.return_value = 0

        on_time_result = MagicMock()
        on_time_result.scalar_one.return_value = 0  # 0% OTDR

        session.execute = AsyncMock(
            side_effect=[
                total_orders_result,
                cancellations_result,
                returns_result,
                total_shipped_result,
                on_time_result,
            ]
        )

        service = SpsEstimationService(session)
        metrics = await service.calculate_estimated_sps(workspace_id, shop_id)

        score = float(metrics["estimated_score"])
        assert 0.0 <= score <= 5.0


class TestSaveDailySnapshot:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.fixture
    def shop_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_save_creates_snapshot(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> None:
        """save_daily_snapshot should calculate metrics and persist an SpsSnapshot."""
        session = AsyncMock()
        session.add = MagicMock()

        for_result = MagicMock()
        for_result.scalar_one.return_value = 50

        session.execute = AsyncMock(return_value=for_result)

        service = SpsEstimationService(session)
        snapshot = await service.save_daily_snapshot(workspace_id, shop_id)

        session.add.assert_called_once()
        assert snapshot.workspace_id == workspace_id
        assert snapshot.shop_id == shop_id
        assert snapshot.date == date.today()
        assert snapshot.estimated_score is not None


class TestGetSpsHistory:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_returns_snapshots(self, workspace_id: uuid.UUID) -> None:
        """get_sps_history should return list of SpsSnapshot objects."""
        session = AsyncMock()

        snap1 = SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            date=date(2026, 3, 1),
            estimated_score="4.2",
        )
        snap2 = SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            date=date(2026, 3, 2),
            estimated_score="4.3",
        )

        result = MagicMock()
        result.scalars.return_value.all.return_value = [snap1, snap2]
        session.execute = AsyncMock(return_value=result)

        service = SpsEstimationService(session)
        history = await service.get_sps_history(workspace_id, days=30)

        assert len(history) == 2
        assert history[0].estimated_score == "4.2"

    @pytest.mark.asyncio
    async def test_with_shop_filter(self, workspace_id: uuid.UUID) -> None:
        """get_sps_history should accept optional shop_id filter."""
        session = AsyncMock()
        shop_id = uuid.uuid4()

        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=result)

        service = SpsEstimationService(session)
        history = await service.get_sps_history(workspace_id, shop_id=shop_id, days=7)

        assert history == []
        session.execute.assert_awaited_once()

"""Tests for KpiService - overview aggregation, timeseries, snapshots, drill-down."""

import uuid
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.db.models.analytics import UnifiedKpiSnapshot
from backend.modules.analytics.services.kpi_service import KpiService


class TestGetOverview:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_get_overview_aggregates_all_modules(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        session.add = MagicMock()

        # 5 sequential queries: order_count, campaign_count, video_count,
        # total_views, saved_creators
        order_result = MagicMock()
        order_result.scalar_one.return_value = 42

        campaign_result = MagicMock()
        campaign_result.scalar_one.return_value = 5

        video_result = MagicMock()
        video_result.scalar_one.return_value = 120

        views_result = MagicMock()
        views_result.scalar_one.return_value = 99000

        creators_result = MagicMock()
        creators_result.scalar_one.return_value = 8

        session.execute = AsyncMock(
            side_effect=[
                order_result,
                campaign_result,
                video_result,
                views_result,
                creators_result,
            ]
        )

        service = KpiService(session)
        overview = await service.get_overview(workspace_id)

        assert overview["total_orders"] == 42
        assert overview["active_campaigns"] == 5
        assert overview["total_videos"] == 120
        assert overview["total_views"] == 99000
        assert overview["saved_creators"] == 8
        assert set(overview.keys()) == {
            "total_orders",
            "active_campaigns",
            "total_videos",
            "total_views",
            "saved_creators",
        }


class TestGetTimeseries:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_get_timeseries_returns_snapshots(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        snap1 = SimpleNamespace(
            date=date(2026, 2, 18),
            total_orders=10,
            total_revenue="500.00",
            active_campaigns=3,
            total_views=1000,
        )
        snap2 = SimpleNamespace(
            date=date(2026, 2, 19),
            total_orders=12,
            total_revenue="600.00",
            active_campaigns=4,
            total_views=1200,
        )
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [snap1, snap2]
        session.execute = AsyncMock(return_value=result_mock)

        service = KpiService(session)
        timeseries = await service.get_timeseries(workspace_id, days=30)

        assert len(timeseries) == 2
        assert timeseries[0]["date"] == "2026-02-18"
        assert timeseries[0]["total_orders"] == 10
        assert timeseries[0]["total_revenue"] == "500.00"
        assert timeseries[0]["active_campaigns"] == 3
        assert timeseries[0]["total_views"] == 1000
        assert timeseries[1]["date"] == "2026-02-19"

    @pytest.mark.asyncio
    async def test_get_timeseries_empty(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=result_mock)

        service = KpiService(session)
        timeseries = await service.get_timeseries(workspace_id)

        assert timeseries == []


class TestTakeSnapshot:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_take_snapshot_creates_new(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        # get_overview queries (5 results)
        order_result = MagicMock()
        order_result.scalar_one.return_value = 10
        campaign_result = MagicMock()
        campaign_result.scalar_one.return_value = 2
        video_result = MagicMock()
        video_result.scalar_one.return_value = 50
        views_result = MagicMock()
        views_result.scalar_one.return_value = 5000
        creators_result = MagicMock()
        creators_result.scalar_one.return_value = 3

        # Snapshot lookup returns None (no existing snapshot)
        snapshot_result = MagicMock()
        snapshot_result.scalar_one_or_none.return_value = None

        session.execute = AsyncMock(
            side_effect=[
                order_result,
                campaign_result,
                video_result,
                views_result,
                creators_result,
                snapshot_result,
            ]
        )

        service = KpiService(session)
        snapshot = await service.take_snapshot(workspace_id)

        assert session.add.called
        added = session.add.call_args_list[0][0][0]
        assert isinstance(added, UnifiedKpiSnapshot)
        assert added.total_orders == 10
        assert added.active_campaigns == 2
        assert added.total_videos == 50
        assert added.total_views == 5000
        assert added.saved_creators == 3

    @pytest.mark.asyncio
    async def test_take_snapshot_updates_existing(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        session.add = MagicMock()

        # get_overview queries (5 results)
        order_result = MagicMock()
        order_result.scalar_one.return_value = 20
        campaign_result = MagicMock()
        campaign_result.scalar_one.return_value = 4
        video_result = MagicMock()
        video_result.scalar_one.return_value = 80
        views_result = MagicMock()
        views_result.scalar_one.return_value = 9000
        creators_result = MagicMock()
        creators_result.scalar_one.return_value = 6

        # Existing snapshot found
        existing = SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            date=date.today(),
            total_orders=10,
            active_campaigns=2,
            total_videos=50,
            total_views=5000,
            saved_creators=3,
        )
        snapshot_result = MagicMock()
        snapshot_result.scalar_one_or_none.return_value = existing

        session.execute = AsyncMock(
            side_effect=[
                order_result,
                campaign_result,
                video_result,
                views_result,
                creators_result,
                snapshot_result,
            ]
        )

        service = KpiService(session)
        snapshot = await service.take_snapshot(workspace_id)

        # Fields updated on existing object
        assert existing.total_orders == 20
        assert existing.active_campaigns == 4
        assert existing.total_videos == 80
        assert existing.total_views == 9000
        assert existing.saved_creators == 6
        # Should NOT add new object when updating
        assert not session.add.called


class TestDrillDown:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_drill_down_commerce(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 55
        session.execute = AsyncMock(return_value=count_result)

        service = KpiService(session)
        result = await service.get_drill_down(workspace_id, "commerce")

        assert result["module"] == "commerce"
        assert result["stats"]["total_orders"] == 55

    @pytest.mark.asyncio
    async def test_drill_down_unknown_module(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()

        service = KpiService(session)
        result = await service.get_drill_down(workspace_id, "nonexistent")

        assert result["module"] == "nonexistent"
        assert result["stats"] == {}

"""Tests for shop_health_sync Celery workers — daily SPS, metrics, and alert checks."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestCalculateDailySps:
    @pytest.mark.asyncio
    async def test_iterates_all_shops(self) -> None:
        """Should calculate SPS for all shops in all workspaces."""
        ws1 = SimpleNamespace(id=uuid.uuid4())
        shop1 = SimpleNamespace(id=uuid.uuid4(), workspace_id=ws1.id)

        mock_session = AsyncMock()
        mock_result_ws = MagicMock()
        mock_result_ws.scalars.return_value.all.return_value = [ws1]

        mock_result_shops = MagicMock()
        mock_result_shops.scalars.return_value.all.return_value = [shop1]

        mock_session.execute = AsyncMock(
            side_effect=[mock_result_ws, mock_result_shops]
        )
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_sps_service = MagicMock()
        mock_sps_service.save_daily_snapshot = AsyncMock(
            return_value=SimpleNamespace(estimated_score="4.2")
        )

        with (
            patch(
                "backend.workers.shop_health_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.shop_health_sync.SpsEstimationService",
                return_value=mock_sps_service,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.shop_health_sync import _calculate_daily_sps

            await _calculate_daily_sps()

        mock_sps_service.save_daily_snapshot.assert_awaited_once_with(ws1.id, shop1.id)
        mock_session.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_handles_shop_failure(self) -> None:
        """Should rollback and continue if one shop fails."""
        ws1 = SimpleNamespace(id=uuid.uuid4())
        shop1 = SimpleNamespace(id=uuid.uuid4(), workspace_id=ws1.id)

        mock_session = AsyncMock()
        mock_result_ws = MagicMock()
        mock_result_ws.scalars.return_value.all.return_value = [ws1]

        mock_result_shops = MagicMock()
        mock_result_shops.scalars.return_value.all.return_value = [shop1]

        mock_session.execute = AsyncMock(
            side_effect=[mock_result_ws, mock_result_shops]
        )
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_sps_service = MagicMock()
        mock_sps_service.save_daily_snapshot = AsyncMock(
            side_effect=RuntimeError("DB error")
        )

        with (
            patch(
                "backend.workers.shop_health_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.shop_health_sync.SpsEstimationService",
                return_value=mock_sps_service,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.shop_health_sync import _calculate_daily_sps

            await _calculate_daily_sps()

        mock_session.rollback.assert_awaited()


class TestCalculateDailyUnifiedMetrics:
    @pytest.mark.asyncio
    async def test_iterates_all_shops(self) -> None:
        """Should calculate metrics for all shops in all workspaces."""
        ws1 = SimpleNamespace(id=uuid.uuid4())
        shop1 = SimpleNamespace(id=uuid.uuid4(), workspace_id=ws1.id)

        mock_session = AsyncMock()
        mock_result_ws = MagicMock()
        mock_result_ws.scalars.return_value.all.return_value = [ws1]

        mock_result_shops = MagicMock()
        mock_result_shops.scalars.return_value.all.return_value = [shop1]

        mock_session.execute = AsyncMock(
            side_effect=[mock_result_ws, mock_result_shops]
        )
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_analytics_service = MagicMock()
        mock_analytics_service.calculate_daily_metrics = AsyncMock(
            return_value=SimpleNamespace(total_gmv="1000.00")
        )

        with (
            patch(
                "backend.workers.shop_health_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.shop_health_sync.UnifiedAnalyticsService",
                return_value=mock_analytics_service,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.shop_health_sync import (
                _calculate_daily_unified_metrics,
            )

            await _calculate_daily_unified_metrics()

        mock_analytics_service.calculate_daily_metrics.assert_awaited_once()
        mock_session.commit.assert_awaited()


class TestCheckHealthAlerts:
    @pytest.mark.asyncio
    async def test_evaluates_alerts_for_all_shops(self) -> None:
        """Should evaluate alerts for all shops."""
        ws1 = SimpleNamespace(id=uuid.uuid4())
        shop1 = SimpleNamespace(id=uuid.uuid4(), workspace_id=ws1.id)

        mock_session = AsyncMock()
        mock_result_ws = MagicMock()
        mock_result_ws.scalars.return_value.all.return_value = [ws1]

        mock_result_shops = MagicMock()
        mock_result_shops.scalars.return_value.all.return_value = [shop1]

        mock_session.execute = AsyncMock(
            side_effect=[mock_result_ws, mock_result_shops]
        )
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()

        mock_sps_service = MagicMock()
        mock_sps_service.calculate_estimated_sps = AsyncMock(
            return_value={
                "estimated_score": "4.0",
                "return_rate": "2.0",
                "cancellation_rate": "1.0",
                "otdr": "95.0",
                "total_orders": 100,
                "total_shipped": 90,
            }
        )

        mock_alert_service = MagicMock()
        mock_alert_service.evaluate_and_create_alerts = AsyncMock(return_value=[])

        with (
            patch(
                "backend.workers.shop_health_sync.async_session_factory"
            ) as mock_factory,
            patch(
                "backend.workers.shop_health_sync.SpsEstimationService",
                return_value=mock_sps_service,
            ),
            patch(
                "backend.workers.shop_health_sync.AlertService",
                return_value=mock_alert_service,
            ),
        ):
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

            from backend.workers.shop_health_sync import _check_health_alerts

            await _check_health_alerts()

        mock_sps_service.calculate_estimated_sps.assert_awaited_once()
        mock_alert_service.evaluate_and_create_alerts.assert_awaited_once()
        mock_session.commit.assert_awaited()


class TestCeleryTaskRegistration:
    def test_calculate_daily_sps_task(self) -> None:
        from backend.workers.shop_health_sync import calculate_daily_sps

        assert (
            calculate_daily_sps.name
            == "backend.workers.shop_health_sync.calculate_daily_sps"
        )

    def test_calculate_daily_unified_metrics_task(self) -> None:
        from backend.workers.shop_health_sync import calculate_daily_unified_metrics

        assert (
            calculate_daily_unified_metrics.name
            == "backend.workers.shop_health_sync.calculate_daily_unified_metrics"
        )

    def test_check_health_alerts_task(self) -> None:
        from backend.workers.shop_health_sync import check_health_alerts

        assert (
            check_health_alerts.name
            == "backend.workers.shop_health_sync.check_health_alerts"
        )


class TestBeatScheduleRegistration:
    def test_sps_schedule_exists(self) -> None:
        from backend.workers.celery_app import celery_app

        assert "calculate-daily-sps" in celery_app.conf.beat_schedule

    def test_unified_metrics_schedule_exists(self) -> None:
        from backend.workers.celery_app import celery_app

        assert "calculate-daily-unified-metrics" in celery_app.conf.beat_schedule

    def test_health_alerts_schedule_exists(self) -> None:
        from backend.workers.celery_app import celery_app

        assert "check-health-alerts" in celery_app.conf.beat_schedule

    def test_sps_schedule_timing(self) -> None:
        from backend.workers.celery_app import celery_app

        sched = celery_app.conf.beat_schedule["calculate-daily-sps"]
        assert sched["schedule"].hour == {1}
        assert sched["schedule"].minute == {1}

    def test_unified_metrics_schedule_timing(self) -> None:
        from backend.workers.celery_app import celery_app

        sched = celery_app.conf.beat_schedule["calculate-daily-unified-metrics"]
        assert sched["schedule"].hour == {1}
        assert sched["schedule"].minute == {30}

    def test_health_alerts_schedule_timing(self) -> None:
        from backend.workers.celery_app import celery_app

        sched = celery_app.conf.beat_schedule["check-health-alerts"]
        assert sched["schedule"].minute == {46}

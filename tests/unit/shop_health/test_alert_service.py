"""Tests for AlertService — threshold evaluation, listing, acknowledgement."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.modules.shop_health.services.alert_service import (
    ALERT_THRESHOLDS,
    AlertService,
)


class TestAlertThresholds:
    def test_thresholds_defined(self) -> None:
        assert len(ALERT_THRESHOLDS) == 6

    def test_critical_sps_threshold(self) -> None:
        critical = [
            t
            for t in ALERT_THRESHOLDS
            if t["severity"] == "CRITICAL" and t["type"] == "SPS_DROP"
        ]
        assert len(critical) == 1
        assert critical[0]["value"] == 3.0

    def test_violation_thresholds(self) -> None:
        violation = [t for t in ALERT_THRESHOLDS if t["type"] == "VIOLATION_THRESHOLD"]
        assert len(violation) == 2

    def test_cs_degradation_threshold(self) -> None:
        cs = [t for t in ALERT_THRESHOLDS if t["type"] == "CS_DEGRADATION"]
        assert len(cs) == 1
        assert cs[0]["value"] == 85.0

    def test_otdr_warning_threshold(self) -> None:
        otdr = [t for t in ALERT_THRESHOLDS if t["type"] == "OTDR_WARNING"]
        assert len(otdr) == 1
        assert otdr[0]["value"] == 90.0


class TestEvaluateAndCreateAlerts:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.fixture
    def shop_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_no_alerts_for_healthy_shop(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> None:
        """Healthy metrics should trigger zero alerts."""
        session = AsyncMock()
        session.add = MagicMock()

        service = AlertService(session)
        metrics = {
            "estimated_score": 4.5,
            "violation_points": 0,
            "cs_response_rate": 95.0,
            "otdr": 98.0,
        }
        alerts = await service.evaluate_and_create_alerts(
            workspace_id, shop_id, metrics
        )

        assert len(alerts) == 0
        session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_critical_sps_alert(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> None:
        """SPS below 3.0 should trigger CRITICAL alert."""
        session = AsyncMock()
        session.add = MagicMock()

        service = AlertService(session)
        metrics = {
            "estimated_score": 2.5,
            "violation_points": 0,
            "cs_response_rate": 95.0,
            "otdr": 98.0,
        }
        alerts = await service.evaluate_and_create_alerts(
            workspace_id, shop_id, metrics
        )

        critical = [a for a in alerts if a.severity == "CRITICAL"]
        assert len(critical) >= 1
        assert any(a.alert_type == "SPS_DROP" for a in critical)

    @pytest.mark.asyncio
    async def test_warning_sps_alert(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> None:
        """SPS below 3.5 but above 3.0 should trigger WARNING but not CRITICAL for SPS."""
        session = AsyncMock()
        session.add = MagicMock()

        service = AlertService(session)
        metrics = {
            "estimated_score": 3.2,
            "violation_points": 0,
            "cs_response_rate": 95.0,
            "otdr": 98.0,
        }
        alerts = await service.evaluate_and_create_alerts(
            workspace_id, shop_id, metrics
        )

        sps_alerts = [a for a in alerts if a.alert_type == "SPS_DROP"]
        assert len(sps_alerts) == 1
        assert sps_alerts[0].severity == "WARNING"

    @pytest.mark.asyncio
    async def test_violation_critical_alert(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> None:
        """24+ violation points should trigger CRITICAL alert."""
        session = AsyncMock()
        session.add = MagicMock()

        service = AlertService(session)
        metrics = {
            "estimated_score": 4.0,
            "violation_points": 25,
            "cs_response_rate": 95.0,
            "otdr": 98.0,
        }
        alerts = await service.evaluate_and_create_alerts(
            workspace_id, shop_id, metrics
        )

        violation_alerts = [a for a in alerts if a.alert_type == "VIOLATION_THRESHOLD"]
        assert len(violation_alerts) >= 1
        critical = [a for a in violation_alerts if a.severity == "CRITICAL"]
        assert len(critical) == 1

    @pytest.mark.asyncio
    async def test_multiple_alerts_at_once(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> None:
        """Shop in bad shape should trigger multiple alerts."""
        session = AsyncMock()
        session.add = MagicMock()

        service = AlertService(session)
        metrics = {
            "estimated_score": 2.5,
            "violation_points": 25,
            "cs_response_rate": 80.0,
            "otdr": 85.0,
        }
        alerts = await service.evaluate_and_create_alerts(
            workspace_id, shop_id, metrics
        )

        # Should trigger: CRITICAL SPS, WARNING SPS, CRITICAL violation, WARNING violation,
        # WARNING CS, WARNING OTDR
        assert len(alerts) >= 4

    @pytest.mark.asyncio
    async def test_alerts_are_added_to_session(
        self, workspace_id: uuid.UUID, shop_id: uuid.UUID
    ) -> None:
        """Each alert should be added to the session."""
        session = AsyncMock()
        session.add = MagicMock()

        service = AlertService(session)
        metrics = {
            "estimated_score": 2.5,
            "violation_points": 0,
            "cs_response_rate": 95.0,
            "otdr": 98.0,
        }
        alerts = await service.evaluate_and_create_alerts(
            workspace_id, shop_id, metrics
        )

        assert session.add.call_count == len(alerts)


class TestListAlerts:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_returns_paginated_results(self, workspace_id: uuid.UUID) -> None:
        """list_alerts should return dict with items, total, page, page_size."""
        session = AsyncMock()

        alert1 = SimpleNamespace(id=uuid.uuid4(), severity="CRITICAL")
        alert2 = SimpleNamespace(id=uuid.uuid4(), severity="WARNING")

        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = [alert1, alert2]

        session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = AlertService(session)
        result = await service.list_alerts(workspace_id, page=1, page_size=20)

        assert result["total"] == 2
        assert len(result["items"]) == 2
        assert result["page"] == 1
        assert result["page_size"] == 20

    @pytest.mark.asyncio
    async def test_filter_by_severity(self, workspace_id: uuid.UUID) -> None:
        """list_alerts with severity filter should still work."""
        session = AsyncMock()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []

        session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = AlertService(session)
        result = await service.list_alerts(
            workspace_id, severity="CRITICAL", page=1, page_size=20
        )

        assert result["total"] == 0
        assert result["items"] == []


class TestAcknowledgeAlert:
    @pytest.mark.asyncio
    async def test_sets_acknowledged_at(self) -> None:
        """acknowledge_alert should set acknowledged_at timestamp."""
        session = AsyncMock()
        alert_id = uuid.uuid4()

        mock_alert = MagicMock()
        mock_alert.acknowledged_at = None

        result = MagicMock()
        result.scalar_one_or_none.return_value = mock_alert
        session.execute = AsyncMock(return_value=result)

        service = AlertService(session)
        acknowledged = await service.acknowledge_alert(alert_id)

        assert acknowledged.acknowledged_at is not None

    @pytest.mark.asyncio
    async def test_raises_for_nonexistent_alert(self) -> None:
        """acknowledge_alert should raise ValueError for missing alerts."""
        session = AsyncMock()
        alert_id = uuid.uuid4()

        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=result)

        service = AlertService(session)
        with pytest.raises(ValueError, match="Alert not found"):
            await service.acknowledge_alert(alert_id)

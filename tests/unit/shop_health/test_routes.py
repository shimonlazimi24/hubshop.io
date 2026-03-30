"""Tests for shop_health routes — verifies router registration, endpoint configuration."""

import uuid
from datetime import UTC

from backend.modules.shop_health.routes import router


class TestRouterConfiguration:
    def test_router_prefix(self) -> None:
        assert router.prefix == "/shop-health"

    def test_router_tags(self) -> None:
        assert "shop-health" in router.tags

    def test_has_sps_route(self) -> None:
        paths = [route.path for route in router.routes]
        assert "/shop-health/sps" in paths

    def test_has_sps_history_route(self) -> None:
        paths = [route.path for route in router.routes]
        assert "/shop-health/sps/history" in paths

    def test_has_violations_get_route(self) -> None:
        routes = [(route.path, route.methods) for route in router.routes]
        assert any(p == "/shop-health/violations" and "GET" in m for p, m in routes)

    def test_has_violations_post_route(self) -> None:
        routes = [(route.path, route.methods) for route in router.routes]
        assert any(p == "/shop-health/violations" and "POST" in m for p, m in routes)

    def test_has_alerts_route(self) -> None:
        paths = [route.path for route in router.routes]
        assert "/shop-health/alerts" in paths

    def test_has_acknowledge_route(self) -> None:
        paths = [route.path for route in router.routes]
        assert "/shop-health/alerts/{alert_id}/acknowledge" in paths

    def test_has_analytics_route(self) -> None:
        paths = [route.path for route in router.routes]
        assert "/shop-health/analytics" in paths

    def test_total_route_count(self) -> None:
        """Should have 7 routes total."""
        assert len(router.routes) == 7


class TestRouterRegisteredInApp:
    def test_shop_health_router_in_app(self) -> None:
        """shop_health router should be registered in the FastAPI app."""
        from backend.main import app

        route_paths = [route.path for route in app.routes]
        assert any("/shop-health" in path for path in route_paths)

    def test_sps_endpoint_accessible(self) -> None:
        """GET /api/shop-health/sps should be in the app routes."""
        from backend.main import app

        route_paths = [route.path for route in app.routes]
        assert "/api/shop-health/sps" in route_paths

    def test_alerts_endpoint_accessible(self) -> None:
        """GET /api/shop-health/alerts should be in the app routes."""
        from backend.main import app

        route_paths = [route.path for route in app.routes]
        assert "/api/shop-health/alerts" in route_paths


class TestSchemaValidation:
    def test_sps_current_response_schema(self) -> None:
        from backend.modules.shop_health.schemas import SpsCurrentResponse

        resp = SpsCurrentResponse(
            estimated_score="4.2",
            return_rate="2.5",
            cancellation_rate="1.0",
            otdr="95.0",
            total_orders=100,
            total_shipped=90,
        )
        assert resp.estimated_score == "4.2"

    def test_violation_response_schema(self) -> None:
        from datetime import datetime

        from backend.modules.shop_health.schemas import ViolationResponse

        now = datetime.now(tz=UTC)
        resp = ViolationResponse(
            id=str(uuid.uuid4()),
            workspace_id=str(uuid.uuid4()),
            shop_id=str(uuid.uuid4()),
            violation_type="COUNTERFEIT",
            points=6,
            description="Counterfeit product detected",
            occurred_at=now,
            expires_at=now,
            resolved=False,
            source="MANUAL",
            created_at=now,
            updated_at=now,
        )
        assert resp.points == 6

    def test_health_alert_response_schema(self) -> None:
        from datetime import datetime

        from backend.modules.shop_health.schemas import HealthAlertResponse

        now = datetime.now(tz=UTC)
        resp = HealthAlertResponse(
            id=str(uuid.uuid4()),
            workspace_id=str(uuid.uuid4()),
            shop_id=str(uuid.uuid4()),
            alert_type="SPS_DROP",
            severity="CRITICAL",
            message="Score dropped",
            metric_name="estimated_score",
            current_value="2.5",
            threshold_value="3.0",
            triggered_at=now,
            created_at=now,
            updated_at=now,
        )
        assert resp.severity == "CRITICAL"
        assert resp.acknowledged_at is None

    def test_create_violation_request_schema(self) -> None:
        from datetime import datetime

        from backend.modules.shop_health.schemas import CreateViolationRequest

        now = datetime.now(tz=UTC)
        req = CreateViolationRequest(
            shop_id=str(uuid.uuid4()),
            violation_type="COUNTERFEIT",
            points=6,
            description="Counterfeit product",
            occurred_at=now,
            expires_at=now,
        )
        assert req.points == 6

    def test_paginated_alerts_response_schema(self) -> None:
        from backend.modules.shop_health.schemas import PaginatedAlertsResponse

        resp = PaginatedAlertsResponse(items=[], total=0, page=1, page_size=20)
        assert resp.total == 0

"""Integration tests for commerce API routes via FastAPI test client."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.db.engine import get_db
from backend.dependencies import get_current_user
from backend.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def mock_user():
    """Create a mock authenticated user."""
    return SimpleNamespace(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )


@pytest.fixture
def mock_db():
    """Create a mock async DB session."""
    return AsyncMock()


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_db):
    """Override FastAPI dependencies for all tests in this module."""
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db
    yield
    app.dependency_overrides.clear()


class TestShopRoutes:
    @pytest.mark.asyncio
    @patch("backend.modules.commerce.services.shop_service.ShopService.list_shops")
    async def test_list_shops_empty(
        self,
        mock_list_shops: AsyncMock,
    ) -> None:
        mock_list_shops.return_value = []

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/commerce/shops?workspace_id={uuid.uuid4()}",
            )

        assert response.status_code == 200
        assert response.json() == []


class TestProductRoutes:
    @pytest.mark.asyncio
    @patch("backend.modules.commerce.services.product_service.ProductService.list_products")
    async def test_list_products_paginated(
        self,
        mock_list: AsyncMock,
    ) -> None:
        from backend.utils.pagination import PaginatedResult

        mock_list.return_value = PaginatedResult(
            items=[], total=0, page=1, page_size=20
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/commerce/products?workspace_id={uuid.uuid4()}",
            )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1

    @pytest.mark.asyncio
    @patch("backend.modules.commerce.services.product_service.ProductService.get_product")
    async def test_get_product_not_found(
        self,
        mock_get: AsyncMock,
    ) -> None:
        mock_get.return_value = None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/commerce/products/{uuid.uuid4()}",
            )

        assert response.status_code == 404


class TestOrderRoutes:
    @pytest.mark.asyncio
    @patch("backend.modules.commerce.services.order_service.OrderService.list_orders")
    async def test_list_orders(
        self,
        mock_list: AsyncMock,
    ) -> None:
        from backend.utils.pagination import PaginatedResult

        mock_list.return_value = PaginatedResult(
            items=[], total=0, page=1, page_size=20
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/commerce/orders?workspace_id={uuid.uuid4()}",
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch("backend.modules.commerce.services.order_service.OrderService.get_order")
    async def test_get_order_not_found(
        self,
        mock_get: AsyncMock,
    ) -> None:
        mock_get.return_value = None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/commerce/orders/{uuid.uuid4()}",
            )

        assert response.status_code == 404


class TestReturnRoutes:
    @pytest.mark.asyncio
    @patch("backend.modules.commerce.services.return_service.ReturnService.list_returns")
    async def test_list_returns(
        self,
        mock_list: AsyncMock,
    ) -> None:
        from backend.utils.pagination import PaginatedResult

        mock_list.return_value = PaginatedResult(
            items=[], total=0, page=1, page_size=20
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/commerce/returns?workspace_id={uuid.uuid4()}",
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    @patch("backend.modules.commerce.services.return_service.ReturnService.approve_return")
    async def test_approve_return_not_found(
        self,
        mock_approve: AsyncMock,
    ) -> None:
        mock_approve.return_value = None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/commerce/returns/{uuid.uuid4()}/approve",
            )

        assert response.status_code == 404


class TestAnalyticsRoutes:
    @pytest.mark.asyncio
    @patch(
        "backend.modules.commerce.services.analytics_service.CommerceAnalyticsService.get_revenue_summary"
    )
    async def test_get_summary(
        self,
        mock_summary: AsyncMock,
    ) -> None:
        mock_summary.return_value = {
            "total_revenue": "1000.00",
            "total_orders": 10,
            "average_order_value": "100.00",
            "return_rate": 0.05,
            "period_start": "2026-01-01T00:00:00+00:00",
            "period_end": "2026-01-31T00:00:00+00:00",
        }

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/commerce/analytics/summary?workspace_id={uuid.uuid4()}",
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total_revenue"] == "1000.00"
        assert data["total_orders"] == 10


class TestUnauthenticatedAccess:
    @pytest.fixture(autouse=True)
    def clear_overrides(self):
        """Clear dependency overrides so auth is required."""
        app.dependency_overrides.clear()
        yield
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_shops_requires_auth(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/commerce/shops?workspace_id={uuid.uuid4()}"
            )

        assert response.status_code in (401, 403)

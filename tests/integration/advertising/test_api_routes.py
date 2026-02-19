"""Integration tests for advertising API routes via FastAPI test client."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.db.engine import get_db
from backend.dependencies import get_current_user
from backend.main import app
from backend.utils.pagination import PaginatedResult


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def mock_user():
    return SimpleNamespace(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture(autouse=True)
def override_deps(mock_user, mock_db):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db
    yield
    app.dependency_overrides.clear()


class TestAdAccountRoutes:
    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.ad_account_service.AdAccountService.list_ad_accounts"
    )
    async def test_list_ad_accounts_empty(
        self, mock_list: AsyncMock
    ) -> None:
        mock_list.return_value = []

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/ads/accounts?workspace_id={uuid.uuid4()}"
            )

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.ad_account_service.AdAccountService.get_ad_account"
    )
    async def test_get_ad_account_not_found(
        self, mock_get: AsyncMock
    ) -> None:
        mock_get.return_value = None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/ads/accounts/{uuid.uuid4()}"
            )

        assert response.status_code == 404

    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.ad_account_service.AdAccountService.sync_ad_accounts_from_connected"
    )
    async def test_sync_ad_accounts(
        self, mock_sync: AsyncMock
    ) -> None:
        mock_sync.return_value = [SimpleNamespace(id=uuid.uuid4())]

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/ads/accounts/sync?workspace_id={uuid.uuid4()}"
            )

        assert response.status_code == 200
        assert response.json()["synced"] == 1


class TestCampaignRoutes:
    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.campaign_service.CampaignService.list_campaigns"
    )
    async def test_list_campaigns_paginated(
        self, mock_list: AsyncMock
    ) -> None:
        mock_list.return_value = PaginatedResult(
            items=[], total=0, page=1, page_size=20
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/ads/campaigns?workspace_id={uuid.uuid4()}"
            )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1

    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.campaign_service.CampaignService.get_campaign"
    )
    async def test_get_campaign_not_found(
        self, mock_get: AsyncMock
    ) -> None:
        mock_get.return_value = None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/ads/campaigns/{uuid.uuid4()}"
            )

        assert response.status_code == 404

    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.ad_account_service.AdAccountService.get_ad_account_by_advertiser_id"
    )
    async def test_create_campaign_account_not_found(
        self, mock_get_acct: AsyncMock
    ) -> None:
        mock_get_acct.return_value = None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/ads/campaigns?workspace_id={uuid.uuid4()}",
                json={
                    "ad_account_id": "nonexistent",
                    "campaign_name": "Test",
                    "objective_type": "TRAFFIC",
                    "budget_mode": "BUDGET_MODE_DAY",
                },
            )

        assert response.status_code == 404

    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.ad_account_service.AdAccountService.list_ad_accounts"
    )
    @patch(
        "backend.modules.advertising.services.campaign_service.CampaignService.sync_campaigns"
    )
    async def test_sync_campaigns(
        self, mock_sync: AsyncMock, mock_list: AsyncMock
    ) -> None:
        mock_list.return_value = [
            SimpleNamespace(id=uuid.uuid4(), advertiser_id="111")
        ]
        mock_sync.return_value = 5

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/ads/campaigns/sync?workspace_id={uuid.uuid4()}"
            )

        assert response.status_code == 200
        assert response.json()["synced"] == 5


class TestAdGroupRoutes:
    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.ad_group_service.AdGroupService.list_ad_groups"
    )
    async def test_list_ad_groups_paginated(
        self, mock_list: AsyncMock
    ) -> None:
        mock_list.return_value = PaginatedResult(
            items=[], total=0, page=1, page_size=20
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/ads/ad-groups?workspace_id={uuid.uuid4()}"
            )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.ad_group_service.AdGroupService.get_ad_group"
    )
    async def test_get_ad_group_not_found(
        self, mock_get: AsyncMock
    ) -> None:
        mock_get.return_value = None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/ads/ad-groups/{uuid.uuid4()}"
            )

        assert response.status_code == 404


class TestAdRoutes:
    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.ad_service.AdService.list_ads"
    )
    async def test_list_ads_paginated(
        self, mock_list: AsyncMock
    ) -> None:
        mock_list.return_value = PaginatedResult(
            items=[], total=0, page=1, page_size=20
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/ads/creatives?workspace_id={uuid.uuid4()}"
            )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.ad_service.AdService.get_ad"
    )
    async def test_get_ad_not_found(
        self, mock_get: AsyncMock
    ) -> None:
        mock_get.return_value = None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/ads/creatives/{uuid.uuid4()}"
            )

        assert response.status_code == 404


class TestReportRoutes:
    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.ad_account_service.AdAccountService.get_ad_account_by_advertiser_id"
    )
    async def test_sync_report_account_not_found(
        self, mock_get_acct: AsyncMock
    ) -> None:
        mock_get_acct.return_value = None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/ads/reports/sync",
                json={
                    "ad_account_id": "nonexistent",
                    "date_start": "2026-01-01",
                    "date_end": "2026-01-31",
                },
            )

        assert response.status_code == 404

    @pytest.mark.asyncio
    @patch(
        "backend.modules.advertising.services.report_service.ReportService.get_sync_report"
    )
    @patch(
        "backend.modules.advertising.services.ad_account_service.AdAccountService.get_ad_account_by_advertiser_id"
    )
    async def test_sync_report_success(
        self,
        mock_get_acct: AsyncMock,
        mock_report: AsyncMock,
    ) -> None:
        mock_get_acct.return_value = SimpleNamespace(
            id=uuid.uuid4(), advertiser_id="111"
        )
        mock_report.return_value = {
            "rows": [
                {
                    "dimensions": {"stat_time_day": "2026-01-15"},
                    "metrics": {"spend": "100.00", "clicks": 50},
                }
            ],
            "total_rows": 1,
        }

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/ads/reports/sync",
                json={
                    "ad_account_id": "111",
                    "date_start": "2026-01-01",
                    "date_end": "2026-01-31",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total_rows"] == 1
        assert len(data["rows"]) == 1
        assert data["rows"][0]["metrics"]["spend"] == "100.00"

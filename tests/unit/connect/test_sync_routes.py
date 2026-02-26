"""Tests for sync status API routes."""

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


SYNC_SVC = "backend.modules.connect.sync_routes.SyncStatusService"


class TestListSyncJobs:
    @pytest.mark.asyncio
    @patch(SYNC_SVC)
    async def test_list_sync_jobs(self, MockService: AsyncMock) -> None:
        mock_svc = AsyncMock()
        mock_svc.list_recent_jobs.return_value = [
            {
                "id": str(uuid.uuid4()),
                "platform": "shop",
                "sync_type": "orders",
                "status": "completed",
                "items_synced": 100,
                "items_total": 100,
                "error_message": None,
                "started_at": "2026-02-26T00:00:00+00:00",
                "completed_at": "2026-02-26T00:01:00+00:00",
                "created_at": "2026-02-26T00:00:00+00:00",
            }
        ]
        MockService.return_value = mock_svc

        workspace_id = uuid.uuid4()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                f"/api/connect/sync/jobs?workspace_id={workspace_id}",
            )

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["platform"] == "shop"


class TestGetActiveSyncJobs:
    @pytest.mark.asyncio
    @patch(SYNC_SVC)
    async def test_get_active_jobs(self, MockService: AsyncMock) -> None:
        mock_svc = AsyncMock()
        mock_svc.get_active_jobs.return_value = []
        MockService.return_value = mock_svc

        workspace_id = uuid.uuid4()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                f"/api/connect/sync/active?workspace_id={workspace_id}",
            )

        assert resp.status_code == 200
        assert resp.json() == []

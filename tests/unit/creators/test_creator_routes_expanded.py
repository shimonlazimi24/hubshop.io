"""Unit tests for expanded creator routes — metrics sync, videos, auth check,
invitation status, campaign stats, and save-from-discovery."""

import uuid
from datetime import UTC, datetime
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


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------

def _make_creator(**overrides) -> SimpleNamespace:
    defaults = {
        "id": str(uuid.uuid4()),
        "platform_creator_id": "plat_cr_1",
        "username": "creator1",
        "display_name": "Creator One",
        "avatar_url": "https://example.com/avatar.jpg",
        "bio": "Hello",
        "follower_count": 10000,
        "following_count": 500,
        "likes_count": 200000,
        "video_count": 150,
        "tier": "GOLD",
        "categories": None,
        "engagement_rate": "3.5",
        "is_saved": True,
        "audience_demographics": None,
        "detail_json": None,
        "created_at": datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
        "updated_at": datetime(2026, 1, 15, 0, 0, 0, tzinfo=UTC),
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_authorization(**overrides) -> SimpleNamespace:
    defaults = {
        "id": str(uuid.uuid4()),
        "creator_id": str(uuid.uuid4()),
        "platform_video_id": "vid_123",
        "authorization_code": "auth_abc",
        "status": "ACTIVE",
        "expires_at": datetime(2026, 6, 1, 0, 0, 0, tzinfo=UTC),
        "created_at": datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_invitation(**overrides) -> SimpleNamespace:
    defaults = {
        "id": str(uuid.uuid4()),
        "campaign_id": str(uuid.uuid4()),
        "creator_id": str(uuid.uuid4()),
        "status": "ACCEPTED",
        "message": "Join our campaign!",
        "offered_amount": "500",
        "responded_at": datetime(2026, 2, 1, 0, 0, 0, tzinfo=UTC),
        "created_at": datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC),
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


PROFILE_SVC = "backend.modules.creators.services.creator_profile_service.CreatorProfileService"
CREATOR_SVC = "backend.modules.creators.services.creator_service.CreatorService"
SPARK_SVC = "backend.modules.creators.services.spark_ads_service.SparkAdsService"
CAMPAIGN_SVC = "backend.modules.creators.services.campaign_service.CreatorCampaignService"


# ---------------------------------------------------------------------------
# 1. POST /creators/profiles/{id}/sync-metrics — 200
# ---------------------------------------------------------------------------

class TestSyncMetricsRoute:
    @pytest.mark.asyncio
    @patch(f"{CREATOR_SVC}.sync_creator_metrics")
    @patch(f"{PROFILE_SVC}.get_creator")
    async def test_sync_metrics_route(
        self, mock_get: AsyncMock, mock_sync: AsyncMock
    ) -> None:
        creator = _make_creator()
        mock_get.return_value = creator
        mock_sync.return_value = creator

        creator_id = uuid.uuid4()
        workspace_id = uuid.uuid4()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/creators/profiles/{creator_id}/sync-metrics"
                f"?workspace_id={workspace_id}",
            )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "creator1"
        assert data["follower_count"] == 10000

    # -------------------------------------------------------------------
    # 2. POST /creators/profiles/{id}/sync-metrics — 404
    # -------------------------------------------------------------------

    @pytest.mark.asyncio
    @patch(f"{PROFILE_SVC}.get_creator")
    async def test_sync_metrics_not_found(
        self, mock_get: AsyncMock
    ) -> None:
        mock_get.return_value = None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/creators/profiles/{uuid.uuid4()}/sync-metrics"
                f"?workspace_id={uuid.uuid4()}",
            )

        assert response.status_code == 404


# ---------------------------------------------------------------------------
# 3. GET /creators/profiles/{id}/videos — 200
# ---------------------------------------------------------------------------

class TestGetCreatorVideosRoute:
    @pytest.mark.asyncio
    @patch(f"{CREATOR_SVC}.get_creator_videos")
    @patch(f"{PROFILE_SVC}.get_creator")
    async def test_get_creator_videos_route(
        self, mock_get: AsyncMock, mock_videos: AsyncMock
    ) -> None:
        creator = _make_creator()
        mock_get.return_value = creator
        mock_videos.return_value = [
            {"video_id": "v1", "title": "Test Video"},
        ]

        creator_id = uuid.uuid4()
        workspace_id = uuid.uuid4()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/creators/profiles/{creator_id}/videos"
                f"?workspace_id={workspace_id}",
            )

        assert response.status_code == 200
        data = response.json()
        assert "videos" in data
        assert len(data["videos"]) == 1
        assert data["videos"][0]["title"] == "Test Video"


# ---------------------------------------------------------------------------
# 4. POST /creators/spark-ads/authorizations/{id}/check — 200
# ---------------------------------------------------------------------------

class TestCheckAuthStatusRoute:
    @pytest.mark.asyncio
    @patch(f"{SPARK_SVC}.check_authorization_status")
    async def test_check_auth_status_route(
        self, mock_check: AsyncMock
    ) -> None:
        auth = _make_authorization()
        mock_check.return_value = auth

        auth_id = uuid.uuid4()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/creators/spark-ads/authorizations/{auth_id}/check",
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ACTIVE"
        assert data["authorization_code"] == "auth_abc"

    # -------------------------------------------------------------------
    # 5. POST /creators/spark-ads/authorizations/{id}/check — 404
    # -------------------------------------------------------------------

    @pytest.mark.asyncio
    @patch(f"{SPARK_SVC}.check_authorization_status")
    async def test_check_auth_not_found(
        self, mock_check: AsyncMock
    ) -> None:
        mock_check.return_value = None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/creators/spark-ads/authorizations/{uuid.uuid4()}/check",
            )

        assert response.status_code == 404


# ---------------------------------------------------------------------------
# 6. PUT /creators/campaigns/{cid}/invitations/{iid}/status — 200
# ---------------------------------------------------------------------------

class TestUpdateInvitationStatusRoute:
    @pytest.mark.asyncio
    @patch(f"{CAMPAIGN_SVC}.update_invitation_status")
    async def test_update_invitation_status_route(
        self, mock_update: AsyncMock
    ) -> None:
        invitation = _make_invitation(status="ACCEPTED")
        mock_update.return_value = invitation

        campaign_id = uuid.uuid4()
        invitation_id = uuid.uuid4()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.put(
                f"/api/creators/campaigns/{campaign_id}"
                f"/invitations/{invitation_id}/status",
                json={"status": "ACCEPTED"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ACCEPTED"

    # -------------------------------------------------------------------
    # 7. PUT /creators/campaigns/{cid}/invitations/{iid}/status — 404
    # -------------------------------------------------------------------

    @pytest.mark.asyncio
    @patch(f"{CAMPAIGN_SVC}.update_invitation_status")
    async def test_update_invitation_not_found(
        self, mock_update: AsyncMock
    ) -> None:
        mock_update.return_value = None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.put(
                f"/api/creators/campaigns/{uuid.uuid4()}"
                f"/invitations/{uuid.uuid4()}/status",
                json={"status": "DECLINED"},
            )

        assert response.status_code == 404


# ---------------------------------------------------------------------------
# 8. GET /creators/campaigns/{id}/stats — 200
# ---------------------------------------------------------------------------

class TestCampaignStatsRoute:
    @pytest.mark.asyncio
    @patch(f"{CAMPAIGN_SVC}.get_campaign_stats")
    @patch(f"{CAMPAIGN_SVC}.get_campaign")
    async def test_campaign_stats_route(
        self, mock_get: AsyncMock, mock_stats: AsyncMock
    ) -> None:
        campaign = SimpleNamespace(id=uuid.uuid4(), name="Test Campaign")
        mock_get.return_value = campaign
        mock_stats.return_value = {
            "total_invitations": 10,
            "pending": 3,
            "accepted": 5,
            "declined": 2,
            "total_offered_amount": "5000.0",
            "acceptance_rate": 50.0,
        }

        campaign_id = uuid.uuid4()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/creators/campaigns/{campaign_id}/stats",
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total_invitations"] == 10
        assert data["accepted"] == 5
        assert data["acceptance_rate"] == 50.0

    # -------------------------------------------------------------------
    # 9. GET /creators/campaigns/{id}/stats — 404
    # -------------------------------------------------------------------

    @pytest.mark.asyncio
    @patch(f"{CAMPAIGN_SVC}.get_campaign")
    async def test_campaign_stats_not_found(
        self, mock_get: AsyncMock
    ) -> None:
        mock_get.return_value = None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/creators/campaigns/{uuid.uuid4()}/stats",
            )

        assert response.status_code == 404


# ---------------------------------------------------------------------------
# 10. POST /creators/discover/save — 201
# ---------------------------------------------------------------------------

class TestSaveCreatorFromDiscoveryRoute:
    @pytest.mark.asyncio
    @patch(f"{CREATOR_SVC}.sync_creator_to_workspace")
    async def test_save_creator_from_discovery_route(
        self, mock_sync: AsyncMock
    ) -> None:
        creator = _make_creator()
        mock_sync.return_value = creator

        workspace_id = uuid.uuid4()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/creators/discover/save?workspace_id={workspace_id}",
                json={
                    "creator_data": {
                        "creator_id": "12345",
                        "username": "new_creator",
                        "follower_count": 50000,
                    }
                },
            )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "creator1"
        assert data["is_saved"] is True

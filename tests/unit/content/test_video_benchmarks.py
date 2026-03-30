"""Tests for video performance benchmarking — top videos, summary, comparison."""

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.db.engine import get_db
from backend.dependencies import get_current_user
from backend.main import app
from backend.modules.content.services.video_service import VideoService

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VIDEO_SVC = "backend.modules.content.services.video_service.VideoService"


def _make_video(**overrides) -> SimpleNamespace:
    """Create a mock Video object with sensible defaults."""
    defaults = {
        "id": uuid.uuid4(),
        "workspace_id": uuid.uuid4(),
        "connected_account_id": uuid.uuid4(),
        "platform_video_id": f"plat_{uuid.uuid4().hex[:8]}",
        "title": "Test Video",
        "description": "A test video",
        "cover_url": "https://example.com/cover.jpg",
        "video_url": None,
        "embed_link": None,
        "duration": 60,
        "status": "PUBLIC",
        "view_count": 1000,
        "like_count": 100,
        "comment_count": 50,
        "share_count": 25,
        "create_time": datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC),
        "detail_json": None,
        "created_at": datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC),
        "updated_at": datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC),
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


# ---------------------------------------------------------------------------
# Fixtures for route tests
# ---------------------------------------------------------------------------


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


# ===========================================================================
# Service tests
# ===========================================================================


class TestGetTopVideos:
    @pytest.mark.asyncio
    async def test_top_videos_by_views(self) -> None:
        """Returns videos ordered by view_count desc."""
        session = AsyncMock()
        v1 = _make_video(view_count=5000, title="Top")
        v2 = _make_video(view_count=3000, title="Mid")
        v3 = _make_video(view_count=1000, title="Low")

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [v1, v2, v3]
        session.execute.return_value = result_mock

        service = VideoService(session)
        videos = await service.get_top_videos(
            uuid.uuid4(), metric="view_count", limit=10
        )

        assert len(videos) == 3
        assert videos[0].title == "Top"
        assert videos[0].view_count == 5000
        session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_top_videos_by_likes(self) -> None:
        """Returns videos ordered by like_count desc."""
        session = AsyncMock()
        v1 = _make_video(like_count=500, title="Most Liked")
        v2 = _make_video(like_count=100, title="Less Liked")

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [v1, v2]
        session.execute.return_value = result_mock

        service = VideoService(session)
        videos = await service.get_top_videos(
            uuid.uuid4(), metric="like_count", limit=10
        )

        assert len(videos) == 2
        assert videos[0].title == "Most Liked"
        assert videos[0].like_count == 500

    @pytest.mark.asyncio
    async def test_top_videos_limit(self) -> None:
        """Respects limit parameter."""
        session = AsyncMock()

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [
            _make_video(view_count=i) for i in range(3)
        ]
        session.execute.return_value = result_mock

        service = VideoService(session)
        videos = await service.get_top_videos(uuid.uuid4(), limit=3)

        assert len(videos) == 3
        session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_top_videos_invalid_metric_defaults_to_views(self) -> None:
        """Invalid metric falls back to view_count without error."""
        session = AsyncMock()
        v1 = _make_video(view_count=9999, title="Fallback")

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [v1]
        session.execute.return_value = result_mock

        service = VideoService(session)
        videos = await service.get_top_videos(
            uuid.uuid4(), metric="invalid_metric", limit=5
        )

        assert len(videos) == 1
        assert videos[0].title == "Fallback"


class TestVideoPerformanceSummary:
    @pytest.mark.asyncio
    async def test_performance_summary_calculation(self) -> None:
        """Verify aggregation math with real numbers."""
        session = AsyncMock()
        row = SimpleNamespace(
            total_videos=5,
            total_views=10000,
            total_likes=1000,
            total_comments=500,
            total_shares=250,
            avg_views=2000.0,
            avg_likes=200.0,
        )
        result_mock = MagicMock()
        result_mock.one.return_value = row
        session.execute.return_value = result_mock

        service = VideoService(session)
        summary = await service.get_video_performance_summary(uuid.uuid4())

        assert summary["total_videos"] == 5
        assert summary["total_views"] == 10000
        assert summary["total_likes"] == 1000
        assert summary["total_comments"] == 500
        assert summary["total_shares"] == 250
        assert summary["avg_views"] == 2000.0
        assert summary["avg_likes"] == 200.0
        # engagement = 1000 + 500 + 250 = 1750, rate = 1750/10000*100 = 17.5
        assert summary["avg_engagement_rate"] == 17.5

    @pytest.mark.asyncio
    async def test_performance_summary_empty_workspace(self) -> None:
        """Zero videos returns zeros and 0.0 engagement rate."""
        session = AsyncMock()
        row = SimpleNamespace(
            total_videos=0,
            total_views=0,
            total_likes=0,
            total_comments=0,
            total_shares=0,
            avg_views=0,
            avg_likes=0,
        )
        result_mock = MagicMock()
        result_mock.one.return_value = row
        session.execute.return_value = result_mock

        service = VideoService(session)
        summary = await service.get_video_performance_summary(uuid.uuid4())

        assert summary["total_videos"] == 0
        assert summary["total_views"] == 0
        assert summary["avg_engagement_rate"] == 0.0


class TestCompareVideoPerformance:
    @pytest.mark.asyncio
    async def test_compare_videos(self) -> None:
        """Returns comparison dicts with engagement_rate for each video."""
        session = AsyncMock()
        vid1 = _make_video(
            view_count=2000,
            like_count=200,
            comment_count=100,
            share_count=50,
            title="Video A",
        )
        vid2 = _make_video(
            view_count=5000,
            like_count=300,
            comment_count=150,
            share_count=75,
            title="Video B",
        )

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [vid1, vid2]
        session.execute.return_value = result_mock

        service = VideoService(session)
        comparisons = await service.compare_video_performance([vid1.id, vid2.id])

        assert len(comparisons) == 2
        assert comparisons[0]["title"] == "Video A"
        assert comparisons[1]["title"] == "Video B"
        assert "engagement_rate" in comparisons[0]
        assert "engagement_rate" in comparisons[1]

    @pytest.mark.asyncio
    async def test_compare_videos_engagement_rate_calc(self) -> None:
        """Verify engagement rate = (likes+comments+shares)/views*100."""
        session = AsyncMock()
        vid = _make_video(
            view_count=4000,
            like_count=200,
            comment_count=100,
            share_count=100,
            title="Rate Test",
        )

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [vid]
        session.execute.return_value = result_mock

        service = VideoService(session)
        comparisons = await service.compare_video_performance([vid.id])

        # engagement = 200+100+100 = 400, rate = 400/4000*100 = 10.0
        assert comparisons[0]["engagement_rate"] == 10.0


# ===========================================================================
# Route tests
# ===========================================================================


class TestTopVideosRoute:
    @pytest.mark.asyncio
    @patch(f"{VIDEO_SVC}.get_top_videos")
    async def test_top_videos_route(self, mock_top: AsyncMock) -> None:
        video = _make_video(id=str(uuid.uuid4()))
        mock_top.return_value = [video]

        workspace_id = uuid.uuid4()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/content/videos/top"
                f"?workspace_id={workspace_id}&metric=view_count&limit=5",
            )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["title"] == "Test Video"
        mock_top.assert_awaited_once()


class TestPerformanceSummaryRoute:
    @pytest.mark.asyncio
    @patch(f"{VIDEO_SVC}.get_video_performance_summary")
    async def test_performance_summary_route(self, mock_summary: AsyncMock) -> None:
        mock_summary.return_value = {
            "total_videos": 10,
            "total_views": 50000,
            "total_likes": 5000,
            "total_comments": 2000,
            "total_shares": 1000,
            "avg_views": 5000.0,
            "avg_likes": 500.0,
            "avg_engagement_rate": 16.0,
        }

        workspace_id = uuid.uuid4()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/content/videos/performance-summary?workspace_id={workspace_id}",
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total_videos"] == 10
        assert data["avg_engagement_rate"] == 16.0
        mock_summary.assert_awaited_once()

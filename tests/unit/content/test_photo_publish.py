"""Tests for photo publishing and video query-by-ID features."""

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.db.engine import get_db
from backend.dependencies import get_current_user
from backend.main import app
from backend.modules.content.services.publish_service import PublishService
from backend.modules.content.services.video_service import VideoService

# ---------------------------------------------------------------------------
# Fixtures
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VIDEO_SVC = "backend.modules.content.services.video_service.VideoService"
PUBLISH_SVC = "backend.modules.content.services.publish_service.PublishService"

SAMPLE_VIDEOS = [
    {
        "id": "vid_001",
        "title": "First Video",
        "video_description": "desc",
        "cover_image_url": "https://example.com/cover1.jpg",
        "embed_link": "https://example.com/embed1",
        "duration": 30,
        "create_time": 1700000000,
        "like_count": 100,
        "comment_count": 10,
        "share_count": 5,
        "view_count": 1000,
    },
    {
        "id": "vid_002",
        "title": "Second Video",
        "video_description": "desc2",
        "cover_image_url": "https://example.com/cover2.jpg",
        "embed_link": "https://example.com/embed2",
        "duration": 60,
        "create_time": 1700100000,
        "like_count": 200,
        "comment_count": 20,
        "share_count": 10,
        "view_count": 2000,
    },
]


def _mock_gateway() -> AsyncMock:
    """Return an AsyncMock that behaves like PlatformGateway."""
    return AsyncMock()


def _mock_account() -> SimpleNamespace:
    """Return a mock ConnectedAccount."""
    return SimpleNamespace(id=uuid.uuid4())


# ---------------------------------------------------------------------------
# VideoService.query_videos_by_id tests
# ---------------------------------------------------------------------------


class TestQueryVideosById:
    @pytest.mark.asyncio
    async def test_query_videos_by_id_success(self) -> None:
        """Mock gateway.post, verify returns videos."""
        session = AsyncMock()
        service = VideoService(session)

        gateway = _mock_gateway()
        gateway.post.return_value = {"data": {"videos": SAMPLE_VIDEOS}}

        account = _mock_account()
        service._get_developer_gateway = AsyncMock(return_value=(account, gateway))

        workspace_id = uuid.uuid4()
        result = await service.query_videos_by_id(workspace_id, ["vid_001", "vid_002"])

        assert len(result) == 2
        assert result[0]["id"] == "vid_001"
        assert result[1]["id"] == "vid_002"

    @pytest.mark.asyncio
    async def test_query_videos_by_id_empty(self) -> None:
        """Returns empty list when no videos match."""
        session = AsyncMock()
        service = VideoService(session)

        gateway = _mock_gateway()
        gateway.post.return_value = {"data": {"videos": []}}

        account = _mock_account()
        service._get_developer_gateway = AsyncMock(return_value=(account, gateway))

        workspace_id = uuid.uuid4()
        result = await service.query_videos_by_id(workspace_id, ["nonexistent"])

        assert result == []

    @pytest.mark.asyncio
    async def test_query_videos_api_call_format(self) -> None:
        """Verify gateway.post called with correct body and params."""
        session = AsyncMock()
        service = VideoService(session)

        gateway = _mock_gateway()
        gateway.post.return_value = {"data": {"videos": []}}

        account = _mock_account()
        service._get_developer_gateway = AsyncMock(return_value=(account, gateway))

        workspace_id = uuid.uuid4()
        video_ids = ["vid_001", "vid_002"]
        await service.query_videos_by_id(workspace_id, video_ids)

        gateway.post.assert_called_once_with(
            "/video/query/",
            json_body={"filters": {"video_ids": video_ids}},
            params={
                "fields": "id,title,video_description,cover_image_url,embed_link,duration,create_time,like_count,comment_count,share_count,view_count"
            },
        )


# ---------------------------------------------------------------------------
# PublishService.create_photo_publish_job tests
# ---------------------------------------------------------------------------


class TestCreatePhotoPublishJob:
    @pytest.mark.asyncio
    async def test_publish_photo_success(self) -> None:
        """Mock gateway.post, verify creates job."""
        session = AsyncMock()
        session.flush = AsyncMock()
        service = PublishService(session)

        gateway = _mock_gateway()
        gateway.post.return_value = {"data": {"publish_id": "photo_pub_123"}}

        account = _mock_account()
        service._get_developer_gateway = AsyncMock(return_value=(account, gateway))

        workspace_id = uuid.uuid4()
        job = await service.create_photo_publish_job(
            workspace_id,
            photo_urls=["https://example.com/photo1.jpg"],
        )

        assert job.publish_id == "photo_pub_123"
        assert job.status == "PENDING"
        assert job.workspace_id == workspace_id
        session.add.assert_called_once_with(job)
        session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_publish_photo_creates_job_record(self) -> None:
        """Verify ContentPublishJob fields set correctly."""
        session = AsyncMock()
        session.flush = AsyncMock()
        service = PublishService(session)

        gateway = _mock_gateway()
        gateway.post.return_value = {"data": {"publish_id": "photo_pub_456"}}

        account = _mock_account()
        service._get_developer_gateway = AsyncMock(return_value=(account, gateway))

        workspace_id = uuid.uuid4()
        job = await service.create_photo_publish_job(
            workspace_id,
            photo_urls=["https://example.com/photo1.jpg"],
            title="My Photo Post",
            description="A nice sunset",
            privacy_level="SELF_ONLY",
            disable_comment=True,
        )

        assert job.publish_id == "photo_pub_456"
        assert job.title == "My Photo Post"
        assert job.video_url is None
        assert job.privacy_level == "SELF_ONLY"
        assert job.disable_comment is True
        assert job.connected_account_id == account.id

    @pytest.mark.asyncio
    async def test_publish_photo_with_title(self) -> None:
        """Verify title passed to API."""
        session = AsyncMock()
        session.flush = AsyncMock()
        service = PublishService(session)

        gateway = _mock_gateway()
        gateway.post.return_value = {"data": {"publish_id": "photo_pub_789"}}

        account = _mock_account()
        service._get_developer_gateway = AsyncMock(return_value=(account, gateway))

        workspace_id = uuid.uuid4()
        await service.create_photo_publish_job(
            workspace_id,
            photo_urls=["https://example.com/photo1.jpg"],
            title="Beach Day",
        )

        call_args = gateway.post.call_args
        body = call_args.kwargs.get("json_body") or call_args[1].get("json_body")
        assert body["post_info"]["title"] == "Beach Day"

    @pytest.mark.asyncio
    async def test_publish_photo_multiple_urls(self) -> None:
        """Verify multiple photo_images sent."""
        session = AsyncMock()
        session.flush = AsyncMock()
        service = PublishService(session)

        gateway = _mock_gateway()
        gateway.post.return_value = {"data": {"publish_id": "photo_pub_multi"}}

        account = _mock_account()
        service._get_developer_gateway = AsyncMock(return_value=(account, gateway))

        photo_urls = [
            "https://example.com/photo1.jpg",
            "https://example.com/photo2.jpg",
            "https://example.com/photo3.jpg",
        ]
        workspace_id = uuid.uuid4()
        await service.create_photo_publish_job(
            workspace_id,
            photo_urls=photo_urls,
        )

        call_args = gateway.post.call_args
        body = call_args.kwargs.get("json_body") or call_args[1].get("json_body")
        assert body["source_info"]["photo_images"] == photo_urls

    @pytest.mark.asyncio
    async def test_publish_photo_api_call_format(self) -> None:
        """Verify gateway.post body structure."""
        session = AsyncMock()
        session.flush = AsyncMock()
        service = PublishService(session)

        gateway = _mock_gateway()
        gateway.post.return_value = {"data": {"publish_id": "photo_pub_fmt"}}

        account = _mock_account()
        service._get_developer_gateway = AsyncMock(return_value=(account, gateway))

        workspace_id = uuid.uuid4()
        photo_urls = ["https://example.com/photo1.jpg"]
        await service.create_photo_publish_job(
            workspace_id,
            photo_urls=photo_urls,
            title="Test",
            description="Desc",
            privacy_level="PUBLIC_TO_EVERYONE",
            disable_comment=False,
            auto_add_music=True,
            photo_cover_index=0,
        )

        gateway.post.assert_called_once_with(
            "/post/publish/content/init/",
            json_body={
                "post_info": {
                    "title": "Test",
                    "description": "Desc",
                    "disable_comment": False,
                    "privacy_level": "PUBLIC_TO_EVERYONE",
                    "auto_add_music": True,
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "photo_cover_index": 0,
                    "photo_images": photo_urls,
                },
                "post_mode": "DIRECT_POST",
                "media_type": "PHOTO",
            },
        )


# ---------------------------------------------------------------------------
# Route tests
# ---------------------------------------------------------------------------


class TestQueryVideosRoute:
    @pytest.mark.asyncio
    @patch(f"{VIDEO_SVC}.query_videos_by_id")
    async def test_query_videos_route(self, mock_query: AsyncMock) -> None:
        mock_query.return_value = SAMPLE_VIDEOS

        workspace_id = uuid.uuid4()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/content/videos/query?workspace_id={workspace_id}",
                json={"video_ids": ["vid_001", "vid_002"]},
            )

        assert response.status_code == 200
        data = response.json()
        assert "videos" in data
        assert len(data["videos"]) == 2
        assert data["videos"][0]["id"] == "vid_001"


class TestPublishPhotoRoute:
    @pytest.mark.asyncio
    @patch(f"{PUBLISH_SVC}.create_photo_publish_job")
    async def test_publish_photo_route(self, mock_publish: AsyncMock) -> None:
        job_id = uuid.uuid4()
        account_id = uuid.uuid4()
        now = datetime(2026, 2, 22, 12, 0, 0, tzinfo=UTC)
        mock_publish.return_value = SimpleNamespace(
            id=str(job_id),
            publish_id="photo_pub_route_test",
            title="Route Photo",
            video_url=None,
            privacy_level="PUBLIC_TO_EVERYONE",
            status="PENDING",
            platform_video_id=None,
            error_message=None,
            created_at=now,
            updated_at=now,
        )

        workspace_id = uuid.uuid4()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/content/publish/photo?workspace_id={workspace_id}",
                json={
                    "photo_urls": ["https://example.com/photo1.jpg"],
                    "title": "Route Photo",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["publish_id"] == "photo_pub_route_test"
        assert data["title"] == "Route Photo"
        assert data["status"] == "PENDING"

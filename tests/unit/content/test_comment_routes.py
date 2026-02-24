"""Unit tests for comment routes in the content module."""

import uuid
from datetime import UTC, datetime
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


def _make_comment(**overrides) -> SimpleNamespace:
    """Helper to create a mock comment object."""
    defaults = {
        "id": str(uuid.uuid4()),
        "platform_comment_id": "plat_c_1",
        "parent_comment_id": None,
        "text": "Great video!",
        "like_count": 5,
        "reply_count": 1,
        "author_username": "testuser",
        "author_avatar_url": "https://example.com/avatar.jpg",
        "comment_create_time": datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC),
        "created_at": datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC),
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_video() -> SimpleNamespace:
    """Helper to create a mock video object."""
    return SimpleNamespace(
        id=uuid.uuid4(),
        platform_video_id="plat_v_1",
        title="Test Video",
        status="PUBLISHED",
    )


COMMENT_SVC = "backend.modules.content.services.comment_service.CommentService"
VIDEO_SVC = "backend.modules.content.services.video_service.VideoService"


class TestListComments:
    @pytest.mark.asyncio
    @patch(f"{COMMENT_SVC}.list_comments")
    async def test_list_comments_route(self, mock_list: AsyncMock) -> None:
        comment = _make_comment()
        mock_list.return_value = PaginatedResult(
            items=[comment], total=1, page=1, page_size=20
        )

        workspace_id = uuid.uuid4()
        video_id = uuid.uuid4()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/content/videos/{video_id}/comments"
                f"?workspace_id={workspace_id}",
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["page"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["text"] == "Great video!"

    @pytest.mark.asyncio
    @patch(f"{COMMENT_SVC}.list_comments")
    async def test_list_comments_empty(self, mock_list: AsyncMock) -> None:
        mock_list.return_value = PaginatedResult(
            items=[], total=0, page=1, page_size=20
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                f"/api/content/videos/{uuid.uuid4()}/comments"
                f"?workspace_id={uuid.uuid4()}",
            )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0


class TestSyncComments:
    @pytest.mark.asyncio
    @patch(f"{COMMENT_SVC}.sync_comments")
    @patch(f"{VIDEO_SVC}.get_video")
    async def test_sync_comments_route(
        self, mock_get_video: AsyncMock, mock_sync: AsyncMock
    ) -> None:
        video = _make_video()
        mock_get_video.return_value = video
        mock_sync.return_value = 15

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/content/videos/{uuid.uuid4()}/comments/sync"
                f"?workspace_id={uuid.uuid4()}",
            )

        assert response.status_code == 200
        assert response.json() == {"synced": 15}

    @pytest.mark.asyncio
    @patch(f"{VIDEO_SVC}.get_video")
    async def test_sync_comments_video_not_found(
        self, mock_get_video: AsyncMock
    ) -> None:
        mock_get_video.return_value = None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/content/videos/{uuid.uuid4()}/comments/sync"
                f"?workspace_id={uuid.uuid4()}",
            )

        assert response.status_code == 404


class TestReplyToComment:
    @pytest.mark.asyncio
    @patch(f"{COMMENT_SVC}.reply_to_comment")
    @patch(f"{VIDEO_SVC}.get_video")
    async def test_reply_to_comment_route(
        self, mock_get_video: AsyncMock, mock_reply: AsyncMock
    ) -> None:
        video = _make_video()
        mock_get_video.return_value = video
        mock_reply.return_value = {"comment_id": "new_reply_123"}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/content/videos/{uuid.uuid4()}/comments/abc123/reply"
                f"?workspace_id={uuid.uuid4()}",
                json={"text": "Thanks for watching!"},
            )

        assert response.status_code == 200
        assert response.json() == {"comment_id": "new_reply_123"}

    @pytest.mark.asyncio
    @patch(f"{VIDEO_SVC}.get_video")
    async def test_reply_video_not_found(self, mock_get_video: AsyncMock) -> None:
        mock_get_video.return_value = None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/content/videos/{uuid.uuid4()}/comments/abc123/reply"
                f"?workspace_id={uuid.uuid4()}",
                json={"text": "Hello"},
            )

        assert response.status_code == 404


class TestDeleteComment:
    @pytest.mark.asyncio
    @patch(f"{COMMENT_SVC}.delete_comment")
    @patch(f"{VIDEO_SVC}.get_video")
    async def test_delete_comment_route(
        self, mock_get_video: AsyncMock, mock_delete: AsyncMock
    ) -> None:
        video = _make_video()
        mock_get_video.return_value = video
        mock_delete.return_value = True

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete(
                f"/api/content/videos/{uuid.uuid4()}/comments/abc123"
                f"?workspace_id={uuid.uuid4()}",
            )

        assert response.status_code == 200
        assert response.json() == {"deleted": True}

    @pytest.mark.asyncio
    @patch(f"{VIDEO_SVC}.get_video")
    async def test_delete_video_not_found(self, mock_get_video: AsyncMock) -> None:
        mock_get_video.return_value = None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete(
                f"/api/content/videos/{uuid.uuid4()}/comments/abc123"
                f"?workspace_id={uuid.uuid4()}",
            )

        assert response.status_code == 404

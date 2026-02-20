"""Tests for OrganicAccountService — profile, posts, benchmarks, publish, hashtags."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.organic.services.account_service import OrganicAccountService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def workspace_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def connected_account_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def patched_build_gateway(mock_gateway: AsyncMock):
    with patch.object(
        OrganicAccountService,
        "_build_gateway",
        return_value=mock_gateway,
    ) as mock_build:
        yield mock_build


class TestGetProfile:
    @pytest.mark.asyncio
    async def test_get_profile(
        self,
        mock_session: AsyncMock,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        mock_gateway: AsyncMock,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"username": "brand_account", "followers": 10000}
        }

        service = OrganicAccountService(mock_session)
        result = await service.get_profile(workspace_id, connected_account_id)

        assert result["username"] == "brand_account"
        assert result["followers"] == 10000
        mock_gateway.get.assert_called_once_with("/accounts/profile/")
        patched_build_gateway.assert_called_once_with(connected_account_id)


class TestGetPosts:
    @pytest.mark.asyncio
    async def test_get_posts_default_pagination(
        self,
        mock_session: AsyncMock,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        mock_gateway: AsyncMock,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"posts": [{"id": "p1"}, {"id": "p2"}]}
        }

        service = OrganicAccountService(mock_session)
        result = await service.get_posts(workspace_id, connected_account_id)

        assert len(result["posts"]) == 2
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["page"] == "1"
        assert call_params["page_size"] == "20"

    @pytest.mark.asyncio
    async def test_get_posts_custom_pagination(
        self,
        mock_session: AsyncMock,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        mock_gateway: AsyncMock,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"posts": []}}

        service = OrganicAccountService(mock_session)
        await service.get_posts(
            workspace_id, connected_account_id, page=3, page_size=10
        )

        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["page"] == "3"
        assert call_params["page_size"] == "10"


class TestGetBenchmarks:
    @pytest.mark.asyncio
    async def test_get_benchmarks_no_category(
        self,
        mock_session: AsyncMock,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        mock_gateway: AsyncMock,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"avg_views": 5000, "avg_likes": 200}
        }

        service = OrganicAccountService(mock_session)
        result = await service.get_benchmarks(workspace_id, connected_account_id)

        assert result["avg_views"] == 5000
        mock_gateway.get.assert_called_once_with(
            "/accounts/benchmarks/", params=None
        )

    @pytest.mark.asyncio
    async def test_get_benchmarks_with_category(
        self,
        mock_session: AsyncMock,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        mock_gateway: AsyncMock,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"category": "fashion"}}

        service = OrganicAccountService(mock_session)
        result = await service.get_benchmarks(
            workspace_id, connected_account_id, category="fashion"
        )

        assert result["category"] == "fashion"
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["category"] == "fashion"


class TestPublishVideo:
    @pytest.mark.asyncio
    async def test_publish_video(
        self,
        mock_session: AsyncMock,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        mock_gateway: AsyncMock,
        patched_build_gateway,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"publish_id": "pub_123", "status": "PENDING"}
        }

        config = {"video_url": "https://example.com/video.mp4", "title": "My video"}
        service = OrganicAccountService(mock_session)
        result = await service.publish_video(
            workspace_id, connected_account_id, video_config=config
        )

        assert result["publish_id"] == "pub_123"
        mock_gateway.post.assert_called_once_with(
            "/accounts/posts/video/publish/",
            json_body=config,
        )


class TestPublishPhoto:
    @pytest.mark.asyncio
    async def test_publish_photo(
        self,
        mock_session: AsyncMock,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        mock_gateway: AsyncMock,
        patched_build_gateway,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"publish_id": "pub_456", "status": "PENDING"}
        }

        config = {"image_url": "https://example.com/photo.jpg", "caption": "Look!"}
        service = OrganicAccountService(mock_session)
        result = await service.publish_photo(
            workspace_id, connected_account_id, photo_config=config
        )

        assert result["publish_id"] == "pub_456"
        mock_gateway.post.assert_called_once_with(
            "/accounts/posts/photo/publish/",
            json_body=config,
        )


class TestGetPublishStatus:
    @pytest.mark.asyncio
    async def test_get_publish_status(
        self,
        mock_session: AsyncMock,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        mock_gateway: AsyncMock,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"publish_id": "pub_123", "status": "COMPLETE"}
        }

        service = OrganicAccountService(mock_session)
        result = await service.get_publish_status(
            workspace_id, connected_account_id, publish_id="pub_123"
        )

        assert result["status"] == "COMPLETE"
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["publish_id"] == "pub_123"


class TestRecommendHashtags:
    @pytest.mark.asyncio
    async def test_recommend_hashtags(
        self,
        mock_session: AsyncMock,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        mock_gateway: AsyncMock,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"hashtags": ["#fashion", "#style", "#ootd"]}
        }

        service = OrganicAccountService(mock_session)
        result = await service.recommend_hashtags(
            workspace_id, connected_account_id, text="summer fashion outfit"
        )

        assert len(result["hashtags"]) == 3
        assert "#fashion" in result["hashtags"]
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["text"] == "summer fashion outfit"

"""Tests for CreatorInsightService - discover, get insight, save."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.modules.intelligence.services.creator_insight_service import (
    CreatorInsightService,
)


class TestDiscoverCreators:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_discover_returns_creators_sorted_by_engagement(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        research_client = AsyncMock()
        research_client.query_videos = AsyncMock(
            return_value={
                "data": {
                    "videos": [
                        {
                            "username": "creator_a",
                            "like_count": 100,
                            "comment_count": 10,
                            "share_count": 5,
                            "view_count": 500,
                        },
                        {
                            "username": "creator_b",
                            "like_count": 500,
                            "comment_count": 50,
                            "share_count": 25,
                            "view_count": 5000,
                        },
                        {
                            "username": "creator_a",
                            "like_count": 200,
                            "comment_count": 20,
                            "share_count": 10,
                            "view_count": 1000,
                        },
                    ]
                }
            }
        )

        service = CreatorInsightService(session)
        creators = await service.discover_creators(
            workspace_id, research_client, keyword="dance"
        )

        assert len(creators) == 2
        # creator_b has higher avg_engagement (575 / 1 = 575)
        # creator_a has (100+10+5+200+20+10) / 2 = 172.5
        assert creators[0]["username"] == "creator_b"
        assert creators[1]["username"] == "creator_a"
        assert creators[1]["video_count"] == 2

    @pytest.mark.asyncio
    async def test_discover_empty_videos(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        research_client = AsyncMock()
        research_client.query_videos = AsyncMock(return_value={"data": {"videos": []}})

        service = CreatorInsightService(session)
        creators = await service.discover_creators(workspace_id, research_client)

        assert creators == []

    @pytest.mark.asyncio
    async def test_discover_videos_without_username(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        research_client = AsyncMock()
        research_client.query_videos = AsyncMock(
            return_value={
                "data": {
                    "videos": [
                        {
                            "username": None,
                            "like_count": 50,
                            "comment_count": 5,
                            "share_count": 1,
                            "view_count": 200,
                        },
                        {
                            "like_count": 50,
                            "comment_count": 5,
                            "share_count": 1,
                            "view_count": 200,
                        },
                    ]
                }
            }
        )

        service = CreatorInsightService(session)
        creators = await service.discover_creators(workspace_id, research_client)

        assert creators == []

    @pytest.mark.asyncio
    async def test_discover_with_hashtag_filter(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        research_client = AsyncMock()
        research_client.query_videos = AsyncMock(
            return_value={
                "data": {
                    "videos": [
                        {
                            "username": "dancer",
                            "like_count": 300,
                            "comment_count": 30,
                            "share_count": 15,
                            "view_count": 3000,
                        }
                    ]
                }
            }
        )

        service = CreatorInsightService(session)
        creators = await service.discover_creators(
            workspace_id, research_client, hashtag="dance"
        )

        assert len(creators) == 1
        assert creators[0]["username"] == "dancer"
        assert creators[0]["total_likes"] == 300
        research_client.query_videos.assert_called_once()
        call_kwargs = research_client.query_videos.call_args
        assert call_kwargs.kwargs.get("hashtag_name") == "dance"


class TestGetCreatorInsight:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_returns_full_insight(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        research_client = AsyncMock()
        research_client.query_user_info = AsyncMock(
            return_value={
                "data": {
                    "display_name": "Star Creator",
                    "follower_count": 100000,
                }
            }
        )
        research_client.query_videos = AsyncMock(
            return_value={
                "data": {
                    "videos": [
                        {
                            "like_count": 500,
                            "comment_count": 50,
                            "share_count": 25,
                            "view_count": 5000,
                        },
                        {
                            "like_count": 300,
                            "comment_count": 30,
                            "share_count": 15,
                            "view_count": 3000,
                        },
                    ]
                }
            }
        )

        service = CreatorInsightService(session)
        insight = await service.get_creator_insight(
            workspace_id, "starcreator", research_client
        )

        assert insight["username"] == "starcreator"
        assert insight["profile"]["display_name"] == "Star Creator"
        assert insight["video_count"] == 2
        assert insight["total_likes"] == 800
        assert insight["total_comments"] == 80
        assert insight["total_shares"] == 40
        assert insight["total_views"] == 8000
        assert insight["avg_engagement"] == 460.0  # (800+80+40)/2

    @pytest.mark.asyncio
    async def test_insight_no_videos(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        research_client = AsyncMock()
        research_client.query_user_info = AsyncMock(
            return_value={"data": {"display_name": "New Creator"}}
        )
        research_client.query_videos = AsyncMock(return_value={"data": {"videos": []}})

        service = CreatorInsightService(session)
        insight = await service.get_creator_insight(
            workspace_id, "newcreator", research_client
        )

        assert insight["video_count"] == 0
        assert insight["total_likes"] == 0
        assert insight["avg_engagement"] == 0.0


class TestSaveInsight:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.fixture
    def user_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_save_creates_research_query(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        service = CreatorInsightService(session)
        creator_data = {
            "username": "testcreator",
            "total_likes": 500,
        }
        result = await service.save_insight(workspace_id, creator_data, user_id)

        assert session.add.called
        added = session.add.call_args_list[0][0][0]
        assert added.name == "Creator Insight: testcreator"
        assert added.query_params == creator_data
        assert added.created_by == user_id
        assert result["name"] == "Creator Insight: testcreator"

    @pytest.mark.asyncio
    async def test_save_with_missing_username(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        service = CreatorInsightService(session)
        result = await service.save_insight(workspace_id, {"total_likes": 100}, user_id)

        added = session.add.call_args_list[0][0][0]
        assert added.name == "Creator Insight: unknown"

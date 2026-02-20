"""Tests for CompetitorService - add, remove, list, sync, detail, compare."""

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.modules.intelligence.services.competitor_service import CompetitorService


class TestAddCompetitor:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_add_competitor_creates_tracker(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        research_client = AsyncMock()
        research_client.query_user_info = AsyncMock(
            return_value={
                "data": {
                    "display_name": "Cool Creator",
                    "user_id": "12345",
                    "follower_count": 50000,
                }
            }
        )

        service = CompetitorService(session)
        result = await service.add_competitor(
            workspace_id, "coolcreator", research_client
        )

        assert session.add.called
        assert result["username"] == "coolcreator"
        assert result["display_name"] == "Cool Creator"
        assert result["profile_data"]["follower_count"] == 50000

    @pytest.mark.asyncio
    async def test_add_competitor_with_empty_profile(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        research_client = AsyncMock()
        research_client.query_user_info = AsyncMock(return_value={"data": {}})

        service = CompetitorService(session)
        result = await service.add_competitor(
            workspace_id, "unknown_user", research_client
        )

        assert result["username"] == "unknown_user"
        assert result["display_name"] is None


class TestRemoveCompetitor:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_remove_existing_competitor(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        session.delete = AsyncMock()
        session.flush = AsyncMock()

        tracker = SimpleNamespace(id=uuid.uuid4(), workspace_id=workspace_id)
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = tracker
        session.execute = AsyncMock(return_value=result_mock)

        service = CompetitorService(session)
        deleted = await service.remove_competitor(workspace_id, tracker.id)

        assert deleted is True
        session.delete.assert_called_once_with(tracker)

    @pytest.mark.asyncio
    async def test_remove_nonexistent_competitor(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=result_mock)

        service = CompetitorService(session)
        deleted = await service.remove_competitor(workspace_id, uuid.uuid4())

        assert deleted is False


class TestListCompetitors:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_list_returns_all_trackers(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        t1 = SimpleNamespace(
            id=uuid.uuid4(),
            username="user1",
            display_name="User One",
            profile_data={"follower_count": 100},
            last_synced_at=datetime(2026, 2, 19, tzinfo=timezone.utc),
        )
        t2 = SimpleNamespace(
            id=uuid.uuid4(),
            username="user2",
            display_name="User Two",
            profile_data={},
            last_synced_at=None,
        )
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [t1, t2]
        session.execute = AsyncMock(return_value=result_mock)

        service = CompetitorService(session)
        competitors = await service.list_competitors(workspace_id)

        assert len(competitors) == 2
        assert competitors[0]["username"] == "user1"
        assert competitors[1]["last_synced_at"] is None

    @pytest.mark.asyncio
    async def test_list_empty(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=result_mock)

        service = CompetitorService(session)
        competitors = await service.list_competitors(workspace_id)

        assert competitors == []


class TestSyncAllCompetitors:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_sync_creates_new_content(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        tracker_id = uuid.uuid4()
        tracker = SimpleNamespace(
            id=tracker_id,
            username="creator1",
            last_synced_at=None,
        )

        # First execute: list trackers; subsequent: content lookups (not found)
        tracker_result = MagicMock()
        tracker_result.scalars.return_value.all.return_value = [tracker]

        content_not_found = MagicMock()
        content_not_found.scalar_one_or_none.return_value = None

        session.execute = AsyncMock(
            side_effect=[tracker_result, content_not_found, content_not_found]
        )

        research_client = AsyncMock()
        research_client.query_videos = AsyncMock(
            return_value={
                "data": {
                    "videos": [
                        {
                            "id": "v1",
                            "video_description": "Cool video",
                            "like_count": 50,
                            "comment_count": 10,
                            "share_count": 5,
                            "view_count": 500,
                            "hashtag_names": ["dance"],
                            "create_time": 1708300000,
                        },
                        {
                            "id": "v2",
                            "video_description": "Another video",
                            "like_count": 100,
                            "comment_count": 20,
                            "share_count": 10,
                            "view_count": 1000,
                            "hashtag_names": ["fyp"],
                        },
                    ]
                }
            }
        )

        service = CompetitorService(session)
        count = await service.sync_all_competitors(workspace_id, research_client)

        assert count == 2
        assert session.add.call_count == 2

    @pytest.mark.asyncio
    async def test_sync_updates_existing_content(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        tracker_id = uuid.uuid4()
        tracker = SimpleNamespace(
            id=tracker_id,
            username="creator1",
            last_synced_at=None,
        )

        tracker_result = MagicMock()
        tracker_result.scalars.return_value.all.return_value = [tracker]

        existing_content = SimpleNamespace(
            id=uuid.uuid4(),
            tracker_id=tracker_id,
            video_id="v1",
            description="Old desc",
            metrics={"like_count": 10},
            hashtags=None,
        )
        content_found = MagicMock()
        content_found.scalar_one_or_none.return_value = existing_content

        session.execute = AsyncMock(side_effect=[tracker_result, content_found])

        research_client = AsyncMock()
        research_client.query_videos = AsyncMock(
            return_value={
                "data": {
                    "videos": [
                        {
                            "id": "v1",
                            "video_description": "Updated desc",
                            "like_count": 100,
                            "comment_count": 20,
                            "share_count": 10,
                            "view_count": 1000,
                            "hashtag_names": ["dance"],
                        },
                    ]
                }
            }
        )

        service = CompetitorService(session)
        count = await service.sync_all_competitors(workspace_id, research_client)

        # Existing content updated, not added as new
        assert count == 0
        assert existing_content.description == "Updated desc"
        assert existing_content.metrics["like_count"] == 100

    @pytest.mark.asyncio
    async def test_sync_no_competitors(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        session.flush = AsyncMock()

        tracker_result = MagicMock()
        tracker_result.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=tracker_result)

        research_client = AsyncMock()

        service = CompetitorService(session)
        count = await service.sync_all_competitors(workspace_id, research_client)

        assert count == 0
        research_client.query_videos.assert_not_called()


class TestGetCompetitorDetail:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_returns_detail_with_content(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        tracker_id = uuid.uuid4()
        tracker = SimpleNamespace(
            id=tracker_id,
            username="creator1",
            display_name="Creator One",
            profile_data={"follower_count": 5000},
            last_synced_at=datetime(2026, 2, 19, tzinfo=timezone.utc),
        )
        content = SimpleNamespace(
            id=uuid.uuid4(),
            video_id="v1",
            description="A cool video",
            metrics={"like_count": 50},
            hashtags=["dance"],
            published_at=datetime(2026, 2, 18, tzinfo=timezone.utc),
        )

        tracker_result = MagicMock()
        tracker_result.scalar_one_or_none.return_value = tracker
        content_result = MagicMock()
        content_result.scalars.return_value.all.return_value = [content]

        session.execute = AsyncMock(
            side_effect=[tracker_result, content_result]
        )

        service = CompetitorService(session)
        detail = await service.get_competitor_detail(workspace_id, tracker_id)

        assert detail is not None
        assert detail["username"] == "creator1"
        assert len(detail["content"]) == 1
        assert detail["content"][0]["video_id"] == "v1"

    @pytest.mark.asyncio
    async def test_returns_none_for_missing(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=result_mock)

        service = CompetitorService(session)
        detail = await service.get_competitor_detail(
            workspace_id, uuid.uuid4()
        )

        assert detail is None


class TestCompareCompetitors:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_compare_multiple_competitors(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()

        id1 = uuid.uuid4()
        id2 = uuid.uuid4()

        tracker1 = SimpleNamespace(
            id=id1, username="user1", display_name="User 1"
        )
        tracker2 = SimpleNamespace(
            id=id2, username="user2", display_name="User 2"
        )

        content1 = SimpleNamespace(
            metrics={"like_count": 100, "comment_count": 10, "share_count": 5, "view_count": 500}
        )
        content2 = SimpleNamespace(
            metrics={"like_count": 200, "comment_count": 20, "share_count": 10, "view_count": 1000}
        )

        tracker1_result = MagicMock()
        tracker1_result.scalar_one_or_none.return_value = tracker1
        content1_result = MagicMock()
        content1_result.scalars.return_value.all.return_value = [content1]

        tracker2_result = MagicMock()
        tracker2_result.scalar_one_or_none.return_value = tracker2
        content2_result = MagicMock()
        content2_result.scalars.return_value.all.return_value = [content2]

        session.execute = AsyncMock(
            side_effect=[
                tracker1_result,
                content1_result,
                tracker2_result,
                content2_result,
            ]
        )

        service = CompetitorService(session)
        comparisons = await service.compare_competitors(
            workspace_id, [id1, id2]
        )

        assert len(comparisons) == 2
        assert comparisons[0]["username"] == "user1"
        assert comparisons[0]["total_likes"] == 100
        assert comparisons[0]["total_views"] == 500
        assert comparisons[0]["avg_engagement"] == 115.0  # (100+10+5)/1
        assert comparisons[1]["username"] == "user2"
        assert comparisons[1]["total_likes"] == 200

    @pytest.mark.asyncio
    async def test_compare_skips_missing_competitors(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()

        missing_result = MagicMock()
        missing_result.scalar_one_or_none.return_value = None

        session.execute = AsyncMock(return_value=missing_result)

        service = CompetitorService(session)
        comparisons = await service.compare_competitors(
            workspace_id, [uuid.uuid4()]
        )

        assert comparisons == []

    @pytest.mark.asyncio
    async def test_compare_empty_ids(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()

        service = CompetitorService(session)
        comparisons = await service.compare_competitors(workspace_id, [])

        assert comparisons == []

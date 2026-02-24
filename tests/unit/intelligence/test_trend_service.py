"""Tests for TrendService - sync, query, and history."""

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.modules.intelligence.services.trend_service import TrendService


class TestSyncTrends:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_sync_trends_creates_snapshots_from_videos(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        research_client = AsyncMock()
        research_client.query_videos = AsyncMock(
            return_value={
                "data": {
                    "videos": [
                        {
                            "hashtag_names": ["dance", "trending"],
                            "like_count": 100,
                            "comment_count": 20,
                            "share_count": 5,
                            "view_count": 1000,
                        },
                        {
                            "hashtag_names": ["dance"],
                            "like_count": 200,
                            "comment_count": 30,
                            "share_count": 10,
                            "view_count": 2000,
                        },
                    ]
                }
            }
        )

        service = TrendService(session)
        count = await service.sync_trends(workspace_id, research_client)

        assert count == 2  # "dance" and "trending"
        assert session.add.call_count == 2
        assert session.flush.called

    @pytest.mark.asyncio
    async def test_sync_trends_empty_videos(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        research_client = AsyncMock()
        research_client.query_videos = AsyncMock(return_value={"data": {"videos": []}})

        service = TrendService(session)
        count = await service.sync_trends(workspace_id, research_client)

        assert count == 0
        assert session.add.call_count == 0

    @pytest.mark.asyncio
    async def test_sync_trends_videos_without_hashtags(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        research_client = AsyncMock()
        research_client.query_videos = AsyncMock(
            return_value={
                "data": {
                    "videos": [
                        {
                            "hashtag_names": None,
                            "like_count": 50,
                            "comment_count": 5,
                            "share_count": 1,
                            "view_count": 500,
                        }
                    ]
                }
            }
        )

        service = TrendService(session)
        count = await service.sync_trends(workspace_id, research_client)

        assert count == 0

    @pytest.mark.asyncio
    async def test_sync_trends_aggregates_engagement(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        research_client = AsyncMock()
        research_client.query_videos = AsyncMock(
            return_value={
                "data": {
                    "videos": [
                        {
                            "hashtag_names": ["fyp"],
                            "like_count": 100,
                            "comment_count": 0,
                            "share_count": 0,
                            "view_count": 0,
                        },
                        {
                            "hashtag_names": ["fyp"],
                            "like_count": 200,
                            "comment_count": 0,
                            "share_count": 0,
                            "view_count": 0,
                        },
                    ]
                }
            }
        )

        service = TrendService(session)
        await service.sync_trends(workspace_id, research_client)

        # The snapshot for "fyp" should have engagement = 100 + 200 = 300
        added = session.add.call_args_list[0][0][0]
        assert added.engagement_score == 300.0

    @pytest.mark.asyncio
    async def test_sync_trends_no_data_key(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        research_client = AsyncMock()
        research_client.query_videos = AsyncMock(return_value={})

        service = TrendService(session)
        count = await service.sync_trends(workspace_id, research_client)

        assert count == 0


class TestGetTrendingHashtags:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_returns_hashtags_ordered_by_score(
        self, workspace_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        snap1 = SimpleNamespace(
            id=uuid.uuid4(),
            name="dance",
            engagement_score=500.0,
            region=None,
            captured_at=datetime(2026, 2, 19, tzinfo=UTC),
            metadata_json=None,
        )
        snap2 = SimpleNamespace(
            id=uuid.uuid4(),
            name="fyp",
            engagement_score=1000.0,
            region="US",
            captured_at=datetime(2026, 2, 19, tzinfo=UTC),
            metadata_json={"extra": True},
        )
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [snap2, snap1]
        session.execute = AsyncMock(return_value=result_mock)

        service = TrendService(session)
        hashtags = await service.get_trending_hashtags(workspace_id, limit=10)

        assert len(hashtags) == 2
        assert hashtags[0]["name"] == "fyp"
        assert hashtags[0]["engagement_score"] == 1000.0
        assert hashtags[0]["region"] == "US"
        assert hashtags[1]["name"] == "dance"

    @pytest.mark.asyncio
    async def test_returns_empty_list(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=result_mock)

        service = TrendService(session)
        hashtags = await service.get_trending_hashtags(workspace_id)

        assert hashtags == []


class TestGetTrendingSounds:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_returns_sounds(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        snap = SimpleNamespace(
            id=uuid.uuid4(),
            name="cool_beat",
            engagement_score=750.0,
            region=None,
            captured_at=datetime(2026, 2, 19, tzinfo=UTC),
            metadata_json=None,
        )
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [snap]
        session.execute = AsyncMock(return_value=result_mock)

        service = TrendService(session)
        sounds = await service.get_trending_sounds(workspace_id)

        assert len(sounds) == 1
        assert sounds[0]["name"] == "cool_beat"

    @pytest.mark.asyncio
    async def test_returns_empty_sounds(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=result_mock)

        service = TrendService(session)
        sounds = await service.get_trending_sounds(workspace_id)

        assert sounds == []


class TestGetTrendHistory:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_returns_time_series(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        snap1 = SimpleNamespace(
            captured_at=datetime(2026, 2, 10, tzinfo=UTC),
            engagement_score=100.0,
        )
        snap2 = SimpleNamespace(
            captured_at=datetime(2026, 2, 15, tzinfo=UTC),
            engagement_score=250.0,
        )
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [snap1, snap2]
        session.execute = AsyncMock(return_value=result_mock)

        service = TrendService(session)
        history = await service.get_trend_history(workspace_id, "dance", days=30)

        assert len(history) == 2
        assert history[0]["engagement_score"] == 100.0
        assert history[1]["engagement_score"] == 250.0

    @pytest.mark.asyncio
    async def test_returns_empty_history(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=result_mock)

        service = TrendService(session)
        history = await service.get_trend_history(workspace_id, "nonexistent", days=7)

        assert history == []

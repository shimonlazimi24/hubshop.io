"""Tests for expanded SparkAdsService and CreatorService performance reporting."""

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.modules.creators.services.creator_service import CreatorService
from backend.modules.creators.services.spark_ads_service import SparkAdsService

# ---------------------------------------------------------------------------
# cancel_authorization
# ---------------------------------------------------------------------------


class TestCancelAuthorization:
    @pytest.mark.asyncio
    async def test_cancel_authorization_pending(self) -> None:
        """Pending auth becomes REVOKED."""
        auth = SimpleNamespace(
            id=uuid.uuid4(),
            status="PENDING",
        )
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = auth
        session.execute.return_value = result

        service = SparkAdsService(session)
        updated = await service.cancel_authorization(auth.id)

        assert updated is not None
        assert updated.status == "REVOKED"

    @pytest.mark.asyncio
    async def test_cancel_authorization_not_pending(self) -> None:
        """Non-pending auth remains unchanged."""
        auth = SimpleNamespace(
            id=uuid.uuid4(),
            status="APPROVED",
        )
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = auth
        session.execute.return_value = result

        service = SparkAdsService(session)
        updated = await service.cancel_authorization(auth.id)

        assert updated is not None
        assert updated.status == "APPROVED"

    @pytest.mark.asyncio
    async def test_cancel_authorization_not_found(self) -> None:
        """Returns None when authorization does not exist."""
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result

        service = SparkAdsService(session)
        updated = await service.cancel_authorization(uuid.uuid4())

        assert updated is None


# ---------------------------------------------------------------------------
# get_authorization_code
# ---------------------------------------------------------------------------


class TestGetAuthorizationCode:
    @pytest.mark.asyncio
    async def test_get_code_approved(self) -> None:
        """Approved auth returns the authorization code."""
        auth = SimpleNamespace(
            id=uuid.uuid4(),
            status="APPROVED",
            authorization_code="SPARK_CODE_123",
        )
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = auth
        session.execute.return_value = result

        service = SparkAdsService(session)
        code = await service.get_authorization_code(auth.id)

        assert code == "SPARK_CODE_123"

    @pytest.mark.asyncio
    async def test_get_code_pending(self) -> None:
        """Pending auth returns None."""
        auth = SimpleNamespace(
            id=uuid.uuid4(),
            status="PENDING",
            authorization_code=None,
        )
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = auth
        session.execute.return_value = result

        service = SparkAdsService(session)
        code = await service.get_authorization_code(auth.id)

        assert code is None

    @pytest.mark.asyncio
    async def test_get_code_not_found(self) -> None:
        """Returns None when authorization does not exist."""
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result

        service = SparkAdsService(session)
        code = await service.get_authorization_code(uuid.uuid4())

        assert code is None


# ---------------------------------------------------------------------------
# list_authorized_videos
# ---------------------------------------------------------------------------


class TestListAuthorizedVideos:
    @pytest.mark.asyncio
    async def test_list_authorized_videos(self) -> None:
        """Returns only APPROVED authorizations."""
        workspace_id = uuid.uuid4()
        auths = [
            SimpleNamespace(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                status="APPROVED",
                authorization_code="CODE_A",
                created_at=datetime.now(tz=UTC),
            ),
            SimpleNamespace(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                status="APPROVED",
                authorization_code="CODE_B",
                created_at=datetime.now(tz=UTC),
            ),
        ]
        session = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = auths
        session.execute.return_value = result

        service = SparkAdsService(session)
        videos = await service.list_authorized_videos(workspace_id)

        assert len(videos) == 2
        assert videos[0].authorization_code == "CODE_A"
        assert videos[1].authorization_code == "CODE_B"

    @pytest.mark.asyncio
    async def test_list_authorized_empty(self) -> None:
        """No approved auths returns empty list."""
        session = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        session.execute.return_value = result

        service = SparkAdsService(session)
        videos = await service.list_authorized_videos(uuid.uuid4())

        assert videos == []


# ---------------------------------------------------------------------------
# get_creator_performance
# ---------------------------------------------------------------------------


class TestCreatorPerformance:
    @pytest.mark.asyncio
    async def test_creator_performance(self) -> None:
        """Verify all fields are returned correctly."""
        creator_id = uuid.uuid4()
        creator = SimpleNamespace(
            id=creator_id,
            username="sparkstar",
            display_name="Spark Star",
            follower_count=100000,
            following_count=500,
            likes_count=2500000,
            video_count=100,
            tier="MACRO",
            engagement_rate="3.5",
        )
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = creator
        session.execute.return_value = result

        service = CreatorService(session)
        perf = await service.get_creator_performance(creator_id)

        assert perf["creator_id"] == str(creator_id)
        assert perf["username"] == "sparkstar"
        assert perf["display_name"] == "Spark Star"
        assert perf["follower_count"] == 100000
        assert perf["following_count"] == 500
        assert perf["likes_count"] == 2500000
        assert perf["video_count"] == 100
        assert perf["tier"] == "MACRO"
        assert perf["engagement_rate"] == 3.5
        assert perf["avg_likes_per_video"] == 25000.0

    @pytest.mark.asyncio
    async def test_creator_performance_not_found(self) -> None:
        """Returns empty dict when creator does not exist."""
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result

        service = CreatorService(session)
        perf = await service.get_creator_performance(uuid.uuid4())

        assert perf == {}

"""Tests for ContentCreatorBridge — cross-module content-to-creator Spark Ads integration."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.modules.content.services.content_creator_bridge import (
    ContentCreatorBridge,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scalar_result(value: object) -> MagicMock:
    """Create a mock execute result that returns *value* from scalar_one_or_none."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def _scalars_result(values: list) -> MagicMock:
    """Create a mock execute result that returns *values* from scalars().all()."""
    result = MagicMock()
    result.scalars.return_value.all.return_value = values
    return result


# ---------------------------------------------------------------------------
# get_video_with_creator
# ---------------------------------------------------------------------------


class TestGetVideoWithCreator:
    @pytest.mark.asyncio
    async def test_get_video_with_creator(self) -> None:
        """Video found with associated creator and authorization."""
        workspace_id = uuid.uuid4()
        video_id = uuid.uuid4()
        creator_id = uuid.uuid4()

        video = SimpleNamespace(
            id=video_id,
            workspace_id=workspace_id,
            platform_video_id="plat_vid_001",
            title="Viral Dance",
            view_count=50000,
            like_count=3000,
            comment_count=200,
            share_count=150,
        )
        auth = SimpleNamespace(
            workspace_id=workspace_id,
            creator_id=creator_id,
            platform_video_id="plat_vid_001",
            status="APPROVED",
            authorization_code="SPARK_ABC",
        )
        creator = SimpleNamespace(
            id=creator_id,
            username="sparkstar",
            display_name="Spark Star",
            avatar_url="https://example.com/avatar.jpg",
            tier="MACRO",
        )

        session = AsyncMock()
        session.execute.side_effect = [
            _scalar_result(video),
            _scalar_result(auth),
            _scalar_result(creator),
        ]

        service = ContentCreatorBridge(session)
        result = await service.get_video_with_creator(video_id, workspace_id)

        assert result["video"]["video_id"] == str(video_id)
        assert result["video"]["platform_video_id"] == "plat_vid_001"
        assert result["video"]["title"] == "Viral Dance"
        assert result["video"]["view_count"] == 50000
        assert result["video"]["like_count"] == 3000
        assert result["video"]["comment_count"] == 200
        assert result["video"]["share_count"] == 150

        assert result["creator"]["creator_id"] == str(creator_id)
        assert result["creator"]["username"] == "sparkstar"
        assert result["creator"]["display_name"] == "Spark Star"
        assert result["creator"]["avatar_url"] == "https://example.com/avatar.jpg"
        assert result["creator"]["tier"] == "MACRO"

        assert result["authorization"]["status"] == "APPROVED"
        assert result["authorization"]["authorization_code"] == "SPARK_ABC"

    @pytest.mark.asyncio
    async def test_get_video_with_creator_no_auth(self) -> None:
        """Video found but no authorization exists."""
        workspace_id = uuid.uuid4()
        video_id = uuid.uuid4()

        video = SimpleNamespace(
            id=video_id,
            workspace_id=workspace_id,
            platform_video_id="plat_vid_002",
            title="Cooking Hack",
            view_count=10000,
            like_count=800,
            comment_count=50,
            share_count=20,
        )

        session = AsyncMock()
        session.execute.side_effect = [
            _scalar_result(video),
            _scalar_result(None),  # no auth
        ]

        service = ContentCreatorBridge(session)
        result = await service.get_video_with_creator(video_id, workspace_id)

        assert result["video"]["video_id"] == str(video_id)
        assert result["video"]["title"] == "Cooking Hack"
        assert result["creator"] is None
        assert result["authorization"] is None

    @pytest.mark.asyncio
    async def test_get_video_not_found(self) -> None:
        """Returns empty dict when video does not exist."""
        session = AsyncMock()
        session.execute.side_effect = [
            _scalar_result(None),
        ]

        service = ContentCreatorBridge(session)
        result = await service.get_video_with_creator(uuid.uuid4(), uuid.uuid4())

        assert result == {}


# ---------------------------------------------------------------------------
# request_spark_ad_for_video
# ---------------------------------------------------------------------------


class TestRequestSparkAdForVideo:
    @pytest.mark.asyncio
    async def test_request_spark_ad(self) -> None:
        """Creates authorization with correct fields."""
        workspace_id = uuid.uuid4()
        video_id = uuid.uuid4()
        creator_id = uuid.uuid4()

        video = SimpleNamespace(
            id=video_id,
            workspace_id=workspace_id,
            platform_video_id="plat_vid_003",
        )

        session = AsyncMock()
        session.add = MagicMock()  # add() is synchronous in SQLAlchemy
        session.execute.side_effect = [
            _scalar_result(video),  # video lookup
            _scalar_result(None),  # duplicate check (no existing auth)
        ]

        service = ContentCreatorBridge(session)
        auth = await service.request_spark_ad_for_video(
            workspace_id, video_id, creator_id
        )

        assert auth.workspace_id == workspace_id
        assert auth.creator_id == creator_id
        assert auth.platform_video_id == "plat_vid_003"
        assert auth.status == "PENDING"
        session.add.assert_called_once_with(auth)
        session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_request_spark_ad_video_not_found(self) -> None:
        """Raises ValueError when video does not exist."""
        session = AsyncMock()
        session.execute.side_effect = [
            _scalar_result(None),
        ]

        service = ContentCreatorBridge(session)
        video_id = uuid.uuid4()

        with pytest.raises(ValueError, match=str(video_id)):
            await service.request_spark_ad_for_video(
                uuid.uuid4(), video_id, uuid.uuid4()
            )

    @pytest.mark.asyncio
    async def test_request_spark_ad_duplicate_rejected(self) -> None:
        """Raises ValueError when authorization already exists."""
        workspace_id = uuid.uuid4()
        video_id = uuid.uuid4()
        creator_id = uuid.uuid4()

        video = SimpleNamespace(
            id=video_id,
            workspace_id=workspace_id,
            platform_video_id="plat_vid_dup",
        )
        existing_auth = SimpleNamespace(
            workspace_id=workspace_id,
            creator_id=creator_id,
            platform_video_id="plat_vid_dup",
            status="PENDING",
        )

        session = AsyncMock()
        session.execute.side_effect = [
            _scalar_result(video),  # video lookup
            _scalar_result(existing_auth),  # duplicate check finds existing
        ]

        service = ContentCreatorBridge(session)
        with pytest.raises(ValueError, match="already exists"):
            await service.request_spark_ad_for_video(workspace_id, video_id, creator_id)


# ---------------------------------------------------------------------------
# get_creator_content_summary
# ---------------------------------------------------------------------------


class TestGetCreatorContentSummary:
    @pytest.mark.asyncio
    async def test_creator_content_summary(self) -> None:
        """Creator with mixed authorizations returns correct counts."""
        workspace_id = uuid.uuid4()
        creator_id = uuid.uuid4()

        creator = SimpleNamespace(
            id=creator_id,
            workspace_id=workspace_id,
            username="creatorX",
            display_name="Creator X",
            follower_count=250000,
            tier="MACRO",
        )
        authorizations = [
            SimpleNamespace(status="APPROVED", platform_video_id="vid_a"),
            SimpleNamespace(status="APPROVED", platform_video_id="vid_b"),
            SimpleNamespace(status="PENDING", platform_video_id="vid_c"),
            SimpleNamespace(status="REJECTED", platform_video_id="vid_d"),
        ]

        session = AsyncMock()
        session.execute.side_effect = [
            _scalar_result(creator),
            _scalars_result(authorizations),
        ]

        service = ContentCreatorBridge(session)
        result = await service.get_creator_content_summary(workspace_id, creator_id)

        assert result["creator"]["creator_id"] == str(creator_id)
        assert result["creator"]["username"] == "creatorX"
        assert result["creator"]["display_name"] == "Creator X"
        assert result["creator"]["follower_count"] == 250000
        assert result["creator"]["tier"] == "MACRO"

        assert result["authorizations"]["total"] == 4
        assert result["authorizations"]["approved"] == 2
        assert result["authorizations"]["pending"] == 1

        assert result["authorized_video_ids"] == ["vid_a", "vid_b"]

    @pytest.mark.asyncio
    async def test_creator_content_summary_empty(self) -> None:
        """Creator with no authorizations returns zero counts."""
        workspace_id = uuid.uuid4()
        creator_id = uuid.uuid4()

        creator = SimpleNamespace(
            id=creator_id,
            workspace_id=workspace_id,
            username="newcreator",
            display_name="New Creator",
            follower_count=500,
            tier="NANO",
        )

        session = AsyncMock()
        session.execute.side_effect = [
            _scalar_result(creator),
            _scalars_result([]),
        ]

        service = ContentCreatorBridge(session)
        result = await service.get_creator_content_summary(workspace_id, creator_id)

        assert result["creator"]["creator_id"] == str(creator_id)
        assert result["authorizations"]["total"] == 0
        assert result["authorizations"]["approved"] == 0
        assert result["authorizations"]["pending"] == 0
        assert result["authorized_video_ids"] == []

    @pytest.mark.asyncio
    async def test_creator_content_summary_not_found(self) -> None:
        """Returns empty dict when creator does not exist."""
        session = AsyncMock()
        session.execute.side_effect = [
            _scalar_result(None),
        ]

        service = ContentCreatorBridge(session)
        result = await service.get_creator_content_summary(uuid.uuid4(), uuid.uuid4())

        assert result == {}

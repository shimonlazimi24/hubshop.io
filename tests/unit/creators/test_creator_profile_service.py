"""Tests for CreatorProfileService - list, get, save, upsert from API."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.db.models.creators import CreatorProfile
from backend.modules.creators.services.creator_profile_service import (
    CreatorProfileService,
)


class TestListCreators:
    @pytest.mark.asyncio
    async def test_list_creators_paginated(self) -> None:
        session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 2
        creator1 = SimpleNamespace(
            id=uuid.uuid4(), username="creator1", display_name="Creator One"
        )
        creator2 = SimpleNamespace(
            id=uuid.uuid4(), username="creator2", display_name="Creator Two"
        )
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = [creator1, creator2]

        session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = CreatorProfileService(session)
        result = await service.list_creators(uuid.uuid4(), page=1, page_size=20)

        assert result.total == 2
        assert len(result.items) == 2
        assert result.page == 1
        assert result.page_size == 20

    @pytest.mark.asyncio
    async def test_list_creators_empty(self) -> None:
        session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []

        session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = CreatorProfileService(session)
        result = await service.list_creators(uuid.uuid4())

        assert result.total == 0
        assert result.items == []
        assert result.total_pages == 0

    @pytest.mark.asyncio
    async def test_list_creators_filtered_by_tier(self) -> None:
        session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 1
        mega_creator = SimpleNamespace(
            id=uuid.uuid4(),
            username="mega_star",
            display_name="Mega Star",
            tier="MEGA",
        )
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = [mega_creator]

        session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = CreatorProfileService(session)
        result = await service.list_creators(
            uuid.uuid4(), tier="MEGA", page=1, page_size=10
        )

        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].tier == "MEGA"


class TestGetCreator:
    @pytest.mark.asyncio
    async def test_get_creator_found(self) -> None:
        creator = SimpleNamespace(
            id=uuid.uuid4(),
            username="found_creator",
            display_name="Found Creator",
        )
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = creator
        session.execute.return_value = result

        service = CreatorProfileService(session)
        found = await service.get_creator(creator.id)

        assert found is not None
        assert found.username == "found_creator"
        assert found.display_name == "Found Creator"

    @pytest.mark.asyncio
    async def test_get_creator_not_found(self) -> None:
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result

        service = CreatorProfileService(session)
        found = await service.get_creator(uuid.uuid4())

        assert found is None


class TestSaveCreator:
    @pytest.mark.asyncio
    async def test_save_creator_toggle(self) -> None:
        creator = SimpleNamespace(
            id=uuid.uuid4(),
            username="save_me",
            is_saved=False,
        )
        session = AsyncMock()
        # get_creator internally calls session.execute
        result = MagicMock()
        result.scalar_one_or_none.return_value = creator
        session.execute.return_value = result

        service = CreatorProfileService(session)
        updated = await service.save_creator(creator.id, is_saved=True)

        assert updated is not None
        assert updated.is_saved is True

    @pytest.mark.asyncio
    async def test_save_creator_not_found(self) -> None:
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result

        service = CreatorProfileService(session)
        updated = await service.save_creator(uuid.uuid4(), is_saved=True)

        assert updated is None


class TestUpsertCreator:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def sample_creator_data(self) -> dict:
        return {
            "creator_id": "tt_creator_001",
            "username": "new_creator",
            "display_name": "New Creator",
            "avatar_url": "https://example.com/avatar.jpg",
            "bio": "Hello TikTok!",
            "follower_count": 50_000,
            "following_count": 200,
            "likes_count": 1_000_000,
            "video_count": 150,
            "engagement_rate": 4.5,
            "categories": ["comedy", "lifestyle"],
        }

    @pytest.mark.asyncio
    async def test_upsert_creator_creates_new(
        self,
        mock_session: AsyncMock,
        sample_creator_data: dict,
    ) -> None:
        workspace_id = uuid.uuid4()
        service = CreatorProfileService(mock_session)
        creator = await service.upsert_creator_from_api(
            workspace_id, sample_creator_data
        )

        assert mock_session.add.called
        added = mock_session.add.call_args_list[0][0][0]
        assert isinstance(added, CreatorProfile)
        assert added.platform_creator_id == "tt_creator_001"
        assert added.username == "new_creator"
        assert added.display_name == "New Creator"
        assert added.follower_count == 50_000
        assert added.tier == "MICRO"
        assert added.is_saved is False
        assert added.detail_json == sample_creator_data

    @pytest.mark.asyncio
    async def test_upsert_creator_updates_existing(
        self,
        mock_session: AsyncMock,
        sample_creator_data: dict,
    ) -> None:
        existing = SimpleNamespace(
            id=uuid.uuid4(),
            platform_creator_id="tt_creator_001",
            username="old_name",
            display_name="Old Display",
            avatar_url="https://example.com/old.jpg",
            bio="Old bio",
            follower_count=10_000,
            following_count=100,
            likes_count=500_000,
            video_count=80,
            tier="MICRO",
            engagement_rate="2.0",
            categories=None,
            audience_demographics=None,
            detail_json=None,
        )
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = existing
        mock_session.execute.return_value = result_mock

        workspace_id = uuid.uuid4()
        service = CreatorProfileService(mock_session)
        await service.upsert_creator_from_api(workspace_id, sample_creator_data)

        assert existing.username == "new_creator"
        assert existing.display_name == "New Creator"
        assert existing.follower_count == 50_000
        assert existing.tier == "MICRO"
        assert existing.detail_json == sample_creator_data
        # Should not add when updating
        assert not mock_session.add.called

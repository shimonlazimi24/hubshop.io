"""Tests for DataSourceService - register, list, toggle."""

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.modules.intelligence.services.data_source_service import (
    _DATASOURCE_PREFIX,
    DataSourceService,
)


class TestRegisterSource:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.fixture
    def user_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_register_creates_source(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        service = DataSourceService(session)
        result = await service.register_source(
            workspace_id,
            {
                "name": "TikTok Research",
                "source_type": "tiktok_research",
                "enabled": True,
                "settings": {"region": "US"},
            },
            user_id,
        )

        assert session.add.called
        added = session.add.call_args_list[0][0][0]
        assert added.name == f"{_DATASOURCE_PREFIX}TikTok Research"
        assert added.query_params["source_type"] == "tiktok_research"
        assert added.query_params["enabled"] is True
        assert added.query_params["settings"]["region"] == "US"
        assert added.created_by == user_id

    @pytest.mark.asyncio
    async def test_register_defaults(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        service = DataSourceService(session)
        result = await service.register_source(
            workspace_id,
            {"name": "Minimal Source"},
            user_id,
        )

        added = session.add.call_args_list[0][0][0]
        assert added.query_params["source_type"] == "unknown"
        assert added.query_params["enabled"] is True
        assert added.query_params["settings"] == {}

    @pytest.mark.asyncio
    async def test_register_disabled_source(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()

        service = DataSourceService(session)
        await service.register_source(
            workspace_id,
            {
                "name": "Disabled Source",
                "source_type": "test",
                "enabled": False,
            },
            user_id,
        )

        added = session.add.call_args_list[0][0][0]
        assert added.query_params["enabled"] is False


class TestListSources:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_list_returns_all_sources(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        src1 = SimpleNamespace(
            id=uuid.uuid4(),
            name=f"{_DATASOURCE_PREFIX}Source A",
            query_params={
                "source_type": "tiktok_research",
                "enabled": True,
                "settings": {},
            },
            created_at=datetime(2026, 2, 19, tzinfo=UTC),
        )
        src2 = SimpleNamespace(
            id=uuid.uuid4(),
            name=f"{_DATASOURCE_PREFIX}Source B",
            query_params={
                "source_type": "tiktok_marketing",
                "enabled": False,
                "settings": {"api_version": "v1.3"},
            },
            created_at=datetime(2026, 2, 18, tzinfo=UTC),
        )
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [src1, src2]
        session.execute = AsyncMock(return_value=result_mock)

        service = DataSourceService(session)
        sources = await service.list_sources(workspace_id)

        assert len(sources) == 2
        assert sources[0]["name"] == "Source A"
        assert sources[0]["source_type"] == "tiktok_research"
        assert sources[0]["enabled"] is True
        assert sources[1]["name"] == "Source B"
        assert sources[1]["enabled"] is False

    @pytest.mark.asyncio
    async def test_list_empty(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=result_mock)

        service = DataSourceService(session)
        sources = await service.list_sources(workspace_id)

        assert sources == []


class TestToggleSource:
    @pytest.fixture
    def workspace_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @pytest.mark.asyncio
    async def test_toggle_enables_source(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        session.flush = AsyncMock()

        source_id = uuid.uuid4()
        source = SimpleNamespace(
            id=source_id,
            name=f"{_DATASOURCE_PREFIX}Test Source",
            query_params={
                "source_type": "test",
                "enabled": False,
                "settings": {},
            },
            created_at=datetime(2026, 2, 19, tzinfo=UTC),
        )
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = source
        session.execute = AsyncMock(return_value=result_mock)

        service = DataSourceService(session)
        result = await service.toggle_source(workspace_id, source_id, True)

        assert result is not None
        assert result["enabled"] is True
        assert source.query_params["enabled"] is True

    @pytest.mark.asyncio
    async def test_toggle_disables_source(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        session.flush = AsyncMock()

        source_id = uuid.uuid4()
        source = SimpleNamespace(
            id=source_id,
            name=f"{_DATASOURCE_PREFIX}Active Source",
            query_params={
                "source_type": "test",
                "enabled": True,
                "settings": {},
            },
            created_at=datetime(2026, 2, 19, tzinfo=UTC),
        )
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = source
        session.execute = AsyncMock(return_value=result_mock)

        service = DataSourceService(session)
        result = await service.toggle_source(workspace_id, source_id, False)

        assert result is not None
        assert result["enabled"] is False

    @pytest.mark.asyncio
    async def test_toggle_nonexistent_source(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=result_mock)

        service = DataSourceService(session)
        result = await service.toggle_source(workspace_id, uuid.uuid4(), True)

        assert result is None

    @pytest.mark.asyncio
    async def test_toggle_preserves_other_params(self, workspace_id: uuid.UUID) -> None:
        session = AsyncMock()
        session.flush = AsyncMock()

        source_id = uuid.uuid4()
        source = SimpleNamespace(
            id=source_id,
            name=f"{_DATASOURCE_PREFIX}Complex Source",
            query_params={
                "source_type": "tiktok_research",
                "enabled": True,
                "settings": {"region": "US", "max_count": 100},
            },
            created_at=datetime(2026, 2, 19, tzinfo=UTC),
        )
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = source
        session.execute = AsyncMock(return_value=result_mock)

        service = DataSourceService(session)
        result = await service.toggle_source(workspace_id, source_id, False)

        assert result["enabled"] is False
        assert result["settings"]["region"] == "US"
        assert result["source_type"] == "tiktok_research"

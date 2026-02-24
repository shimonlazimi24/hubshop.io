"""Tests for ApiKeyService - create, list, revoke, validate API keys."""

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.db.models.analytics import ApiKey
from backend.modules.analytics.services.api_key_service import ApiKeyService


class TestCreateKey:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_create_key_returns_model_and_raw(
        self, mock_session: AsyncMock
    ) -> None:
        workspace_id = uuid.uuid4()
        user_id = uuid.uuid4()

        service = ApiKeyService(mock_session)
        result = await service.create_key(
            workspace_id, user_id, name="My API Key", scopes=["commerce:read"]
        )

        assert isinstance(result, tuple)
        assert len(result) == 2
        key_model, raw_key = result
        assert isinstance(key_model, ApiKey)
        assert isinstance(raw_key, str)
        assert raw_key.startswith("frodo_")
        assert mock_session.add.called

    @pytest.mark.asyncio
    async def test_create_key_hashes_key(self, mock_session: AsyncMock) -> None:
        workspace_id = uuid.uuid4()
        user_id = uuid.uuid4()

        service = ApiKeyService(mock_session)
        key_model, raw_key = await service.create_key(
            workspace_id, user_id, name="Hashed Key"
        )

        added = mock_session.add.call_args_list[0][0][0]
        # key_hash should be set and should NOT be the raw key
        assert added.key_hash is not None
        assert added.key_hash != raw_key
        # Verify hash matches expected
        expected_hash = ApiKey.hash_key(raw_key)
        assert added.key_hash == expected_hash


class TestListKeys:
    @pytest.mark.asyncio
    async def test_list_keys(self) -> None:
        session = AsyncMock()
        key1 = SimpleNamespace(id=uuid.uuid4(), name="Key 1", is_active=True)
        key2 = SimpleNamespace(id=uuid.uuid4(), name="Key 2", is_active=False)
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [key1, key2]
        session.execute.return_value = result_mock

        service = ApiKeyService(session)
        keys = await service.list_keys(uuid.uuid4())

        assert len(keys) == 2
        assert keys[0].name == "Key 1"
        assert keys[1].name == "Key 2"


class TestRevokeKey:
    @pytest.mark.asyncio
    async def test_revoke_key_found(self) -> None:
        session = AsyncMock()
        key = SimpleNamespace(id=uuid.uuid4(), is_active=True)
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = key
        session.execute.return_value = result_mock

        workspace_id = uuid.uuid4()
        service = ApiKeyService(session)
        revoked = await service.revoke_key(key.id, workspace_id)

        assert revoked is not None
        assert revoked.is_active is False

    @pytest.mark.asyncio
    async def test_revoke_key_not_found(self) -> None:
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock

        service = ApiKeyService(session)
        revoked = await service.revoke_key(uuid.uuid4(), uuid.uuid4())

        assert revoked is None


class TestValidateKey:
    @pytest.mark.asyncio
    async def test_validate_key_valid(self) -> None:
        # Generate a real key to get consistent hash
        full_key, prefix, key_hash = ApiKey.generate_key()

        key = SimpleNamespace(
            id=uuid.uuid4(),
            key_hash=key_hash,
            is_active=True,
            expires_at=None,
            last_used_at=None,
        )

        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = key
        session.execute.return_value = result_mock

        service = ApiKeyService(session)
        validated = await service.validate_key(full_key)

        assert validated is not None
        assert validated.last_used_at is not None

    @pytest.mark.asyncio
    async def test_validate_key_invalid_hash(self) -> None:
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock

        service = ApiKeyService(session)
        validated = await service.validate_key("frodo_invalid_key_12345")

        assert validated is None

    @pytest.mark.asyncio
    async def test_validate_key_expired(self) -> None:
        full_key, prefix, key_hash = ApiKey.generate_key()

        key = SimpleNamespace(
            id=uuid.uuid4(),
            key_hash=key_hash,
            is_active=True,
            expires_at=datetime(2025, 1, 1, tzinfo=UTC),
            last_used_at=None,
        )

        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = key
        session.execute.return_value = result_mock

        service = ApiKeyService(session)
        validated = await service.validate_key(full_key)

        assert validated is None

    @pytest.mark.asyncio
    async def test_validate_key_inactive(self) -> None:
        """Inactive keys should not be found by the query (filtered by is_active=True)."""
        session = AsyncMock()
        result_mock = MagicMock()
        # The query itself filters by is_active=True, so inactive keys return None
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock

        service = ApiKeyService(session)
        validated = await service.validate_key("frodo_some_inactive_key")

        assert validated is None

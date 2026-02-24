"""Tests for AdAccountService - list, get, gateway building, advertiser ID extraction."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.db.models.advertising import AdAccount
from backend.modules.advertising.services.ad_account_service import AdAccountService


class TestListAdAccounts:
    @pytest.mark.asyncio
    async def test_returns_list(self) -> None:
        acct1 = SimpleNamespace(id=uuid.uuid4(), advertiser_id="111")
        acct2 = SimpleNamespace(id=uuid.uuid4(), advertiser_id="222")

        session = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = [acct1, acct2]
        session.execute.return_value = result

        service = AdAccountService(session)
        accounts = await service.list_ad_accounts(uuid.uuid4())
        assert len(accounts) == 2

    @pytest.mark.asyncio
    async def test_returns_empty(self) -> None:
        session = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        session.execute.return_value = result

        service = AdAccountService(session)
        accounts = await service.list_ad_accounts(uuid.uuid4())
        assert accounts == []


class TestGetAdAccount:
    @pytest.mark.asyncio
    async def test_returns_account(self) -> None:
        acct = SimpleNamespace(id=uuid.uuid4(), advertiser_id="111")
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = acct
        session.execute.return_value = result

        service = AdAccountService(session)
        found = await service.get_ad_account(acct.id)
        assert found is not None
        assert found.advertiser_id == "111"

    @pytest.mark.asyncio
    async def test_returns_none_for_missing(self) -> None:
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result

        service = AdAccountService(session)
        found = await service.get_ad_account(uuid.uuid4())
        assert found is None


class TestGetAdAccountByAdvertiserId:
    @pytest.mark.asyncio
    async def test_returns_account(self) -> None:
        acct = SimpleNamespace(id=uuid.uuid4(), advertiser_id="111222333")
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = acct
        session.execute.return_value = result

        service = AdAccountService(session)
        found = await service.get_ad_account_by_advertiser_id("111222333")
        assert found is not None

    @pytest.mark.asyncio
    async def test_returns_none_for_missing(self) -> None:
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result

        service = AdAccountService(session)
        found = await service.get_ad_account_by_advertiser_id("nonexistent")
        assert found is None


class TestExtractAdvertiserIds:
    def test_extracts_from_metadata(self) -> None:
        account = SimpleNamespace(
            metadata_json={"advertiser_ids": ["111", "222", "333"]},
            platform_account_id="111",
        )
        service = AdAccountService(AsyncMock())
        ids = service._extract_advertiser_ids(account)
        assert ids == ["111", "222", "333"]

    def test_handles_none_metadata(self) -> None:
        account = SimpleNamespace(metadata_json=None, platform_account_id="111")
        service = AdAccountService(AsyncMock())
        ids = service._extract_advertiser_ids(account)
        assert ids == []

    def test_handles_empty_metadata(self) -> None:
        account = SimpleNamespace(metadata_json={}, platform_account_id="111")
        service = AdAccountService(AsyncMock())
        ids = service._extract_advertiser_ids(account)
        assert ids == []

    def test_handles_non_list_advertiser_ids(self) -> None:
        account = SimpleNamespace(
            metadata_json={"advertiser_ids": "not_a_list"},
            platform_account_id="111",
        )
        service = AdAccountService(AsyncMock())
        ids = service._extract_advertiser_ids(account)
        assert ids == []

    def test_converts_int_ids_to_strings(self) -> None:
        account = SimpleNamespace(
            metadata_json={"advertiser_ids": [111, 222]},
            platform_account_id="111",
        )
        service = AdAccountService(AsyncMock())
        ids = service._extract_advertiser_ids(account)
        assert ids == ["111", "222"]


class TestBuildGateway:
    @pytest.mark.asyncio
    @patch("backend.modules.advertising.services.ad_account_service.decrypt_token")
    @patch(
        "backend.modules.advertising.services.ad_account_service.TikTokMarketingClient"
    )
    @patch("backend.modules.advertising.services.ad_account_service.PlatformGateway")
    async def test_builds_gateway(
        self,
        mock_gateway_cls: MagicMock,
        mock_client_cls: MagicMock,
        mock_decrypt: MagicMock,
    ) -> None:
        mock_decrypt.return_value = "decrypted-token"
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        vault = SimpleNamespace(
            encrypted_access_token="encrypted-xxx",
            connected_account_id=uuid.uuid4(),
        )
        account = SimpleNamespace(id=vault.connected_account_id)

        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = vault
        session.execute.return_value = result

        service = AdAccountService(session)
        await service.build_gateway(account)

        mock_decrypt.assert_called_once_with("encrypted-xxx")
        mock_client_cls.assert_called_once_with(access_token="decrypted-token")
        mock_gateway_cls.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_for_missing_vault(self) -> None:
        account = SimpleNamespace(id=uuid.uuid4())
        session = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result

        service = AdAccountService(session)
        with pytest.raises(ValueError, match="No token vault"):
            await service.build_gateway(account)


class TestUpsertAdAccount:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = MagicMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute.return_value = result
        session.flush = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_creates_new_ad_account(self, mock_session: AsyncMock) -> None:
        service = AdAccountService(mock_session)
        ad_account = await service._upsert_ad_account(
            workspace_id=uuid.uuid4(),
            connected_account_id=uuid.uuid4(),
            adv_data={
                "advertiser_id": "999888777",
                "advertiser_name": "New Advertiser",
                "currency": "EUR",
                "timezone": "Europe/London",
            },
        )

        assert mock_session.add.called
        added = mock_session.add.call_args_list[0][0][0]
        assert isinstance(added, AdAccount)
        assert added.advertiser_id == "999888777"
        assert added.currency == "EUR"

    @pytest.mark.asyncio
    async def test_updates_existing_ad_account(self, mock_session: AsyncMock) -> None:
        existing = SimpleNamespace(
            id=uuid.uuid4(),
            advertiser_id="999888777",
            advertiser_name="Old Name",
            currency="USD",
            timezone="UTC",
        )
        result = MagicMock()
        result.scalar_one_or_none.return_value = existing
        mock_session.execute.return_value = result

        service = AdAccountService(mock_session)
        await service._upsert_ad_account(
            workspace_id=uuid.uuid4(),
            connected_account_id=uuid.uuid4(),
            adv_data={
                "advertiser_id": "999888777",
                "advertiser_name": "Updated Name",
                "currency": "EUR",
                "timezone": "Europe/London",
            },
        )

        assert existing.advertiser_name == "Updated Name"
        assert existing.currency == "EUR"
        assert not mock_session.add.called

"""Tests for PixelService extended methods — track_event, batch_track_events, PII hashing."""

import hashlib
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.advertising.services.pixel_service import PixelService


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def sample_ad_account() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        advertiser_id="111222333",
        connected_account_id=uuid.uuid4(),
    )


@pytest.fixture
def sample_pixel(sample_ad_account: SimpleNamespace) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        workspace_id=sample_ad_account.workspace_id,
        ad_account_id=sample_ad_account.id,
        platform_pixel_id="pixel_platform_123",
        name="Test Pixel",
        pixel_code="<script>...</script>",
    )


class TestHashPii:
    def test_hash_pii_normalizes_and_hashes(self) -> None:
        result = PixelService._hash_pii("  TEST@Example.COM  ")
        expected = hashlib.sha256(b"test@example.com").hexdigest()
        assert result == expected

    def test_hash_pii_already_lowercase(self) -> None:
        result = PixelService._hash_pii("user@test.com")
        expected = hashlib.sha256(b"user@test.com").hexdigest()
        assert result == expected


class TestHashUserData:
    def test_hashes_email_and_phone(self) -> None:
        user_data = {
            "email": "user@test.com",
            "phone": "+1234567890",
            "name": "John",
        }
        result = PixelService._hash_user_data(user_data)

        assert result["email"] == hashlib.sha256(b"user@test.com").hexdigest()
        assert result["phone"] == hashlib.sha256(b"+1234567890").hexdigest()
        # Non-PII fields should be untouched
        assert result["name"] == "John"

    def test_hashes_phone_number_field(self) -> None:
        user_data = {"phone_number": "+9876543210"}
        result = PixelService._hash_user_data(user_data)
        assert result["phone_number"] == hashlib.sha256(b"+9876543210").hexdigest()

    def test_skips_empty_pii(self) -> None:
        user_data = {"email": "", "phone": None, "name": "Jane"}
        result = PixelService._hash_user_data(user_data)
        assert result["email"] == ""
        assert result["phone"] is None
        assert result["name"] == "Jane"

    def test_does_not_mutate_original(self) -> None:
        user_data = {"email": "test@example.com"}
        PixelService._hash_user_data(user_data)
        assert user_data["email"] == "test@example.com"


class TestTrackEvent:
    @pytest.mark.asyncio
    async def test_track_event_calls_api(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        sample_pixel: SimpleNamespace,
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {"data": {"events_received": 1}}

        with (
            patch.object(PixelService, "get_pixel", return_value=sample_pixel),
            patch(
                "backend.modules.advertising.services.pixel_service.AdAccountService"
            ) as mock_acct_cls,
        ):
            mock_acct = AsyncMock()
            mock_acct.get_ad_account.return_value = sample_ad_account
            mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
            mock_acct_cls.return_value = mock_acct

            service = PixelService(mock_session)
            result = await service.track_event(
                sample_ad_account.workspace_id,
                sample_pixel.id,
                event_type="Purchase",
                event_data={"value": "29.99", "currency": "USD"},
            )

        assert result == {"events_received": 1}
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["pixel_code"] == sample_pixel.platform_pixel_id
        assert len(call_body["data"]) == 1
        assert call_body["data"][0]["event"] == "Purchase"

    @pytest.mark.asyncio
    async def test_track_event_with_user_data_hashes_pii(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        sample_pixel: SimpleNamespace,
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {"data": {}}

        with (
            patch.object(PixelService, "get_pixel", return_value=sample_pixel),
            patch(
                "backend.modules.advertising.services.pixel_service.AdAccountService"
            ) as mock_acct_cls,
        ):
            mock_acct = AsyncMock()
            mock_acct.get_ad_account.return_value = sample_ad_account
            mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
            mock_acct_cls.return_value = mock_acct

            service = PixelService(mock_session)
            await service.track_event(
                sample_ad_account.workspace_id,
                sample_pixel.id,
                event_type="AddToCart",
                event_data={"value": "10.00"},
                user_data={"email": "test@example.com", "name": "Test"},
            )

        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        event = call_body["data"][0]
        assert "context" in event
        hashed_email = hashlib.sha256(b"test@example.com").hexdigest()
        assert event["context"]["user"]["email"] == hashed_email
        assert event["context"]["user"]["name"] == "Test"

    @pytest.mark.asyncio
    async def test_track_event_pixel_not_found(
        self,
        mock_session: AsyncMock,
    ) -> None:
        with patch.object(PixelService, "get_pixel", return_value=None):
            service = PixelService(mock_session)
            with pytest.raises(ValueError, match="not found"):
                await service.track_event(
                    uuid.uuid4(),
                    uuid.uuid4(),
                    event_type="ViewContent",
                    event_data={},
                )


class TestBatchTrackEvents:
    @pytest.mark.asyncio
    async def test_batch_track_events_sends_multiple(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        sample_pixel: SimpleNamespace,
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {"data": {"events_received": 2}}

        with (
            patch.object(PixelService, "get_pixel", return_value=sample_pixel),
            patch(
                "backend.modules.advertising.services.pixel_service.AdAccountService"
            ) as mock_acct_cls,
        ):
            mock_acct = AsyncMock()
            mock_acct.get_ad_account.return_value = sample_ad_account
            mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
            mock_acct_cls.return_value = mock_acct

            service = PixelService(mock_session)
            events = [
                {
                    "event_type": "Purchase",
                    "event_data": {"value": "29.99"},
                },
                {
                    "event_type": "AddToCart",
                    "event_data": {"value": "15.00"},
                    "user_data": {"email": "buyer@test.com"},
                },
            ]
            result = await service.batch_track_events(
                sample_ad_account.workspace_id,
                sample_pixel.id,
                events,
            )

        assert result == {"events_received": 2}
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert len(call_body["data"]) == 2
        assert call_body["data"][0]["event"] == "Purchase"
        assert call_body["data"][1]["event"] == "AddToCart"
        # Second event should have hashed PII
        hashed = hashlib.sha256(b"buyer@test.com").hexdigest()
        assert call_body["data"][1]["context"]["user"]["email"] == hashed

    @pytest.mark.asyncio
    async def test_batch_track_events_pixel_not_found(
        self,
        mock_session: AsyncMock,
    ) -> None:
        with patch.object(PixelService, "get_pixel", return_value=None):
            service = PixelService(mock_session)
            with pytest.raises(ValueError, match="not found"):
                await service.batch_track_events(uuid.uuid4(), uuid.uuid4(), [])

"""Tests for AudienceService extended methods — share, overlap, upload, rule audiences."""

import hashlib
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.modules.advertising.services.audience_service import AudienceService


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
        advertiser_name="Test Advertiser",
        connected_account_id=uuid.uuid4(),
    )


@pytest.fixture
def sample_audience(sample_ad_account: SimpleNamespace) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        workspace_id=sample_ad_account.workspace_id,
        ad_account_id=sample_ad_account.id,
        platform_audience_id="aud_platform_123",
        name="Test Audience",
        audience_type="CUSTOM",
    )


class TestShareAudience:
    @pytest.mark.asyncio
    async def test_share_audience_calls_api(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        sample_audience: SimpleNamespace,
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {"data": {"shared": True}}

        with (
            patch.object(AudienceService, "get_audience", return_value=sample_audience),
            patch(
                "backend.modules.advertising.services.audience_service.AdAccountService"
            ) as mock_acct_cls,
        ):
            mock_acct = AsyncMock()
            mock_acct.get_ad_account.return_value = sample_ad_account
            mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
            mock_acct_cls.return_value = mock_acct

            service = AudienceService(mock_session)
            result = await service.share_audience(
                sample_ad_account.workspace_id,
                sample_audience.id,
                ["adv_456", "adv_789"],
            )

        assert result == {"shared": True}
        mock_gateway.post.assert_called_once_with(
            "/audience/share/",
            json_body={
                "advertiser_id": sample_ad_account.advertiser_id,
                "custom_audience_ids": [sample_audience.platform_audience_id],
                "target_advertiser_ids": ["adv_456", "adv_789"],
            },
        )

    @pytest.mark.asyncio
    async def test_share_audience_not_found(
        self,
        mock_session: AsyncMock,
    ) -> None:
        with patch.object(AudienceService, "get_audience", return_value=None):
            service = AudienceService(mock_session)
            with pytest.raises(ValueError, match="not found"):
                await service.share_audience(uuid.uuid4(), uuid.uuid4(), ["adv_456"])


class TestGetAudienceOverlap:
    @pytest.mark.asyncio
    async def test_overlap_requires_two_ids(
        self,
        mock_session: AsyncMock,
    ) -> None:
        service = AudienceService(mock_session)
        with pytest.raises(ValueError, match="At least 2"):
            await service.get_audience_overlap(uuid.uuid4(), [uuid.uuid4()])

    @pytest.mark.asyncio
    async def test_overlap_calls_api(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
    ) -> None:
        aud1 = SimpleNamespace(
            id=uuid.uuid4(),
            ad_account_id=sample_ad_account.id,
            platform_audience_id="aud_1",
        )
        aud2 = SimpleNamespace(
            id=uuid.uuid4(),
            ad_account_id=sample_ad_account.id,
            platform_audience_id="aud_2",
        )
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {"data": {"overlap_rate": 0.15}}

        call_count = 0

        async def get_audience_side_effect(aid: uuid.UUID):
            if aid == aud1.id:
                return aud1
            if aid == aud2.id:
                return aud2
            return None

        with (
            patch.object(
                AudienceService, "get_audience", side_effect=get_audience_side_effect
            ),
            patch(
                "backend.modules.advertising.services.audience_service.AdAccountService"
            ) as mock_acct_cls,
        ):
            mock_acct = AsyncMock()
            mock_acct.get_ad_account.return_value = sample_ad_account
            mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
            mock_acct_cls.return_value = mock_acct

            service = AudienceService(mock_session)
            result = await service.get_audience_overlap(
                sample_ad_account.workspace_id, [aud1.id, aud2.id]
            )

        assert result == {"overlap_rate": 0.15}
        mock_gateway.post.assert_called_once()


class TestUploadAudienceFile:
    @pytest.mark.asyncio
    async def test_upload_hashes_pii_data(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        sample_audience: SimpleNamespace,
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {"data": {"upload_id": "up_123"}}

        with (
            patch.object(AudienceService, "get_audience", return_value=sample_audience),
            patch(
                "backend.modules.advertising.services.audience_service.AdAccountService"
            ) as mock_acct_cls,
        ):
            mock_acct = AsyncMock()
            mock_acct.get_ad_account.return_value = sample_ad_account
            mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
            mock_acct_cls.return_value = mock_acct

            service = AudienceService(mock_session)
            result = await service.upload_audience_file(
                sample_ad_account.workspace_id,
                sample_audience.id,
                ["test@example.com", "+1234567890"],
            )

        assert result == {"upload_id": "up_123"}

        # Verify the data was SHA-256 hashed
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        expected_hash_email = hashlib.sha256(b"test@example.com").hexdigest()
        expected_hash_phone = hashlib.sha256(b"+1234567890").hexdigest()
        assert call_body["file_signature"][0] == expected_hash_email
        assert call_body["file_signature"][1] == expected_hash_phone

    @pytest.mark.asyncio
    async def test_upload_normalizes_before_hashing(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        sample_audience: SimpleNamespace,
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {"data": {}}

        with (
            patch.object(AudienceService, "get_audience", return_value=sample_audience),
            patch(
                "backend.modules.advertising.services.audience_service.AdAccountService"
            ) as mock_acct_cls,
        ):
            mock_acct = AsyncMock()
            mock_acct.get_ad_account.return_value = sample_ad_account
            mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
            mock_acct_cls.return_value = mock_acct

            service = AudienceService(mock_session)
            await service.upload_audience_file(
                sample_ad_account.workspace_id,
                sample_audience.id,
                ["  TEST@Example.COM  "],
            )

        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        expected = hashlib.sha256(b"test@example.com").hexdigest()
        assert call_body["file_signature"][0] == expected


class TestCreateRuleAudience:
    @pytest.mark.asyncio
    async def test_creates_rule_audience(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {
            "data": {"custom_audience_id": "aud_rule_456"}
        }

        with patch(
            "backend.modules.advertising.services.audience_service.AdAccountService"
        ) as mock_acct_cls:
            mock_acct = AsyncMock()
            mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
            mock_acct_cls.return_value = mock_acct

            service = AudienceService(mock_session)
            audience = await service.create_rule_audience(
                sample_ad_account.workspace_id,
                sample_ad_account,
                name="Rule Audience",
                rules=[{"type": "url", "value": "example.com"}],
            )

        assert mock_session.add.called
        added = mock_session.add.call_args[0][0]
        assert added.name == "Rule Audience"
        assert added.audience_type == "RULE"
        assert added.platform_audience_id == "aud_rule_456"

    @pytest.mark.asyncio
    async def test_rule_audience_sends_rules_to_api(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
    ) -> None:
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {"data": {"custom_audience_id": "aud_r"}}

        rules = [
            {"type": "url", "value": "shop.example.com"},
            {"type": "event", "value": "add_to_cart"},
        ]

        with patch(
            "backend.modules.advertising.services.audience_service.AdAccountService"
        ) as mock_acct_cls:
            mock_acct = AsyncMock()
            mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
            mock_acct_cls.return_value = mock_acct

            service = AudienceService(mock_session)
            await service.create_rule_audience(
                sample_ad_account.workspace_id,
                sample_ad_account,
                name="Rule Aud",
                rules=rules,
            )

        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["rules"] == rules
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id

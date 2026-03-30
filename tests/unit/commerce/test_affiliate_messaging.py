"""Tests for E4: Affiliate creator messaging."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from backend.modules.commerce.services.affiliate_service import AffiliateService


class TestGetCreatorConversations:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_shop(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
        )

    @pytest.mark.asyncio
    async def test_get_conversations(
        self, mock_session: AsyncMock, mock_shop: SimpleNamespace
    ) -> None:
        """Should call gateway to list creator conversations."""
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {
            "data": {
                "conversations": [
                    {
                        "conversation_id": "conv_1",
                        "creator_id": "cr_1",
                        "last_message": "Hello",
                    }
                ]
            }
        }

        with pytest.MonkeyPatch.context() as mp:
            from backend.modules.commerce.services import shop_service as ss_mod

            async def mock_build(self_ss, shop):  # type: ignore[no-untyped-def]
                return mock_gateway

            mp.setattr(ss_mod.ShopService, "build_gateway_for_shop", mock_build)

            service = AffiliateService(mock_session)
            result = await service.get_creator_conversations(mock_shop, page_size=20)

        mock_gateway.get.assert_awaited_once()
        call_args = mock_gateway.get.call_args
        assert "/affiliate/202309/seller/conversations" in call_args[0][0]
        assert "conversations" in result

    @pytest.mark.asyncio
    async def test_get_conversations_empty(
        self, mock_session: AsyncMock, mock_shop: SimpleNamespace
    ) -> None:
        """Should return empty dict when no data."""
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {}

        with pytest.MonkeyPatch.context() as mp:
            from backend.modules.commerce.services import shop_service as ss_mod

            async def mock_build(self_ss, shop):  # type: ignore[no-untyped-def]
                return mock_gateway

            mp.setattr(ss_mod.ShopService, "build_gateway_for_shop", mock_build)

            service = AffiliateService(mock_session)
            result = await service.get_creator_conversations(mock_shop)

        assert result == {}

    @pytest.mark.asyncio
    async def test_get_conversations_custom_page_size(
        self, mock_session: AsyncMock, mock_shop: SimpleNamespace
    ) -> None:
        """Should pass custom page_size to gateway."""
        mock_gateway = AsyncMock()
        mock_gateway.get.return_value = {"data": {"conversations": []}}

        with pytest.MonkeyPatch.context() as mp:
            from backend.modules.commerce.services import shop_service as ss_mod

            async def mock_build(self_ss, shop):  # type: ignore[no-untyped-def]
                return mock_gateway

            mp.setattr(ss_mod.ShopService, "build_gateway_for_shop", mock_build)

            service = AffiliateService(mock_session)
            await service.get_creator_conversations(mock_shop, page_size=50)

        params = mock_gateway.get.call_args[1].get("params", {})
        assert params.get("page_size") == "50"


class TestSendCreatorMessage:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_shop(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
        )

    @pytest.mark.asyncio
    async def test_send_message(
        self, mock_session: AsyncMock, mock_shop: SimpleNamespace
    ) -> None:
        """Should call gateway to send message to a conversation."""
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {
            "data": {"message_id": "msg_001", "status": "sent"}
        }

        with pytest.MonkeyPatch.context() as mp:
            from backend.modules.commerce.services import shop_service as ss_mod

            async def mock_build(self_ss, shop):  # type: ignore[no-untyped-def]
                return mock_gateway

            mp.setattr(ss_mod.ShopService, "build_gateway_for_shop", mock_build)

            service = AffiliateService(mock_session)
            result = await service.send_creator_message(
                mock_shop, "conv_1", content="Hi, interested in collab!"
            )

        mock_gateway.post.assert_awaited_once()
        call_args = mock_gateway.post.call_args
        assert (
            "/affiliate/202309/seller/conversations/conv_1/messages" in call_args[0][0]
        )
        body = call_args[1].get("json_body", {})
        assert body.get("content") == "Hi, interested in collab!"
        assert result["message_id"] == "msg_001"

    @pytest.mark.asyncio
    async def test_send_message_empty_response(
        self, mock_session: AsyncMock, mock_shop: SimpleNamespace
    ) -> None:
        """Should return empty dict when no data."""
        mock_gateway = AsyncMock()
        mock_gateway.post.return_value = {}

        with pytest.MonkeyPatch.context() as mp:
            from backend.modules.commerce.services import shop_service as ss_mod

            async def mock_build(self_ss, shop):  # type: ignore[no-untyped-def]
                return mock_gateway

            mp.setattr(ss_mod.ShopService, "build_gateway_for_shop", mock_build)

            service = AffiliateService(mock_session)
            result = await service.send_creator_message(
                mock_shop, "conv_1", content="Test"
            )

        assert result == {}

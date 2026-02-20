"""Tests for MessagingService — conversations, messages, capability, comment-to-message, auto-messages."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.messaging.services.messaging_service import MessagingService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def connected_account_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def patched_build_gateway(mock_gateway: AsyncMock):
    with patch.object(
        MessagingService, "_build_gateway", return_value=mock_gateway
    ) as mock_build:
        yield mock_build


# ------------------------------------------------------------------ #
#  Conversations
# ------------------------------------------------------------------ #


class TestListConversations:
    @pytest.mark.asyncio
    async def test_list_conversations(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        connected_account_id: uuid.UUID,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"conversation_id": "c1", "participant": "user_123"},
                    {"conversation_id": "c2", "participant": "user_456"},
                ]
            }
        }

        service = MessagingService(mock_session)
        result = await service.list_conversations(connected_account_id)

        assert len(result["list"]) == 2
        mock_gateway.get.assert_called_once()
        call_args = mock_gateway.get.call_args
        assert call_args.args[0] == "/business_messaging/conversation/list/"
        assert call_args.kwargs["params"]["page"] == "1"
        assert call_args.kwargs["params"]["page_size"] == "20"

    @pytest.mark.asyncio
    async def test_list_conversations_with_pagination(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        connected_account_id: uuid.UUID,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"list": []}}

        service = MessagingService(mock_session)
        await service.list_conversations(
            connected_account_id, page=3, page_size=10
        )

        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["page"] == "3"
        assert call_params["page_size"] == "10"


class TestListMessages:
    @pytest.mark.asyncio
    async def test_list_messages(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        connected_account_id: uuid.UUID,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"message_id": "m1", "content": "Hello"},
                    {"message_id": "m2", "content": "World"},
                ]
            }
        }

        service = MessagingService(mock_session)
        result = await service.list_messages(
            connected_account_id, "conv_001"
        )

        assert len(result["list"]) == 2
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["conversation_id"] == "conv_001"

    @pytest.mark.asyncio
    async def test_list_messages_with_pagination(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        connected_account_id: uuid.UUID,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"list": []}}

        service = MessagingService(mock_session)
        await service.list_messages(
            connected_account_id, "conv_001", page=2, page_size=5
        )

        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["page"] == "2"
        assert call_params["page_size"] == "5"


class TestSendMessage:
    @pytest.mark.asyncio
    async def test_send_message_text_only(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        connected_account_id: uuid.UUID,
        patched_build_gateway,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"message_id": "m_new"}
        }

        service = MessagingService(mock_session)
        result = await service.send_message(
            connected_account_id, "conv_001", "Hello there!"
        )

        assert result["message_id"] == "m_new"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["conversation_id"] == "conv_001"
        assert call_body["content"] == "Hello there!"
        assert "media_url" not in call_body

    @pytest.mark.asyncio
    async def test_send_message_with_media(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        connected_account_id: uuid.UUID,
        patched_build_gateway,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"message_id": "m_media"}
        }

        service = MessagingService(mock_session)
        result = await service.send_message(
            connected_account_id,
            "conv_001",
            "Check this out",
            media_url="https://example.com/image.png",
        )

        assert result["message_id"] == "m_media"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["media_url"] == "https://example.com/image.png"


# ------------------------------------------------------------------ #
#  Capability & Comment-to-Message
# ------------------------------------------------------------------ #


class TestCheckCapability:
    @pytest.mark.asyncio
    async def test_check_capability(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        connected_account_id: uuid.UUID,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"is_capable": True, "reasons": []}
        }

        service = MessagingService(mock_session)
        result = await service.check_capability(connected_account_id)

        assert result["is_capable"] is True
        mock_gateway.get.assert_called_once_with(
            "/business_messaging/capability/check/",
        )


class TestToggleCommentToMessage:
    @pytest.mark.asyncio
    async def test_toggle_enable(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        connected_account_id: uuid.UUID,
        patched_build_gateway,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"enabled": True}
        }

        service = MessagingService(mock_session)
        result = await service.toggle_comment_to_message(
            connected_account_id, enabled=True
        )

        assert result["enabled"] is True
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["enabled"] is True

    @pytest.mark.asyncio
    async def test_toggle_disable(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        connected_account_id: uuid.UUID,
        patched_build_gateway,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"enabled": False}
        }

        service = MessagingService(mock_session)
        result = await service.toggle_comment_to_message(
            connected_account_id, enabled=False
        )

        assert result["enabled"] is False
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["enabled"] is False


class TestGetCommentToMessageSetting:
    @pytest.mark.asyncio
    async def test_get_setting(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        connected_account_id: uuid.UUID,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"enabled": True, "updated_at": "2026-01-15T10:00:00Z"}
        }

        service = MessagingService(mock_session)
        result = await service.get_comment_to_message_setting(
            connected_account_id
        )

        assert result["enabled"] is True
        mock_gateway.get.assert_called_once_with(
            "/business_messaging/comment_to_message/setting/",
        )


# ------------------------------------------------------------------ #
#  Auto-Messages
# ------------------------------------------------------------------ #


class TestCreateAutoMessage:
    @pytest.mark.asyncio
    async def test_create_auto_message(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        connected_account_id: uuid.UUID,
        patched_build_gateway,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"auto_message_id": "am_new", "message_type": "WELCOME"}
        }

        service = MessagingService(mock_session)
        result = await service.create_auto_message(
            connected_account_id,
            message_type="WELCOME",
            content="Welcome to our store!",
        )

        assert result["auto_message_id"] == "am_new"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["message_type"] == "WELCOME"
        assert call_body["content"] == "Welcome to our store!"


class TestListAutoMessages:
    @pytest.mark.asyncio
    async def test_list_auto_messages(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        connected_account_id: uuid.UUID,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"auto_message_id": "am1", "message_type": "WELCOME"},
                    {"auto_message_id": "am2", "message_type": "CHAT_PROMPT"},
                ]
            }
        }

        service = MessagingService(mock_session)
        result = await service.list_auto_messages(connected_account_id)

        assert len(result["list"]) == 2
        mock_gateway.get.assert_called_once_with(
            "/business_messaging/auto_message/list/",
        )


class TestUpdateAutoMessage:
    @pytest.mark.asyncio
    async def test_update_auto_message(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        connected_account_id: uuid.UUID,
        patched_build_gateway,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"auto_message_id": "am1"}
        }

        service = MessagingService(mock_session)
        result = await service.update_auto_message(
            connected_account_id,
            auto_message_id="am1",
            content="Updated welcome message!",
        )

        assert result["auto_message_id"] == "am1"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["auto_message_id"] == "am1"
        assert call_body["content"] == "Updated welcome message!"


class TestToggleAutoMessage:
    @pytest.mark.asyncio
    async def test_toggle_auto_message_enable(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        connected_account_id: uuid.UUID,
        patched_build_gateway,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"auto_message_id": "am1", "enabled": True}
        }

        service = MessagingService(mock_session)
        result = await service.toggle_auto_message(
            connected_account_id, auto_message_id="am1", enabled=True
        )

        assert result["enabled"] is True
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["auto_message_id"] == "am1"
        assert call_body["enabled"] is True

    @pytest.mark.asyncio
    async def test_toggle_auto_message_disable(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        connected_account_id: uuid.UUID,
        patched_build_gateway,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"auto_message_id": "am1", "enabled": False}
        }

        service = MessagingService(mock_session)
        result = await service.toggle_auto_message(
            connected_account_id, auto_message_id="am1", enabled=False
        )

        assert result["enabled"] is False
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["enabled"] is False


class TestDeleteAutoMessage:
    @pytest.mark.asyncio
    async def test_delete_auto_message(
        self,
        mock_session: AsyncMock,
        mock_gateway: AsyncMock,
        connected_account_id: uuid.UUID,
        patched_build_gateway,
    ) -> None:
        mock_gateway.request.return_value = {"data": {}}

        service = MessagingService(mock_session)
        result = await service.delete_auto_message(
            connected_account_id, auto_message_id="am1"
        )

        assert result == {}
        mock_gateway.request.assert_called_once()
        call_args = mock_gateway.request.call_args
        assert call_args.args[0] == "DELETE"
        assert call_args.args[1] == "/business_messaging/auto_message/delete/"
        assert call_args.kwargs["json_body"]["auto_message_id"] == "am1"

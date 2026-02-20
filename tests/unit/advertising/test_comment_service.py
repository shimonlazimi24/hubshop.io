"""Tests for CommentService — list, reply, hide, delete ad comments."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.advertising.services.comment_service import CommentService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def sample_ad_account() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        advertiser_id="111222333",
        connected_account_id=uuid.uuid4(),
    )


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def patched_account_service(
    sample_ad_account: SimpleNamespace, mock_gateway: AsyncMock
):
    with patch(
        "backend.modules.advertising.services.comment_service.AdAccountService"
    ) as mock_cls:
        mock_acct = AsyncMock()
        mock_acct.build_gateway_for_ad_account.return_value = mock_gateway
        mock_cls.return_value = mock_acct
        yield mock_cls


class TestListComments:
    @pytest.mark.asyncio
    async def test_list_comments(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "list": [
                    {"comment_id": "c1", "text": "Great ad!"},
                    {"comment_id": "c2", "text": "Love this product"},
                ]
            }
        }

        service = CommentService(mock_session)
        result = await service.list_comments(
            sample_ad_account.workspace_id,
            sample_ad_account,
            ad_id="ad_123",
        )

        assert len(result["list"]) == 2
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["ad_id"] == "ad_123"
        assert call_params["advertiser_id"] == sample_ad_account.advertiser_id

    @pytest.mark.asyncio
    async def test_list_comments_with_pagination(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.get.return_value = {"data": {"list": []}}

        service = CommentService(mock_session)
        await service.list_comments(
            sample_ad_account.workspace_id,
            sample_ad_account,
            ad_id="ad_123",
            page=2,
            page_size=50,
        )

        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["page"] == "2"
        assert call_params["page_size"] == "50"


class TestReplyToComment:
    @pytest.mark.asyncio
    async def test_reply_to_comment(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"reply_id": "reply_1", "status": "success"}
        }

        service = CommentService(mock_session)
        result = await service.reply_to_comment(
            sample_ad_account.workspace_id,
            sample_ad_account,
            comment_id="c1",
            text="Thanks for your feedback!",
        )

        assert result["reply_id"] == "reply_1"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["comment_id"] == "c1"
        assert call_body["text"] == "Thanks for your feedback!"
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id


class TestHideComment:
    @pytest.mark.asyncio
    async def test_hide_comment(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {"data": {"hidden": True}}

        service = CommentService(mock_session)
        result = await service.hide_comment(
            sample_ad_account.workspace_id,
            sample_ad_account,
            comment_id="c1",
        )

        assert result == {"hidden": True}
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["comment_id"] == "c1"
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id


class TestDeleteComment:
    @pytest.mark.asyncio
    async def test_delete_comment(
        self,
        mock_session: AsyncMock,
        sample_ad_account: SimpleNamespace,
        mock_gateway: AsyncMock,
        patched_account_service,
    ) -> None:
        mock_gateway.post.return_value = {"data": {}}

        service = CommentService(mock_session)
        result = await service.delete_comment(
            sample_ad_account.workspace_id,
            sample_ad_account,
            comment_id="c1",
        )

        assert result == {}
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["comment_id"] == "c1"
        assert call_body["advertiser_id"] == sample_ad_account.advertiser_id

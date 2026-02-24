"""Tests for MentionsService — top mentions, keywords, hashtags, replies."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from backend.modules.organic.services.mentions_service import MentionsService


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def workspace_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def connected_account_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def mock_gateway() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def patched_build_gateway(mock_gateway: AsyncMock):
    with patch.object(
        MentionsService,
        "_build_gateway",
        return_value=mock_gateway,
    ) as mock_build:
        yield mock_build


class TestGetTopMentions:
    @pytest.mark.asyncio
    async def test_get_top_mentions(
        self,
        mock_session: AsyncMock,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        mock_gateway: AsyncMock,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "posts": [
                    {"post_id": "p1", "engagement": 5000},
                    {"post_id": "p2", "engagement": 3000},
                ]
            }
        }

        service = MentionsService(mock_session)
        result = await service.get_top_mentions(workspace_id, connected_account_id)

        assert len(result["posts"]) == 2
        mock_gateway.get.assert_called_once_with("/mentions/posts/top/")
        patched_build_gateway.assert_called_once_with(connected_account_id)


class TestGetMentionDetail:
    @pytest.mark.asyncio
    async def test_get_mention_detail(
        self,
        mock_session: AsyncMock,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        mock_gateway: AsyncMock,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "post_id": "p1",
                "author": "creator123",
                "content": "Love this brand!",
            }
        }

        service = MentionsService(mock_session)
        result = await service.get_mention_detail(
            workspace_id, connected_account_id, post_id="p1"
        )

        assert result["post_id"] == "p1"
        assert result["author"] == "creator123"
        call_params = mock_gateway.get.call_args.kwargs["params"]
        assert call_params["post_id"] == "p1"


class TestGetFrequentKeywords:
    @pytest.mark.asyncio
    async def test_get_frequent_keywords(
        self,
        mock_session: AsyncMock,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        mock_gateway: AsyncMock,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "keywords": [
                    {"keyword": "quality", "count": 150},
                    {"keyword": "affordable", "count": 100},
                ]
            }
        }

        service = MentionsService(mock_session)
        result = await service.get_frequent_keywords(workspace_id, connected_account_id)

        assert len(result["keywords"]) == 2
        assert result["keywords"][0]["keyword"] == "quality"
        mock_gateway.get.assert_called_once_with("/mentions/keywords/frequent/")


class TestGetFrequentHashtags:
    @pytest.mark.asyncio
    async def test_get_frequent_hashtags(
        self,
        mock_session: AsyncMock,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        mock_gateway: AsyncMock,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "hashtags": [
                    {"hashtag": "#mybrand", "count": 500},
                    {"hashtag": "#brandname", "count": 300},
                ]
            }
        }

        service = MentionsService(mock_session)
        result = await service.get_frequent_hashtags(workspace_id, connected_account_id)

        assert len(result["hashtags"]) == 2
        assert result["hashtags"][0]["hashtag"] == "#mybrand"
        mock_gateway.get.assert_called_once_with("/mentions/hashtags/frequent/")


class TestGetTopCommentMentions:
    @pytest.mark.asyncio
    async def test_get_top_comment_mentions(
        self,
        mock_session: AsyncMock,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        mock_gateway: AsyncMock,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {
                "comments": [
                    {"comment_id": "c1", "text": "Great product!", "likes": 200},
                ]
            }
        }

        service = MentionsService(mock_session)
        result = await service.get_top_comment_mentions(
            workspace_id, connected_account_id
        )

        assert len(result["comments"]) == 1
        assert result["comments"][0]["text"] == "Great product!"
        mock_gateway.get.assert_called_once_with("/mentions/comments/top/")


class TestReplyToMention:
    @pytest.mark.asyncio
    async def test_reply_to_mention(
        self,
        mock_session: AsyncMock,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        mock_gateway: AsyncMock,
        patched_build_gateway,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"comment_id": "c_reply_1", "status": "POSTED"}
        }

        service = MentionsService(mock_session)
        result = await service.reply_to_mention(
            workspace_id,
            connected_account_id,
            comment_id="c1",
            text="Thank you for your feedback!",
        )

        assert result["status"] == "POSTED"
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["comment_id"] == "c1"
        assert call_body["text"] == "Thank you for your feedback!"


class TestEnableBrandHashtag:
    @pytest.mark.asyncio
    async def test_enable_brand_hashtag(
        self,
        mock_session: AsyncMock,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        mock_gateway: AsyncMock,
        patched_build_gateway,
    ) -> None:
        mock_gateway.post.return_value = {
            "data": {"hashtag": "#mybrand", "enabled": True}
        }

        service = MentionsService(mock_session)
        result = await service.enable_brand_hashtag(
            workspace_id, connected_account_id, hashtag="#mybrand"
        )

        assert result["enabled"] is True
        call_body = mock_gateway.post.call_args.kwargs["json_body"]
        assert call_body["hashtag"] == "#mybrand"


class TestListEnabledHashtags:
    @pytest.mark.asyncio
    async def test_list_enabled_hashtags(
        self,
        mock_session: AsyncMock,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        mock_gateway: AsyncMock,
        patched_build_gateway,
    ) -> None:
        mock_gateway.get.return_value = {
            "data": {"hashtags": ["#mybrand", "#brandname", "#brandlife"]}
        }

        service = MentionsService(mock_session)
        result = await service.list_enabled_hashtags(workspace_id, connected_account_id)

        assert len(result["hashtags"]) == 3
        assert "#mybrand" in result["hashtags"]
        mock_gateway.get.assert_called_once_with("/mentions/brand_hashtag/enabled/")

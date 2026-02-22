"""Tests for CommentService - list, sync, reply, delete, upsert."""

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.db.models.content import Comment
from backend.modules.content.services.comment_service import CommentService


class TestListComments:
    @pytest.mark.asyncio
    async def test_list_comments_returns_paginated(self) -> None:
        session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        c1 = SimpleNamespace(
            id=uuid.uuid4(),
            text="Great video!",
            like_count=5,
        )
        c2 = SimpleNamespace(
            id=uuid.uuid4(),
            text="Love this",
            like_count=3,
        )
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = [c1, c2]

        session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = CommentService(session)
        result = await service.list_comments(
            uuid.uuid4(), uuid.uuid4(), page=1, page_size=20
        )

        assert result.total == 2
        assert len(result.items) == 2
        assert result.page == 1
        assert result.page_size == 20

    @pytest.mark.asyncio
    async def test_list_comments_empty(self) -> None:
        session = AsyncMock()
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []

        session.execute = AsyncMock(side_effect=[count_result, items_result])

        service = CommentService(session)
        result = await service.list_comments(uuid.uuid4(), uuid.uuid4())

        assert result.total == 0
        assert result.items == []
        assert result.total_pages == 0


class TestSyncComments:
    @pytest.mark.asyncio
    async def test_sync_comments_calls_api(self) -> None:
        session = AsyncMock()
        mock_gateway = AsyncMock()
        mock_account = SimpleNamespace(id=uuid.uuid4())

        mock_gateway.post.return_value = {
            "data": {
                "comments": [
                    {
                        "id": "cmt_1",
                        "text": "Nice!",
                        "create_time": 1700000000,
                        "like_count": 2,
                        "reply_count": 0,
                        "parent_comment_id": None,
                        "username": "user1",
                        "profile_image": "https://img.example.com/1.jpg",
                    }
                ],
                "has_more": False,
            }
        }

        # Mock _upsert_comment to avoid DB operations
        video = SimpleNamespace(
            id=uuid.uuid4(),
            platform_video_id="vid_123",
        )

        service = CommentService(session)
        service._get_developer_gateway = AsyncMock(
            return_value=(mock_account, mock_gateway)
        )
        service._upsert_comment = AsyncMock()

        count = await service.sync_comments(uuid.uuid4(), video)

        assert count == 1
        mock_gateway.post.assert_called_once()
        call_args = mock_gateway.post.call_args
        assert call_args[0][0] == "/video/comment/list/"
        assert call_args[1]["json_body"]["video_id"] == "vid_123"

    @pytest.mark.asyncio
    async def test_sync_comments_upserts(self) -> None:
        session = AsyncMock()
        mock_gateway = AsyncMock()
        mock_account = SimpleNamespace(id=uuid.uuid4())

        comments_data = [
            {"id": "cmt_1", "text": "First", "like_count": 1, "reply_count": 0},
            {"id": "cmt_2", "text": "Second", "like_count": 2, "reply_count": 1},
            {"id": "cmt_3", "text": "Third", "like_count": 0, "reply_count": 0},
        ]
        mock_gateway.post.return_value = {
            "data": {"comments": comments_data, "has_more": False}
        }

        video = SimpleNamespace(
            id=uuid.uuid4(), platform_video_id="vid_456"
        )

        service = CommentService(session)
        service._get_developer_gateway = AsyncMock(
            return_value=(mock_account, mock_gateway)
        )
        service._upsert_comment = AsyncMock()

        count = await service.sync_comments(uuid.uuid4(), video)

        assert count == 3
        assert service._upsert_comment.call_count == 3

    @pytest.mark.asyncio
    async def test_sync_comments_pagination(self) -> None:
        session = AsyncMock()
        mock_gateway = AsyncMock()
        mock_account = SimpleNamespace(id=uuid.uuid4())

        # First call: has_more=True with cursor
        page1 = {
            "data": {
                "comments": [{"id": "cmt_1", "text": "Page 1"}],
                "has_more": True,
                "cursor": "abc123",
            }
        }
        # Second call: has_more=False
        page2 = {
            "data": {
                "comments": [{"id": "cmt_2", "text": "Page 2"}],
                "has_more": False,
            }
        }
        mock_gateway.post = AsyncMock(side_effect=[page1, page2])

        video = SimpleNamespace(
            id=uuid.uuid4(), platform_video_id="vid_789"
        )

        service = CommentService(session)
        service._get_developer_gateway = AsyncMock(
            return_value=(mock_account, mock_gateway)
        )
        service._upsert_comment = AsyncMock()

        count = await service.sync_comments(uuid.uuid4(), video)

        assert count == 2
        assert mock_gateway.post.call_count == 2
        # Second call should include cursor
        second_call_body = mock_gateway.post.call_args_list[1][1]["json_body"]
        assert second_call_body["cursor"] == "abc123"


class TestReplyToComment:
    @pytest.mark.asyncio
    async def test_reply_to_comment(self) -> None:
        session = AsyncMock()
        mock_gateway = AsyncMock()
        mock_account = SimpleNamespace(id=uuid.uuid4())

        mock_gateway.post.return_value = {
            "data": {"comment_id": "cmt_reply_1"}
        }

        video = SimpleNamespace(
            id=uuid.uuid4(), platform_video_id="vid_100"
        )

        service = CommentService(session)
        service._get_developer_gateway = AsyncMock(
            return_value=(mock_account, mock_gateway)
        )

        result = await service.reply_to_comment(
            uuid.uuid4(), video, "cmt_parent", "Thanks for watching!"
        )

        assert result == {"comment_id": "cmt_reply_1"}
        mock_gateway.post.assert_called_once_with(
            "/video/comment/reply/create/",
            json_body={
                "video_id": "vid_100",
                "comment_id": "cmt_parent",
                "text": "Thanks for watching!",
            },
        )


class TestDeleteComment:
    @pytest.mark.asyncio
    async def test_delete_comment(self) -> None:
        session = AsyncMock()
        mock_gateway = AsyncMock()
        mock_account = SimpleNamespace(id=uuid.uuid4())

        mock_gateway.post.return_value = {"data": {}}

        video = SimpleNamespace(
            id=uuid.uuid4(), platform_video_id="vid_200"
        )

        service = CommentService(session)
        service._get_developer_gateway = AsyncMock(
            return_value=(mock_account, mock_gateway)
        )

        result = await service.delete_comment(
            uuid.uuid4(), video, "cmt_delete_1"
        )

        assert result is True
        mock_gateway.post.assert_called_once_with(
            "/video/comment/delete/",
            json_body={
                "video_id": "vid_200",
                "comment_id": "cmt_delete_1",
            },
        )


class TestUpsertComment:
    @pytest.mark.asyncio
    async def test_upsert_comment_creates_new(self) -> None:
        session = AsyncMock()
        # Mock: no existing comment found
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock
        session.add = MagicMock()
        session.flush = AsyncMock()

        service = CommentService(session)

        comment_data = {
            "id": "cmt_new_1",
            "text": "Brand new comment",
            "create_time": 1700000000,
            "like_count": 5,
            "reply_count": 1,
            "parent_comment_id": None,
            "username": "test_user",
            "profile_image": "https://img.example.com/avatar.jpg",
        }

        video_id = uuid.uuid4()
        workspace_id = uuid.uuid4()

        comment = await service._upsert_comment(
            video_id, workspace_id, comment_data
        )

        session.add.assert_called_once()
        session.flush.assert_awaited_once()
        assert comment.platform_comment_id == "cmt_new_1"
        assert comment.text == "Brand new comment"
        assert comment.like_count == 5
        assert comment.reply_count == 1
        assert comment.author_username == "test_user"

    @pytest.mark.asyncio
    async def test_upsert_comment_updates_existing(self) -> None:
        session = AsyncMock()
        existing = SimpleNamespace(
            id=uuid.uuid4(),
            platform_comment_id="cmt_exist_1",
            text="Old text",
            like_count=1,
            reply_count=0,
            parent_comment_id=None,
            author_username="old_user",
            author_avatar_url=None,
            detail_json=None,
        )
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = existing
        session.execute.return_value = result_mock

        service = CommentService(session)

        comment_data = {
            "id": "cmt_exist_1",
            "text": "Updated text",
            "like_count": 10,
            "reply_count": 3,
            "parent_comment_id": None,
            "username": "new_user",
            "profile_image": "https://img.example.com/new.jpg",
        }

        comment = await service._upsert_comment(
            uuid.uuid4(), uuid.uuid4(), comment_data
        )

        assert comment.text == "Updated text"
        assert comment.like_count == 10
        assert comment.reply_count == 3
        assert comment.author_username == "new_user"
        assert comment.author_avatar_url == "https://img.example.com/new.jpg"
        # Should NOT call session.add for an existing comment
        session.add.assert_not_called()


class TestCommentModel:
    def test_comment_model_creation(self) -> None:
        ws_id = uuid.uuid4()
        vid_id = uuid.uuid4()

        comment = Comment()
        comment.workspace_id = ws_id
        comment.video_id = vid_id
        comment.platform_comment_id = "cmt_model_1"
        comment.parent_comment_id = "cmt_parent_1"
        comment.text = "Test comment text"
        comment.like_count = 42
        comment.reply_count = 7
        comment.author_username = "tester"
        comment.author_avatar_url = "https://img.example.com/tester.jpg"
        comment.comment_create_time = datetime(
            2026, 2, 20, 12, 0, 0, tzinfo=timezone.utc
        )
        comment.detail_json = {"id": "cmt_model_1", "text": "Test comment text"}

        assert comment.workspace_id == ws_id
        assert comment.video_id == vid_id
        assert comment.platform_comment_id == "cmt_model_1"
        assert comment.parent_comment_id == "cmt_parent_1"
        assert comment.text == "Test comment text"
        assert comment.like_count == 42
        assert comment.reply_count == 7
        assert comment.author_username == "tester"
        assert comment.author_avatar_url == "https://img.example.com/tester.jpg"
        assert comment.comment_create_time == datetime(
            2026, 2, 20, 12, 0, 0, tzinfo=timezone.utc
        )
        assert comment.detail_json == {
            "id": "cmt_model_1",
            "text": "Test comment text",
        }

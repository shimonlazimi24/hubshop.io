import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.content import Comment, Video
from backend.db.models.platform import (
    AccountStatus,
    ConnectedAccount,
    Platform,
    TokenVault,
)
from backend.tiktok.developer.client import TikTokDeveloperClient
from backend.tiktok.gateway import PlatformGateway
from backend.utils.crypto import decrypt_token
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class CommentService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_comments(
        self,
        workspace_id: uuid.UUID,
        video_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Comment]:
        """List comments for a video from the local database."""
        query = select(Comment).where(
            Comment.workspace_id == workspace_id,
            Comment.video_id == video_id,
        )
        count_query = select(func.count(Comment.id)).where(
            Comment.workspace_id == workspace_id,
            Comment.video_id == video_id,
        )

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(Comment.comment_create_time.desc().nulls_last())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    async def sync_comments(self, workspace_id: uuid.UUID, video: Video) -> int:
        """Fetch comments from Developer API and upsert locally.

        Uses cursor pagination (has_more + cursor).
        """
        _, gateway = await self._get_developer_gateway(workspace_id)

        synced = 0
        cursor: str | None = None
        max_count = 20

        while True:
            body: dict = {
                "video_id": video.platform_video_id,
                "max_count": max_count,
            }
            if cursor:
                body["cursor"] = cursor

            resp = await gateway.post(
                "/video/comment/list/",
                json_body=body,
                params={
                    "fields": "id,text,create_time,like_count,reply_count,"
                    "parent_comment_id,username,profile_image"
                },
            )
            data = resp.get("data", {})
            comments = data.get("comments", [])

            for comment_data in comments:
                await self._upsert_comment(video.id, workspace_id, comment_data)
                synced += 1

            has_more = data.get("has_more", False)
            cursor = str(data.get("cursor", "")) if has_more else None
            if not has_more or not comments:
                break

        return synced

    async def reply_to_comment(
        self,
        workspace_id: uuid.UUID,
        video: Video,
        comment_id: str,
        text: str,
    ) -> dict:
        """Reply to a comment via Developer API."""
        _, gateway = await self._get_developer_gateway(workspace_id)

        resp = await gateway.post(
            "/video/comment/reply/create/",
            json_body={
                "video_id": video.platform_video_id,
                "comment_id": comment_id,
                "text": text,
            },
        )
        return resp.get("data", {})

    async def delete_comment(
        self,
        workspace_id: uuid.UUID,
        video: Video,
        comment_id: str,
    ) -> bool:
        """Delete a comment via Developer API."""
        _, gateway = await self._get_developer_gateway(workspace_id)

        resp = await gateway.post(
            "/video/comment/delete/",
            json_body={
                "video_id": video.platform_video_id,
                "comment_id": comment_id,
            },
        )
        return True

    async def _upsert_comment(
        self,
        video_id: uuid.UUID,
        workspace_id: uuid.UUID,
        comment_data: dict,
    ) -> Comment:
        """Upsert a comment from API data into the local database."""
        platform_comment_id = str(comment_data.get("id", ""))
        result = await self._session.execute(
            select(Comment).where(Comment.platform_comment_id == platform_comment_id)
        )
        comment = result.scalar_one_or_none()

        text = comment_data.get("text", "")
        like_count = comment_data.get("like_count", 0)
        reply_count = comment_data.get("reply_count", 0)
        parent_comment_id = comment_data.get("parent_comment_id")
        author_username = comment_data.get("username")
        author_avatar_url = comment_data.get("profile_image")

        comment_create_time = None
        if comment_data.get("create_time"):
            comment_create_time = datetime.fromtimestamp(
                comment_data["create_time"], tz=UTC
            )

        if comment:
            comment.text = text
            comment.like_count = like_count
            comment.reply_count = reply_count
            comment.parent_comment_id = parent_comment_id
            comment.author_username = author_username
            comment.author_avatar_url = author_avatar_url
            comment.detail_json = comment_data
        else:
            comment = Comment(
                workspace_id=workspace_id,
                video_id=video_id,
                platform_comment_id=platform_comment_id,
                parent_comment_id=parent_comment_id,
                text=text,
                like_count=like_count,
                reply_count=reply_count,
                author_username=author_username,
                author_avatar_url=author_avatar_url,
                comment_create_time=comment_create_time,
                detail_json=comment_data,
            )
            self._session.add(comment)
            await self._session.flush()

        return comment

    async def _get_developer_gateway(
        self, workspace_id: uuid.UUID
    ) -> tuple[ConnectedAccount, PlatformGateway]:
        """Get the first active Developer account and its gateway."""
        result = await self._session.execute(
            select(ConnectedAccount).where(
                ConnectedAccount.workspace_id == workspace_id,
                ConnectedAccount.platform == Platform.DEVELOPER,
                ConnectedAccount.status == AccountStatus.ACTIVE,
            )
        )
        account = result.scalars().first()
        if not account:
            raise ValueError("No active Developer account found")

        gateway = await self._build_gateway(account)
        return account, gateway

    async def _build_gateway(self, account: ConnectedAccount) -> PlatformGateway:
        """Build a PlatformGateway for a Developer account."""
        result = await self._session.execute(
            select(TokenVault).where(TokenVault.connected_account_id == account.id)
        )
        vault = result.scalar_one_or_none()
        if not vault:
            raise ValueError(f"No token vault for account {account.id}")

        access_token = decrypt_token(vault.encrypted_access_token)
        client = TikTokDeveloperClient(access_token=access_token)
        return PlatformGateway(
            platform=Platform.DEVELOPER,
            account_id=str(account.id),
            client=client,
        )

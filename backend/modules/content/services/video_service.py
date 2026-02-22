import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.content import Video, VideoMetrics
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


class VideoService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_videos(
        self,
        workspace_id: uuid.UUID,
        *,
        status_filter: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Video]:
        query = select(Video).where(Video.workspace_id == workspace_id)
        count_query = select(func.count(Video.id)).where(
            Video.workspace_id == workspace_id
        )

        if status_filter:
            query = query.where(Video.status == status_filter)
            count_query = count_query.where(Video.status == status_filter)
        if search:
            query = query.where(Video.title.ilike(f"%{search}%"))
            count_query = count_query.where(Video.title.ilike(f"%{search}%"))

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(Video.create_time.desc().nulls_last())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(
            items=items, total=total, page=page, page_size=page_size
        )

    async def get_video(self, video_id: uuid.UUID) -> Video | None:
        result = await self._session.execute(
            select(Video).where(Video.id == video_id)
        )
        return result.scalar_one_or_none()

    async def get_video_metrics(
        self, video_id: uuid.UUID
    ) -> list[VideoMetrics]:
        result = await self._session.execute(
            select(VideoMetrics)
            .where(VideoMetrics.video_id == video_id)
            .order_by(VideoMetrics.date.desc())
        )
        return list(result.scalars().all())

    async def sync_videos(self, workspace_id: uuid.UUID) -> int:
        """Sync videos from all Developer-connected accounts in workspace."""
        result = await self._session.execute(
            select(ConnectedAccount).where(
                ConnectedAccount.workspace_id == workspace_id,
                ConnectedAccount.platform == Platform.DEVELOPER,
                ConnectedAccount.status == AccountStatus.ACTIVE,
            )
        )
        accounts = result.scalars().all()
        total_synced = 0

        for account in accounts:
            try:
                gateway = await self._build_gateway(account)
                synced = await self._sync_account_videos(
                    workspace_id, account, gateway
                )
                total_synced += synced
            except Exception:
                logger.exception(
                    "Failed to sync videos for account %s", account.id
                )

        return total_synced

    async def _sync_account_videos(
        self,
        workspace_id: uuid.UUID,
        account: ConnectedAccount,
        gateway: PlatformGateway,
    ) -> int:
        """Fetch video list from Developer API and upsert locally."""
        synced = 0
        cursor: str | None = None
        max_count = 20

        while True:
            body: dict = {"max_count": max_count}
            if cursor:
                body["cursor"] = cursor

            resp = await gateway.post(
                "/video/list/",
                json_body=body,
                params={"fields": "id,title,video_description,cover_image_url,share_url,embed_link,duration,create_time,like_count,comment_count,share_count,view_count"},
            )
            data = resp.get("data", {})
            videos = data.get("videos", [])

            for video_data in videos:
                await self._upsert_video(workspace_id, account.id, video_data)
                synced += 1

            has_more = data.get("has_more", False)
            cursor = str(data.get("cursor", "")) if has_more else None
            if not has_more or not videos:
                break

        return synced

    async def _upsert_video(
        self,
        workspace_id: uuid.UUID,
        connected_account_id: uuid.UUID,
        video_data: dict,
    ) -> Video:
        platform_id = str(video_data.get("id", ""))
        result = await self._session.execute(
            select(Video).where(Video.platform_video_id == platform_id)
        )
        video = result.scalar_one_or_none()

        title = video_data.get("title", "")
        description = video_data.get("video_description", "")
        cover_url = video_data.get("cover_image_url")
        embed_link = video_data.get("embed_link")
        duration = video_data.get("duration")
        view_count = video_data.get("view_count", 0)
        like_count = video_data.get("like_count", 0)
        comment_count = video_data.get("comment_count", 0)
        share_count = video_data.get("share_count", 0)

        create_time = None
        if video_data.get("create_time"):
            create_time = datetime.fromtimestamp(
                video_data["create_time"], tz=UTC
            )

        if video:
            video.title = title
            video.description = description
            video.cover_url = cover_url
            video.embed_link = embed_link
            video.duration = duration
            video.view_count = view_count
            video.like_count = like_count
            video.comment_count = comment_count
            video.share_count = share_count
            video.detail_json = video_data
        else:
            video = Video(
                workspace_id=workspace_id,
                connected_account_id=connected_account_id,
                platform_video_id=platform_id,
                title=title,
                description=description,
                cover_url=cover_url,
                embed_link=embed_link,
                duration=duration,
                status="PUBLIC",
                view_count=view_count,
                like_count=like_count,
                comment_count=comment_count,
                share_count=share_count,
                create_time=create_time,
                detail_json=video_data,
            )
            self._session.add(video)
            await self._session.flush()

        return video

    async def publish_video(
        self,
        workspace_id: uuid.UUID,
        *,
        video_url: str,
        title: str | None = None,
        privacy_level: str = "PUBLIC_TO_EVERYONE",
        disable_duet: bool = False,
        disable_comment: bool = False,
        disable_stitch: bool = False,
        brand_content_toggle: bool = False,
        brand_organic_toggle: bool = False,
    ) -> dict:
        """Initiate a direct post via Developer API."""
        account, gateway = await self._get_developer_gateway(workspace_id)

        post_info: dict = {
            "privacy_level": privacy_level,
            "disable_duet": disable_duet,
            "disable_comment": disable_comment,
            "disable_stitch": disable_stitch,
            "brand_content_toggle": brand_content_toggle,
            "brand_organic_toggle": brand_organic_toggle,
        }
        if title:
            post_info["title"] = title

        body = {
            "post_info": post_info,
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": video_url,
            },
        }

        resp = await gateway.post("/post/publish/video/direct_post/", json_body=body)
        return resp.get("data", {})

    async def get_publish_status(
        self, workspace_id: uuid.UUID, publish_id: str
    ) -> dict:
        """Check the status of a published video."""
        _, gateway = await self._get_developer_gateway(workspace_id)

        resp = await gateway.post(
            "/post/publish/status/fetch/",
            json_body={"publish_id": publish_id},
        )
        return resp.get("data", {})

    async def get_creator_info(self, workspace_id: uuid.UUID) -> dict:
        """Fetch creator info (privacy options, limits) from Developer API."""
        _, gateway = await self._get_developer_gateway(workspace_id)

        resp = await gateway.get("/post/publish/creator_info/query/")
        return resp.get("data", {})

    async def query_videos_by_id(
        self, workspace_id: uuid.UUID, video_ids: list[str]
    ) -> list[dict]:
        """Query specific videos by their platform IDs via Developer API."""
        _, gateway = await self._get_developer_gateway(workspace_id)
        resp = await gateway.post(
            "/video/query/",
            json_body={"filters": {"video_ids": video_ids}},
            params={
                "fields": "id,title,video_description,cover_image_url,embed_link,duration,create_time,like_count,comment_count,share_count,view_count"
            },
        )
        return resp.get("data", {}).get("videos", [])

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

    async def _build_gateway(
        self, account: ConnectedAccount
    ) -> PlatformGateway:
        """Build a PlatformGateway for a Developer account."""
        result = await self._session.execute(
            select(TokenVault).where(
                TokenVault.connected_account_id == account.id
            )
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

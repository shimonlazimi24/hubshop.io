import calendar
import logging
import uuid
from collections import defaultdict
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.content import ContentPublishJob, Video
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


class PublishService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_publish_job(
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
    ) -> ContentPublishJob:
        """Create a ContentPublishJob and initiate the publish via Developer API."""
        account, gateway = await self._get_developer_gateway(workspace_id)

        # Build the direct post request body
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
        data = resp.get("data", {})
        publish_id = data.get("publish_id", "")

        job = ContentPublishJob(
            workspace_id=workspace_id,
            connected_account_id=account.id,
            publish_id=publish_id,
            title=title,
            video_url=video_url,
            privacy_level=privacy_level,
            status="PENDING",
            disable_duet=disable_duet,
            disable_comment=disable_comment,
            disable_stitch=disable_stitch,
            brand_content_toggle=brand_content_toggle,
            brand_organic_toggle=brand_organic_toggle,
        )
        self._session.add(job)
        await self._session.flush()

        return job

    async def get_publish_job(
        self, job_id: uuid.UUID
    ) -> ContentPublishJob | None:
        result = await self._session.execute(
            select(ContentPublishJob).where(ContentPublishJob.id == job_id)
        )
        return result.scalar_one_or_none()

    async def list_publish_jobs(
        self,
        workspace_id: uuid.UUID,
        *,
        status_filter: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[ContentPublishJob]:
        query = select(ContentPublishJob).where(
            ContentPublishJob.workspace_id == workspace_id
        )
        count_query = select(func.count(ContentPublishJob.id)).where(
            ContentPublishJob.workspace_id == workspace_id
        )

        if status_filter:
            query = query.where(ContentPublishJob.status == status_filter)
            count_query = count_query.where(
                ContentPublishJob.status == status_filter
            )

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(ContentPublishJob.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(
            items=items, total=total, page=page, page_size=page_size
        )

    async def update_publish_status(
        self,
        publish_id: str,
        status: str,
        platform_video_id: str | None = None,
        error_message: str | None = None,
    ) -> ContentPublishJob | None:
        """Update the local publish job record from a webhook or status check."""
        result = await self._session.execute(
            select(ContentPublishJob).where(
                ContentPublishJob.publish_id == publish_id
            )
        )
        job = result.scalar_one_or_none()
        if not job:
            return None

        job.status = status
        if platform_video_id:
            job.platform_video_id = platform_video_id
        if error_message:
            job.error_message = error_message

        await self._session.flush()
        return job

    async def check_and_update_publish_status(
        self,
        workspace_id: uuid.UUID,
        publish_id: str,
    ) -> ContentPublishJob | None:
        """Check publish status via TikTok API and update local record."""
        result = await self._session.execute(
            select(ContentPublishJob).where(
                ContentPublishJob.publish_id == publish_id
            )
        )
        job = result.scalar_one_or_none()
        if not job:
            return None

        _, gateway = await self._get_developer_gateway(workspace_id)
        resp = await gateway.post(
            "/post/publish/status/fetch/",
            json_body={"publish_id": publish_id},
        )
        data = resp.get("data", {})

        api_status = data.get("status", job.status)
        platform_video_id = data.get("publicaly_available_post_id") or data.get(
            "video_id"
        )
        error_msg = data.get("fail_reason") or data.get("error_msg")

        job.status = api_status
        if platform_video_id:
            job.platform_video_id = str(platform_video_id)
        if error_msg:
            job.error_message = str(error_msg)

        await self._session.flush()
        return job

    async def get_calendar_entries(
        self,
        workspace_id: uuid.UUID,
        year: int,
        month: int,
    ) -> list[dict]:
        """Return video publish dates for the calendar view.

        Combines published videos (by create_time) and scheduled publish
        jobs (by created_at) into a per-day summary.
        """
        _, last_day = calendar.monthrange(year, month)
        start_dt = datetime(year, month, 1, tzinfo=UTC)
        end_dt = datetime(year, month, last_day, 23, 59, 59, tzinfo=UTC)

        # Fetch videos created in this month
        video_result = await self._session.execute(
            select(Video).where(
                Video.workspace_id == workspace_id,
                Video.create_time >= start_dt,
                Video.create_time <= end_dt,
            )
        )
        videos = list(video_result.scalars().all())

        # Fetch publish jobs created in this month
        job_result = await self._session.execute(
            select(ContentPublishJob).where(
                ContentPublishJob.workspace_id == workspace_id,
                ContentPublishJob.created_at >= start_dt,
                ContentPublishJob.created_at <= end_dt,
            )
        )
        jobs = list(job_result.scalars().all())

        # Group by date
        date_videos: dict[str, list] = defaultdict(list)
        for video in videos:
            if video.create_time:
                date_key = video.create_time.strftime("%Y-%m-%d")
                date_videos[date_key].append(video)

        # Also include publish jobs as calendar entries
        for job in jobs:
            if job.created_at:
                date_key = job.created_at.strftime("%Y-%m-%d")
                # Avoid duplicates: only add if no video with matching platform_video_id
                existing_platform_ids = {
                    v.platform_video_id for v in date_videos[date_key]
                }
                if job.platform_video_id and job.platform_video_id in existing_platform_ids:
                    continue
                # Represent job as a lightweight dict compatible with VideoSummaryResponse
                date_videos[date_key].append(job)

        entries: list[dict] = []
        for date_key in sorted(date_videos.keys()):
            items = date_videos[date_key]
            entries.append(
                {
                    "date": date_key,
                    "video_count": len(items),
                    "videos": items,
                }
            )

        return entries

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

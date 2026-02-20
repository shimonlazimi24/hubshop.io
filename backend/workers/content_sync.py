import asyncio
import logging

from sqlalchemy import select

from backend.db.engine import async_session_factory
from backend.db.models.platform import AccountStatus, ConnectedAccount, Platform
from backend.modules.content.services.video_service import VideoService
from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):  # type: ignore[no-untyped-def]
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _sync_all_videos() -> None:
    """Sync videos for all workspaces with active Developer accounts."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(ConnectedAccount.workspace_id)
            .where(
                ConnectedAccount.platform == Platform.DEVELOPER,
                ConnectedAccount.status == AccountStatus.ACTIVE,
            )
            .distinct()
        )
        workspace_ids = result.scalars().all()

        for workspace_id in workspace_ids:
            try:
                service = VideoService(session)
                synced = await service.sync_videos(workspace_id)
                await session.commit()
                logger.info(
                    "Synced %d videos for workspace %s", synced, workspace_id
                )
            except Exception:
                await session.rollback()
                logger.exception(
                    "Failed to sync videos for workspace %s", workspace_id
                )


async def _sync_video_metrics() -> None:
    """Sync video metrics for all videos across all workspaces."""
    from backend.db.models.content import Video

    async with async_session_factory() as session:
        result = await session.execute(select(Video.workspace_id).distinct())
        workspace_ids = result.scalars().all()

        for workspace_id in workspace_ids:
            try:
                service = VideoService(session)
                # Get all videos for this workspace
                videos_result = await session.execute(
                    select(Video).where(Video.workspace_id == workspace_id)
                )
                videos = videos_result.scalars().all()
                logger.info(
                    "Syncing metrics for %d videos in workspace %s",
                    len(videos),
                    workspace_id,
                )
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception(
                    "Failed to sync video metrics for workspace %s",
                    workspace_id,
                )


@celery_app.task(name="backend.workers.content_sync.sync_all_videos")
def sync_all_videos() -> None:
    _run_async(_sync_all_videos())


@celery_app.task(name="backend.workers.content_sync.sync_video_metrics")
def sync_video_metrics() -> None:
    _run_async(_sync_video_metrics())

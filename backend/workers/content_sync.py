import logging
from datetime import UTC, datetime

from sqlalchemy import select

from backend.db.engine import async_session_factory
from backend.db.models.platform import AccountStatus, ConnectedAccount, Platform
from backend.modules.content.services.video_service import VideoService
from backend.workers.async_utils import async_task
from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


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
                logger.info("Synced %d videos for workspace %s", synced, workspace_id)
            except Exception:
                await session.rollback()
                logger.exception("Failed to sync videos for workspace %s", workspace_id)


async def _sync_video_metrics() -> None:
    """Sync video metrics for all videos across all workspaces.

    For each workspace, fetches current metrics from the Developer API
    using the video/query endpoint, then updates local DB records.
    """
    from backend.db.models.content import Video, VideoMetrics

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
                if not videos:
                    continue

                logger.info(
                    "Syncing metrics for %d videos in workspace %s",
                    len(videos),
                    workspace_id,
                )

                # Batch video IDs for API query (Developer API accepts up to 50)
                platform_ids = [
                    v.platform_video_id for v in videos if v.platform_video_id
                ]
                batch_size = 50
                video_map = {v.platform_video_id: v for v in videos}

                for i in range(0, len(platform_ids), batch_size):
                    batch = platform_ids[i : i + batch_size]
                    try:
                        api_videos = await service.query_videos_by_id(
                            workspace_id, batch
                        )
                    except Exception:
                        logger.exception(
                            "Failed to fetch metrics batch for workspace %s",
                            workspace_id,
                        )
                        continue

                    today = datetime.now(tz=UTC).date()
                    for vdata in api_videos:
                        vid = str(vdata.get("id", ""))
                        video = video_map.get(vid)
                        if not video:
                            continue

                        try:
                            # Update the video's cached counts
                            video.view_count = vdata.get("view_count", video.view_count)
                            video.like_count = vdata.get("like_count", video.like_count)
                            video.comment_count = vdata.get(
                                "comment_count", video.comment_count
                            )
                            video.share_count = vdata.get(
                                "share_count", video.share_count
                            )
                            video.detail_json = vdata

                            # Upsert a daily metrics snapshot
                            existing = await session.execute(
                                select(VideoMetrics).where(
                                    VideoMetrics.video_id == video.id,
                                    VideoMetrics.date == today,
                                )
                            )
                            metrics_row = existing.scalar_one_or_none()
                            if metrics_row:
                                metrics_row.views = video.view_count
                                metrics_row.likes = video.like_count
                                metrics_row.comments = video.comment_count
                                metrics_row.shares = video.share_count
                            else:
                                session.add(
                                    VideoMetrics(
                                        video_id=video.id,
                                        date=today,
                                        views=video.view_count,
                                        likes=video.like_count,
                                        comments=video.comment_count,
                                        shares=video.share_count,
                                    )
                                )
                        except Exception:
                            logger.exception(
                                "Failed to update metrics for video %s", vid
                            )

                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception(
                    "Failed to sync video metrics for workspace %s",
                    workspace_id,
                )


@celery_app.task(name="backend.workers.content_sync.sync_all_videos")
@async_task
async def sync_all_videos() -> None:
    await _sync_all_videos()


@celery_app.task(name="backend.workers.content_sync.sync_video_metrics")
@async_task
async def sync_video_metrics() -> None:
    await _sync_video_metrics()

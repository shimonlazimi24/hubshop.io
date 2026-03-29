"""Celery tasks for LIVE stream monitoring and analytics."""

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select, update

from backend.db.engine import async_session_factory
from backend.db.models.live import (
    LiveAnalytics,
    LiveEvent,
    LiveEventType,
    LiveSession,
    SessionStatus,
)
from backend.tiktok.live.client import (
    LiveEventData,
    TikTokLiveClientWrapper,
)
from backend.tiktok.live.client import LiveEventType as ClientEventType
from backend.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):  # type: ignore[no-untyped-def]
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _monitor_live_stream(session_id: str, unique_id: str) -> None:
    """Monitor a TikTok LIVE stream and capture events."""
    wrapper = TikTokLiveClientWrapper(unique_id=unique_id)

    async def on_event(event: LiveEventData) -> None:
        """Store captured event in database."""
        async with async_session_factory() as session:
            try:
                db_event = LiveEvent(
                    session_id=session_id,
                    event_type=LiveEventType(event.event_type.value),
                    user_id=event.user_id,
                    username=event.username,
                    payload=event.payload,
                    timestamp=event.timestamp,
                )
                session.add(db_event)
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("Failed to store LIVE event")

    async def on_end(event: LiveEventData) -> None:
        """Mark session as ended when stream ends."""
        await on_event(event)
        async with async_session_factory() as session:
            try:
                await session.execute(
                    update(LiveSession)
                    .where(LiveSession.id == session_id)
                    .values(
                        status=SessionStatus.ENDED,
                        ended_at=datetime.now(tz=UTC),
                    )
                )
                await session.commit()
                logger.info("LIVE session %s ended", session_id)
            except Exception:
                await session.rollback()
                logger.exception("Failed to update session status")

    # Register callbacks for all event types
    for event_type in ClientEventType:
        if event_type == ClientEventType.LIVE_END:
            wrapper.on_event(event_type, on_end)
        else:
            wrapper.on_event(event_type, on_event)

    # Update session with room_id once connected
    try:
        await wrapper.connect()
    except NotImplementedError:
        logger.error("TikTokLive package not installed")
        async with async_session_factory() as session:
            await session.execute(
                update(LiveSession)
                .where(LiveSession.id == session_id)
                .values(
                    status=SessionStatus.ERROR,
                    error_message="TikTokLive package not installed",
                )
            )
            await session.commit()
    except Exception as exc:
        logger.exception("LIVE monitoring failed for %s", unique_id)
        async with async_session_factory() as session:
            await session.execute(
                update(LiveSession)
                .where(LiveSession.id == session_id)
                .values(
                    status=SessionStatus.ERROR,
                    error_message=str(exc),
                    ended_at=datetime.now(tz=UTC),
                )
            )
            await session.commit()


async def _estimate_peak_concurrent(session, session_id: str) -> int:  # type: ignore[no-untyped-def]
    """Estimate peak concurrent viewers from JOIN events.

    Uses a simple approach: count distinct users who joined within each
    60-second window and return the maximum count observed.
    """
    from sqlalchemy import extract

    join_events = await session.execute(
        select(
            LiveEvent.user_id,
            extract("epoch", LiveEvent.timestamp).label("ts"),
        ).where(
            LiveEvent.session_id == session_id,
            LiveEvent.event_type == LiveEventType.JOIN,
            LiveEvent.user_id.isnot(None),
        )
    )
    rows = join_events.all()
    if not rows:
        return 0

    # Sort by timestamp, then slide a 60-second window
    sorted_rows = sorted(rows, key=lambda r: r.ts)
    peak = 0
    window_start = 0
    seen_in_window: set[str] = set()

    for i, row in enumerate(sorted_rows):
        # Move window start forward while outside 60s window
        while sorted_rows[window_start].ts < row.ts - 60:
            window_start += 1
        # Count unique users in current window
        seen_in_window = {r.user_id for r in sorted_rows[window_start : i + 1]}
        peak = max(peak, len(seen_in_window))

    return peak


async def _sum_gift_repeat_counts(session, session_id: str) -> int:  # type: ignore[no-untyped-def]
    """Sum gift repeat_count values from GIFT event payloads.

    The TikTokLive library stores ``repeat_count`` in the event payload
    but does not include monetary value. This returns the total repeat
    count as a proxy until a gift-value mapping table is available.
    """
    gift_events = await session.execute(
        select(LiveEvent.payload).where(
            LiveEvent.session_id == session_id,
            LiveEvent.event_type == LiveEventType.GIFT,
        )
    )
    total = 0
    for (payload,) in gift_events.all():
        if isinstance(payload, dict):
            total += int(payload.get("repeat_count", 0))
    return total


async def _compute_live_analytics(session_id: str) -> None:
    """Compute analytics for a completed LIVE session."""
    async with async_session_factory() as session:
        try:
            # Count events by type
            counts = {}
            for event_type in LiveEventType:
                result = await session.execute(
                    select(func.count(LiveEvent.id)).where(
                        LiveEvent.session_id == session_id,
                        LiveEvent.event_type == event_type,
                    )
                )
                counts[event_type.value] = result.scalar() or 0

            # Get unique viewers (distinct user_ids from JOIN events)
            viewer_result = await session.execute(
                select(func.count(func.distinct(LiveEvent.user_id))).where(
                    LiveEvent.session_id == session_id,
                    LiveEvent.event_type == LiveEventType.JOIN,
                    LiveEvent.user_id.isnot(None),
                )
            )
            total_viewers = viewer_result.scalar() or 0

            # Top commenters
            top_commenters_result = await session.execute(
                select(LiveEvent.username, func.count(LiveEvent.id).label("count"))
                .where(
                    LiveEvent.session_id == session_id,
                    LiveEvent.event_type == LiveEventType.COMMENT,
                    LiveEvent.username.isnot(None),
                )
                .group_by(LiveEvent.username)
                .order_by(func.count(LiveEvent.id).desc())
                .limit(10)
            )
            top_commenters = [
                {"username": row[0], "count": row[1]}
                for row in top_commenters_result.all()
            ]

            # Top gifters
            top_gifters_result = await session.execute(
                select(LiveEvent.username, func.count(LiveEvent.id).label("count"))
                .where(
                    LiveEvent.session_id == session_id,
                    LiveEvent.event_type == LiveEventType.GIFT,
                    LiveEvent.username.isnot(None),
                )
                .group_by(LiveEvent.username)
                .order_by(func.count(LiveEvent.id).desc())
                .limit(10)
            )
            top_gifters = [
                {"username": row[0], "count": row[1]}
                for row in top_gifters_result.all()
            ]

            # Estimate peak concurrent viewers by counting overlapping join/leave
            # windows. Since the TikTokLive library does not emit viewer-count
            # snapshots, we approximate using the maximum number of unique
            # viewers seen within any 60-second sliding window of JOIN events.
            peak_concurrent = await _estimate_peak_concurrent(session, session_id)

            # Gift revenue: the TikTokLive library provides gift name and
            # repeat_count in the event payload, but does NOT include the
            # monetary value (diamond/coin cost) of each gift. Accurate
            # revenue calculation requires a gift-value mapping table which
            # is not yet implemented. Sum repeat_count as a proxy metric.
            gift_revenue = await _sum_gift_repeat_counts(session, session_id)

            total_engagement = (
                counts.get("comment", 0)
                + counts.get("like", 0)
                + counts.get("share", 0)
            )
            engagement_rate = (
                total_engagement / total_viewers if total_viewers > 0 else 0.0
            )

            analytics = LiveAnalytics(
                session_id=session_id,
                total_viewers=total_viewers,
                peak_concurrent=peak_concurrent,
                total_comments=counts.get("comment", 0),
                total_likes=counts.get("like", 0),
                total_shares=counts.get("share", 0),
                total_follows=counts.get("follow", 0),
                gift_revenue=float(gift_revenue),
                engagement_rate=round(engagement_rate, 4),
                top_commenters=top_commenters,
                top_gifters=top_gifters,
            )
            session.add(analytics)
            await session.commit()
            logger.info("Computed analytics for LIVE session %s", session_id)
        except Exception:
            await session.rollback()
            logger.exception("Failed to compute analytics for session %s", session_id)


async def _cleanup_stale_sessions() -> None:
    """Clean up LIVE sessions stuck in 'monitoring' state for over 24 hours."""
    cutoff = datetime.now(tz=UTC) - timedelta(hours=24)

    async with async_session_factory() as session:
        try:
            await session.execute(
                update(LiveSession)
                .where(
                    LiveSession.status == SessionStatus.MONITORING,
                    LiveSession.started_at < cutoff,
                )
                .values(
                    status=SessionStatus.ERROR,
                    error_message="Session timed out (24h limit)",
                    ended_at=datetime.now(tz=UTC),
                )
            )
            await session.commit()
            logger.info("Cleaned up stale LIVE sessions")
        except Exception:
            await session.rollback()
            logger.exception("Failed to cleanup stale sessions")


@celery_app.task(name="backend.workers.live_sync.monitor_live_stream")
def monitor_live_stream(session_id: str, unique_id: str) -> None:
    """Monitor a LIVE stream. Triggered on-demand by StreamMonitorService."""
    _run_async(_monitor_live_stream(session_id, unique_id))


@celery_app.task(name="backend.workers.live_sync.compute_live_analytics")
def compute_live_analytics(session_id: str) -> None:
    """Compute analytics for a completed session. Triggered on stream end."""
    _run_async(_compute_live_analytics(session_id))


@celery_app.task(name="backend.workers.live_sync.cleanup_stale_sessions")
def cleanup_stale_sessions() -> None:
    """Cleanup stale LIVE sessions. Runs every hour."""
    _run_async(_cleanup_stale_sessions())

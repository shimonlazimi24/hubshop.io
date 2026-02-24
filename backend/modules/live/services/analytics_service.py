"""Service for LIVE session analytics and event queries."""

import logging
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.live import (
    LiveAnalytics,
    LiveEvent,
    LiveSession,
)
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class LiveAnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_session_analytics(
        self,
        workspace_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> LiveAnalytics | None:
        """Return LiveAnalytics for a session (None if not computed yet).

        Validates the session belongs to the workspace before returning analytics.
        """
        # Verify session belongs to workspace
        session_result = await self._session.execute(
            select(LiveSession.id).where(
                LiveSession.id == session_id,
                LiveSession.workspace_id == workspace_id,
            )
        )
        if session_result.scalar_one_or_none() is None:
            return None

        result = await self._session.execute(
            select(LiveAnalytics).where(
                LiveAnalytics.session_id == session_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_session_events(
        self,
        workspace_id: uuid.UUID,
        session_id: uuid.UUID,
        *,
        event_type: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedResult[LiveEvent]:
        """List events for a session, optionally filtered by type, paginated.

        Validates the session belongs to the workspace before returning events.
        """
        # Verify session belongs to workspace
        session_result = await self._session.execute(
            select(LiveSession.id).where(
                LiveSession.id == session_id,
                LiveSession.workspace_id == workspace_id,
            )
        )
        if session_result.scalar_one_or_none() is None:
            return PaginatedResult(items=[], total=0, page=page, page_size=page_size)

        query = select(LiveEvent).where(LiveEvent.session_id == session_id)
        count_query = select(func.count(LiveEvent.id)).where(
            LiveEvent.session_id == session_id
        )

        if event_type:
            query = query.where(LiveEvent.event_type == event_type)
            count_query = count_query.where(LiveEvent.event_type == event_type)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(LiveEvent.timestamp.desc()).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    async def compute_analytics(self, session_id: uuid.UUID) -> None:
        """Trigger analytics computation by dispatching Celery task."""
        from backend.workers.live_sync import compute_live_analytics

        compute_live_analytics.delay(str(session_id))
        logger.info("Dispatched analytics computation for session %s", session_id)

    async def get_sessions_summary(
        self,
        workspace_id: uuid.UUID,
        *,
        days: int = 30,
    ) -> dict:
        """Return summary stats across sessions in the last N days.

        Returns total sessions, average engagement rate, and total viewers.
        """
        cutoff = datetime.now(tz=UTC) - timedelta(days=days)

        # Count total sessions in period
        total_result = await self._session.execute(
            select(func.count(LiveSession.id)).where(
                LiveSession.workspace_id == workspace_id,
                LiveSession.started_at >= cutoff,
            )
        )
        total_sessions = total_result.scalar_one()

        # Get session IDs for the period
        session_ids_result = await self._session.execute(
            select(LiveSession.id).where(
                LiveSession.workspace_id == workspace_id,
                LiveSession.started_at >= cutoff,
            )
        )
        session_ids = [row[0] for row in session_ids_result.all()]

        if not session_ids:
            return {
                "total_sessions": 0,
                "avg_engagement_rate": 0.0,
                "total_viewers": 0,
                "period_days": days,
            }

        # Aggregate analytics for those sessions
        analytics_result = await self._session.execute(
            select(
                func.coalesce(func.avg(LiveAnalytics.engagement_rate), 0.0),
                func.coalesce(func.sum(LiveAnalytics.total_viewers), 0),
            ).where(LiveAnalytics.session_id.in_(session_ids))
        )
        row = analytics_result.one()
        avg_engagement = float(row[0])
        total_viewers = int(row[1])

        return {
            "total_sessions": total_sessions,
            "avg_engagement_rate": round(avg_engagement, 4),
            "total_viewers": total_viewers,
            "period_days": days,
        }

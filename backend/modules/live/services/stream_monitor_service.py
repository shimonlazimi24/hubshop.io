"""Service for managing LIVE stream monitoring sessions."""

import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.live import LiveSession, SessionStatus
from backend.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class StreamMonitorService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def start_monitoring(
        self,
        workspace_id: uuid.UUID,
        unique_id: str,
        title: str | None = None,
    ) -> LiveSession:
        """Create a LiveSession in MONITORING status and dispatch Celery task."""
        from backend.workers.live_sync import monitor_live_stream

        session = LiveSession(
            workspace_id=workspace_id,
            unique_id=unique_id,
            status=SessionStatus.MONITORING.value,
            started_at=datetime.now(tz=UTC),
        )
        self._session.add(session)
        await self._session.flush()

        monitor_live_stream.delay(str(session.id), unique_id)
        logger.info(
            "Started monitoring LIVE for %s (session %s)", unique_id, session.id
        )
        return session

    async def stop_monitoring(
        self,
        workspace_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> LiveSession | None:
        """Mark a session as ENDED with current timestamp."""
        result = await self._session.execute(
            select(LiveSession).where(
                LiveSession.id == session_id,
                LiveSession.workspace_id == workspace_id,
            )
        )
        live_session = result.scalar_one_or_none()
        if live_session is None:
            return None

        live_session.status = SessionStatus.ENDED.value
        live_session.ended_at = datetime.now(tz=UTC)
        await self._session.flush()
        logger.info("Stopped monitoring session %s", session_id)
        return live_session

    async def get_session(
        self,
        workspace_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> LiveSession | None:
        """Get a single session by ID, scoped to workspace."""
        result = await self._session.execute(
            select(LiveSession).where(
                LiveSession.id == session_id,
                LiveSession.workspace_id == workspace_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_sessions(
        self,
        workspace_id: uuid.UUID,
        *,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[LiveSession]:
        """List sessions with optional status filter, paginated."""
        query = select(LiveSession).where(LiveSession.workspace_id == workspace_id)
        count_query = select(func.count(LiveSession.id)).where(
            LiveSession.workspace_id == workspace_id
        )

        if status:
            query = query.where(LiveSession.status == status)
            count_query = count_query.where(LiveSession.status == status)

        total = (await self._session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(LiveSession.started_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())

        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    async def get_active_sessions(
        self,
        workspace_id: uuid.UUID,
    ) -> list[LiveSession]:
        """List sessions currently in MONITORING status."""
        result = await self._session.execute(
            select(LiveSession)
            .where(
                LiveSession.workspace_id == workspace_id,
                LiveSession.status == SessionStatus.MONITORING.value,
            )
            .order_by(LiveSession.started_at.desc())
        )
        return list(result.scalars().all())

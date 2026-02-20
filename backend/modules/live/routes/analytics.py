"""Routes for LIVE session analytics and events."""

import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import PaginatedResponse
from backend.modules.live.schemas import (
    LiveAnalyticsResponse,
    LiveEventResponse,
    SessionsSummaryResponse,
)
from backend.modules.live.services.analytics_service import LiveAnalyticsService

router = APIRouter()


@router.get(
    "/sessions/{session_id}/analytics",
    response_model=LiveAnalyticsResponse,
)
async def get_session_analytics(
    workspace_id: uuid.UUID,
    session_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> LiveAnalyticsResponse:
    """Get analytics for a specific LIVE session."""
    service = LiveAnalyticsService(db)
    analytics = await service.get_session_analytics(workspace_id, session_id)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analytics not found for this session",
        )
    return LiveAnalyticsResponse.model_validate(analytics)


@router.get(
    "/sessions/{session_id}/events",
    response_model=PaginatedResponse[LiveEventResponse],
)
async def get_session_events(
    workspace_id: uuid.UUID,
    session_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    event_type: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> PaginatedResponse[LiveEventResponse]:
    """Get events for a LIVE session, optionally filtered by event type."""
    service = LiveAnalyticsService(db)
    result = await service.get_session_events(
        workspace_id,
        session_id,
        event_type=event_type,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[LiveEventResponse.model_validate(e) for e in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.post("/sessions/{session_id}/compute-analytics")
async def compute_analytics(
    workspace_id: uuid.UUID,
    session_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Trigger analytics computation for a LIVE session."""
    service = LiveAnalyticsService(db)
    # Verify session exists and belongs to workspace
    from backend.modules.live.services.stream_monitor_service import (
        StreamMonitorService,
    )

    monitor_service = StreamMonitorService(db)
    session = await monitor_service.get_session(workspace_id, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    await service.compute_analytics(session_id)
    return {"status": "computing", "session_id": str(session_id)}


@router.get("/summary", response_model=SessionsSummaryResponse)
async def get_sessions_summary(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    days: int = 30,
) -> SessionsSummaryResponse:
    """Get summary statistics across LIVE sessions for the last N days."""
    service = LiveAnalyticsService(db)
    summary = await service.get_sessions_summary(workspace_id, days=days)
    return SessionsSummaryResponse(**summary)

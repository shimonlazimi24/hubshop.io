"""Routes for LIVE stream session management."""

import uuid

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import CurrentUser, DBSession
from backend.modules.commerce.schemas import PaginatedResponse
from backend.modules.live.schemas import LiveSessionResponse, StartMonitoringRequest
from backend.modules.live.services.stream_monitor_service import StreamMonitorService

router = APIRouter()


@router.post("/sessions", response_model=LiveSessionResponse)
async def start_monitoring(
    workspace_id: uuid.UUID,
    body: StartMonitoringRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> LiveSessionResponse:
    """Start monitoring a TikTok LIVE stream."""
    service = StreamMonitorService(db)
    session = await service.start_monitoring(
        workspace_id,
        unique_id=body.unique_id,
        title=body.title,
    )
    return LiveSessionResponse.model_validate(session)


@router.delete("/sessions/{session_id}", response_model=LiveSessionResponse)
async def stop_monitoring(
    workspace_id: uuid.UUID,
    session_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> LiveSessionResponse:
    """Stop monitoring a LIVE stream session."""
    service = StreamMonitorService(db)
    session = await service.stop_monitoring(workspace_id, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return LiveSessionResponse.model_validate(session)


@router.get(
    "/sessions/active",
    response_model=list[LiveSessionResponse],
)
async def get_active_sessions(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[LiveSessionResponse]:
    """Get all currently active (monitoring) sessions."""
    service = StreamMonitorService(db)
    sessions = await service.get_active_sessions(workspace_id)
    return [LiveSessionResponse.model_validate(s) for s in sessions]


@router.get(
    "/sessions",
    response_model=PaginatedResponse[LiveSessionResponse],
)
async def list_sessions(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    status_filter: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[LiveSessionResponse]:
    """List all sessions with optional status filter."""
    service = StreamMonitorService(db)
    result = await service.list_sessions(
        workspace_id,
        status=status_filter,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[LiveSessionResponse.model_validate(s) for s in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        total_pages=result.total_pages,
    )


@router.get("/sessions/{session_id}", response_model=LiveSessionResponse)
async def get_session(
    workspace_id: uuid.UUID,
    session_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> LiveSessionResponse:
    """Get a single session by ID."""
    service = StreamMonitorService(db)
    session = await service.get_session(workspace_id, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return LiveSessionResponse.model_validate(session)

import uuid

from fastapi import APIRouter, HTTPException

from backend.dependencies import CurrentUser, DBSession
from backend.modules.analytics.schemas import (
    NotificationPreferenceResponse,
    NotificationResponse,
    UpdatePreferenceRequest,
)
from backend.modules.analytics.services.notification_service import (
    NotificationService,
)

router = APIRouter()


@router.get("/notifications")
async def list_notifications(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    is_read: bool | None = None,
    module: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """List notifications for the current user."""
    service = NotificationService(db)
    result = await service.list_notifications(
        current_user.id,
        workspace_id=workspace_id,
        is_read=is_read,
        module=module,
        page=page,
        page_size=page_size,
    )
    return {
        "items": [NotificationResponse.model_validate(n) for n in result.items],
        "total": result.total,
        "page": result.page,
        "page_size": result.page_size,
        "total_pages": result.total_pages,
    }


@router.get("/notifications/unread-count")
async def get_unread_count(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Get unread notification count."""
    service = NotificationService(db)
    count = await service.get_unread_count(current_user.id, workspace_id)
    return {"count": count}


@router.post("/notifications/{notification_id}/read")
async def mark_read(
    notification_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> NotificationResponse:
    """Mark a notification as read."""
    service = NotificationService(db)
    notification = await service.mark_read(notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    await db.commit()
    return NotificationResponse.model_validate(notification)


@router.post("/notifications/read-all")
async def mark_all_read(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Mark all notifications as read."""
    service = NotificationService(db)
    updated = await service.mark_all_read(current_user.id, workspace_id)
    await db.commit()
    return {"updated": updated}


@router.get("/notifications/preferences")
async def get_preferences(
    current_user: CurrentUser,
    db: DBSession,
) -> list[NotificationPreferenceResponse]:
    """Get notification preferences."""
    service = NotificationService(db)
    prefs = await service.get_preferences(current_user.id)
    return [NotificationPreferenceResponse.model_validate(p) for p in prefs]


@router.put("/notifications/preferences")
async def update_preference(
    body: UpdatePreferenceRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> NotificationPreferenceResponse:
    """Update a notification preference."""
    service = NotificationService(db)
    pref = await service.update_preference(
        current_user.id, body.module, body.channel, body.is_enabled
    )
    await db.commit()
    return NotificationPreferenceResponse.model_validate(pref)

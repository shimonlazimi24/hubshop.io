import uuid

from fastapi import APIRouter

from backend.dependencies import CurrentUser, DBSession

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/videos")
async def list_videos(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """List TikTok videos. Phase 4 implementation."""
    return {"videos": [], "message": "Content module - Phase 4"}

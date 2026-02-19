import uuid

from fastapi import APIRouter

from backend.dependencies import CurrentUser, DBSession

router = APIRouter(prefix="/creators", tags=["creators"])


@router.get("/discover")
async def discover_creators(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Discover TikTok creators. Phase 5 implementation."""
    return {"creators": [], "message": "Creators module - Phase 5"}

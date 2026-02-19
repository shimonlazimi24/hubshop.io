import uuid

from fastapi import APIRouter

from backend.dependencies import CurrentUser, DBSession

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def get_overview(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Get unified analytics overview. Phase 6 implementation."""
    return {"kpis": {}, "message": "Analytics module - Phase 6"}

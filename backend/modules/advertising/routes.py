import uuid

from fastapi import APIRouter

from backend.dependencies import CurrentUser, DBSession

router = APIRouter(prefix="/ads", tags=["advertising"])


@router.get("/accounts")
async def list_ad_accounts(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """List ad accounts for a workspace. Phase 3 implementation."""
    return {"ad_accounts": [], "message": "Advertising module - Phase 3"}


@router.get("/campaigns")
async def list_campaigns(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """List campaigns. Phase 3 implementation."""
    return {"campaigns": [], "message": "Advertising module - Phase 3"}

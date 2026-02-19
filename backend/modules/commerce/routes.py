import uuid

from fastapi import APIRouter

from backend.dependencies import CurrentUser, DBSession

router = APIRouter(prefix="/commerce", tags=["commerce"])


@router.get("/shops")
async def list_shops(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """List TikTok shops for a workspace. Phase 2 implementation."""
    return {"shops": [], "message": "Commerce module - Phase 2"}


@router.get("/products")
async def list_products(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """List products from synced shops. Phase 2 implementation."""
    return {"products": [], "message": "Commerce module - Phase 2"}


@router.get("/orders")
async def list_orders(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """List orders from synced shops. Phase 2 implementation."""
    return {"orders": [], "message": "Commerce module - Phase 2"}

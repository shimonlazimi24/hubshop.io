"""Routes for data source management endpoints."""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.intelligence.services.data_source_service import DataSourceService

router = APIRouter()


class RegisterSourceRequest(BaseModel):
    name: str
    source_type: str
    enabled: bool = True
    settings: dict[str, Any] = {}


class ToggleSourceRequest(BaseModel):
    enabled: bool


@router.post("/sources")
async def register_source(
    workspace_id: uuid.UUID,
    body: RegisterSourceRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict[str, Any]:
    """Register a new data source configuration."""
    service = DataSourceService(db)
    return await service.register_source(
        workspace_id,
        {
            "name": body.name,
            "source_type": body.source_type,
            "enabled": body.enabled,
            "settings": body.settings,
        },
        user_id=current_user.id,
    )


@router.get("/sources")
async def list_sources(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict[str, Any]]:
    """List all data source configurations for the workspace."""
    service = DataSourceService(db)
    return await service.list_sources(workspace_id)


@router.patch("/sources/{source_id}")
async def toggle_source(
    source_id: uuid.UUID,
    workspace_id: uuid.UUID,
    body: ToggleSourceRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict[str, Any]:
    """Enable or disable a data source."""
    service = DataSourceService(db)
    result = await service.toggle_source(workspace_id, source_id, body.enabled)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )
    return result

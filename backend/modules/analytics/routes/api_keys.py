import uuid

from fastapi import APIRouter, HTTPException

from backend.dependencies import CurrentUser, DBSession
from backend.modules.analytics.schemas import (
    ApiKeyCreateResponse,
    ApiKeyResponse,
    CreateApiKeyRequest,
)
from backend.modules.analytics.services.api_key_service import ApiKeyService

router = APIRouter()


@router.get("/api-keys")
async def list_keys(
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[ApiKeyResponse]:
    """List API keys for the workspace."""
    service = ApiKeyService(db)
    keys = await service.list_keys(workspace_id)
    return [ApiKeyResponse.model_validate(k) for k in keys]


@router.post("/api-keys", status_code=201)
async def create_key(
    workspace_id: uuid.UUID,
    body: CreateApiKeyRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> ApiKeyCreateResponse:
    """Create a new API key. The raw key is only shown once."""
    service = ApiKeyService(db)
    key, raw_key = await service.create_key(
        workspace_id, current_user.id, name=body.name, scopes=body.scopes
    )
    await db.commit()
    return ApiKeyCreateResponse(
        key=ApiKeyResponse.model_validate(key),
        raw_key=raw_key,
    )


@router.delete("/api-keys/{key_id}")
async def revoke_key(
    key_id: uuid.UUID,
    workspace_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> ApiKeyResponse:
    """Revoke an API key."""
    service = ApiKeyService(db)
    key = await service.revoke_key(key_id, workspace_id)
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    await db.commit()
    return ApiKeyResponse.model_validate(key)

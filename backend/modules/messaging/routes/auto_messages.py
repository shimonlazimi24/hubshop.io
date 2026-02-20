"""Messaging routes — auto-message CRUD (create, list, update, toggle, delete)."""

import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.messaging.services.messaging_service import MessagingService

router = APIRouter(prefix="/auto-messages")


# --- Request models ---


class CreateAutoMessageRequest(BaseModel):
    connected_account_id: uuid.UUID
    message_type: str
    content: str


class UpdateAutoMessageRequest(BaseModel):
    connected_account_id: uuid.UUID
    content: str


class ToggleAutoMessageRequest(BaseModel):
    connected_account_id: uuid.UUID
    enabled: bool


class DeleteAutoMessageRequest(BaseModel):
    connected_account_id: uuid.UUID


# --- Endpoints ---


@router.get("")
async def list_auto_messages(
    connected_account_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """List all auto-messages for a connected account."""
    service = MessagingService(db)
    return await service.list_auto_messages(connected_account_id)


@router.post("")
async def create_auto_message(
    body: CreateAutoMessageRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Create a new auto-message."""
    service = MessagingService(db)
    return await service.create_auto_message(
        body.connected_account_id,
        message_type=body.message_type,
        content=body.content,
    )


@router.post("/{auto_message_id}")
async def update_auto_message(
    auto_message_id: str,
    body: UpdateAutoMessageRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Update an existing auto-message's content."""
    service = MessagingService(db)
    return await service.update_auto_message(
        body.connected_account_id,
        auto_message_id=auto_message_id,
        content=body.content,
    )


@router.post("/{auto_message_id}/toggle")
async def toggle_auto_message(
    auto_message_id: str,
    body: ToggleAutoMessageRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Toggle an auto-message on or off."""
    service = MessagingService(db)
    return await service.toggle_auto_message(
        body.connected_account_id,
        auto_message_id=auto_message_id,
        enabled=body.enabled,
    )


@router.delete("/{auto_message_id}")
async def delete_auto_message(
    auto_message_id: str,
    body: DeleteAutoMessageRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Delete an auto-message."""
    service = MessagingService(db)
    return await service.delete_auto_message(
        body.connected_account_id,
        auto_message_id=auto_message_id,
    )

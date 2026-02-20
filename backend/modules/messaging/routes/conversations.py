"""Messaging routes — conversations, messages, capability, and comment-to-message settings."""

import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from backend.dependencies import CurrentUser, DBSession
from backend.modules.messaging.services.messaging_service import MessagingService

router = APIRouter()


# --- Request models ---


class SendMessageRequest(BaseModel):
    content: str
    media_url: str | None = None


class ToggleCommentToMessageRequest(BaseModel):
    enabled: bool


# --- Endpoints ---


@router.get("/conversations")
async def list_conversations(
    connected_account_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """List business messaging conversations for a connected account."""
    service = MessagingService(db)
    return await service.list_conversations(
        connected_account_id, page=page, page_size=page_size
    )


@router.get("/conversations/{conversation_id}/messages")
async def list_messages(
    conversation_id: str,
    connected_account_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """List messages in a specific conversation."""
    service = MessagingService(db)
    return await service.list_messages(
        connected_account_id, conversation_id, page=page, page_size=page_size
    )


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    connected_account_id: uuid.UUID,
    body: SendMessageRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Send a message in a conversation."""
    service = MessagingService(db)
    return await service.send_message(
        connected_account_id,
        conversation_id,
        body.content,
        media_url=body.media_url,
    )


@router.get("/capability")
async def check_capability(
    connected_account_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Check business messaging capability for the connected account."""
    service = MessagingService(db)
    return await service.check_capability(connected_account_id)


@router.post("/comment-to-message/toggle")
async def toggle_comment_to_message(
    connected_account_id: uuid.UUID,
    body: ToggleCommentToMessageRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Toggle the comment-to-message feature."""
    service = MessagingService(db)
    return await service.toggle_comment_to_message(
        connected_account_id, enabled=body.enabled
    )


@router.get("/comment-to-message/setting")
async def get_comment_to_message_setting(
    connected_account_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Get the current comment-to-message setting."""
    service = MessagingService(db)
    return await service.get_comment_to_message_setting(connected_account_id)

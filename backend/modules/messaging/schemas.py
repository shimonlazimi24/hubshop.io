"""Pydantic schemas for the messaging module — conversations, messages, auto-messages."""

from __future__ import annotations

import uuid

from pydantic import BaseModel

# --- Conversations ---


class ConversationResponse(BaseModel):
    conversation_id: str
    user_id: str | None = None
    username: str | None = None
    last_message: str | None = None
    last_message_time: str | None = None
    unread_count: int = 0


class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse] = []
    total: int = 0
    page: int = 1
    page_size: int = 20


# --- Messages ---


class MessageResponse(BaseModel):
    message_id: str
    conversation_id: str
    content: str
    media_url: str | None = None
    sender_type: str | None = None
    created_at: str | None = None


class MessageListResponse(BaseModel):
    messages: list[MessageResponse] = []
    total: int = 0
    page: int = 1
    page_size: int = 20


class SendMessageRequest(BaseModel):
    content: str
    media_url: str | None = None


class SendMessageResponse(BaseModel):
    message_id: str | None = None
    status: str = "sent"


# --- Capability ---


class CapabilityResponse(BaseModel):
    enabled: bool = False
    features: list[str] = []


# --- Comment-to-Message ---


class ToggleCommentToMessageRequest(BaseModel):
    enabled: bool


class CommentToMessageSettingResponse(BaseModel):
    enabled: bool = False


# --- Auto-Messages ---


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


class AutoMessageResponse(BaseModel):
    auto_message_id: str
    message_type: str
    content: str
    enabled: bool = True
    created_at: str | None = None


class AutoMessageListResponse(BaseModel):
    auto_messages: list[AutoMessageResponse] = []

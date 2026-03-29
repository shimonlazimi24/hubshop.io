"""Pydantic schemas for the connect module — accounts, OAuth, and sync jobs."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict

# --- Connected Account ---


class ConnectedAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    platform: str
    platform_account_id: str
    platform_account_name: str | None = None
    status: str
    identity_group_id: uuid.UUID | None = None


# --- OAuth ---


class AuthorizeResponse(BaseModel):
    authorize_url: str


# --- Sync Jobs ---


class SyncJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform: str
    sync_type: str
    status: str
    items_synced: int | None = None
    items_total: int | None = None
    error_message: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    created_at: str | None = None


class TriggerSyncResponse(BaseModel):
    status: str
    job_ids: list[str]

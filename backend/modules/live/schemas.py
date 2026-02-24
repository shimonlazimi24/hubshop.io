"""Pydantic schemas for LIVE module request/response models."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

# --- Request Schemas ---


class StartMonitoringRequest(BaseModel):
    unique_id: str
    title: str | None = None


# --- Response Schemas ---


class LiveSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    unique_id: str
    room_id: str | None = None
    status: str
    started_at: datetime
    ended_at: datetime | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


class LiveEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    event_type: str
    user_id: str | None = None
    username: str | None = None
    payload: dict
    timestamp: datetime


class LiveAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    total_viewers: int
    peak_concurrent: int
    total_comments: int
    total_likes: int
    total_shares: int
    total_follows: int
    gift_revenue: float
    engagement_rate: float
    top_commenters: dict | None = None
    top_gifters: dict | None = None
    created_at: datetime
    updated_at: datetime


class SessionsSummaryResponse(BaseModel):
    total_sessions: int
    avg_engagement_rate: float
    total_viewers: int
    period_days: int

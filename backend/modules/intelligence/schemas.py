"""Pydantic schemas for the intelligence module — trends, competitors, creators, data sources."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

# --- Trends ---


class TrendSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    engagement_score: float
    region: str | None = None
    captured_at: str | None = None
    metadata: dict[str, Any] | None = None


class TrendHistoryPoint(BaseModel):
    date: str | None = None
    engagement_score: float


# --- Competitors ---


class AddCompetitorRequest(BaseModel):
    tiktok_username: str


class CompareCompetitorsRequest(BaseModel):
    competitor_ids: list[uuid.UUID]


class CompetitorSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    display_name: str | None = None
    profile_data: dict[str, Any] | None = None
    last_synced_at: str | None = None


class CompetitorContentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    video_id: str
    description: str | None = None
    metrics: dict[str, Any] | None = None
    hashtags: list[str] | None = None
    published_at: str | None = None


class CompetitorDetailResponse(BaseModel):
    id: str
    username: str
    display_name: str | None = None
    profile_data: dict[str, Any] | None = None
    last_synced_at: str | None = None
    content: list[CompetitorContentResponse] = []


class CompetitorComparisonResponse(BaseModel):
    id: str
    username: str
    display_name: str | None = None
    video_count: int
    total_likes: int
    total_comments: int
    total_shares: int
    total_views: int
    avg_engagement: float


# --- Creators ---


class DiscoverCreatorsRequest(BaseModel):
    keyword: str | None = None
    hashtag: str | None = None
    min_followers: int = 0
    max_count: int = 50


# --- Data Sources ---


class RegisterSourceRequest(BaseModel):
    name: str
    source_type: str
    enabled: bool = True
    settings: dict[str, Any] = {}


class ToggleSourceRequest(BaseModel):
    enabled: bool


class DataSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    source_type: str
    enabled: bool
    settings: dict[str, Any] | None = None
    created_at: datetime | None = None

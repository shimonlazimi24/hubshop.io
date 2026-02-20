from datetime import datetime

from pydantic import BaseModel, ConfigDict

# --- KPI Overview ---


class KpiOverviewResponse(BaseModel):
    total_orders: int
    active_campaigns: int
    total_videos: int
    total_views: int
    saved_creators: int


class KpiTimeseriesPoint(BaseModel):
    date: str
    total_orders: int
    total_revenue: str
    active_campaigns: int
    total_views: int


class DrillDownResponse(BaseModel):
    module: str
    stats: dict


# --- Scheduled Reports ---


class ScheduledReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    modules: dict | list
    metrics: dict
    frequency: str
    format: str
    is_active: bool
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class CreateReportRequest(BaseModel):
    name: str
    description: str | None = None
    modules: list[str]
    metrics: dict | None = None
    frequency: str = "WEEKLY"
    format: str = "CSV"


class UpdateReportRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    modules: list[str] | None = None
    frequency: str | None = None
    format: str | None = None
    is_active: bool | None = None


# --- Notifications ---


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    notification_type: str
    title: str
    message: str
    module: str | None = None
    action_url: str | None = None
    is_read: bool
    read_at: datetime | None = None
    created_at: datetime


class NotificationPreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    module: str
    channel: str
    is_enabled: bool


class UpdatePreferenceRequest(BaseModel):
    module: str
    channel: str
    is_enabled: bool


# --- API Keys ---


class ApiKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    key_prefix: str
    scopes: dict | list
    is_active: bool
    last_used_at: datetime | None = None
    expires_at: datetime | None = None
    created_at: datetime


class ApiKeyCreateResponse(BaseModel):
    key: ApiKeyResponse
    raw_key: str


class CreateApiKeyRequest(BaseModel):
    name: str
    scopes: list[str] | None = None

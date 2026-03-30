from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class SpsSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    shop_id: str
    date: date
    estimated_score: str
    return_rate: str | None = None
    cancellation_rate: str | None = None
    otdr: str | None = None
    im_dissatisfaction_rate: str | None = None
    after_sales_handling_hours: str | None = None
    review_rate: str | None = None
    settlement_tier_eligible: str | None = None
    created_at: datetime
    updated_at: datetime


class SpsCurrentResponse(BaseModel):
    estimated_score: str
    return_rate: str
    cancellation_rate: str
    otdr: str
    total_orders: int
    total_shipped: int


class ViolationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    shop_id: str
    violation_type: str
    points: int
    description: str
    occurred_at: datetime
    expires_at: datetime
    resolved: bool
    source: str
    detail_json: dict | None = None
    created_at: datetime
    updated_at: datetime


class CreateViolationRequest(BaseModel):
    shop_id: str
    violation_type: str
    points: int
    description: str
    occurred_at: datetime
    expires_at: datetime


class HealthAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    shop_id: str
    alert_type: str
    severity: str
    message: str
    metric_name: str
    current_value: str
    threshold_value: str
    triggered_at: datetime
    acknowledged_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class AcknowledgeAlertRequest(BaseModel):
    pass


class UnifiedMetricsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    shop_id: str
    date: date
    total_gmv: str
    order_count: int
    return_count: int
    cancellation_count: int
    avg_order_value: str | None = None
    affiliate_gmv: str | None = None
    paid_gmv: str | None = None
    organic_gmv: str | None = None
    cs_response_rate: str | None = None
    active_promotions: int
    active_campaigns: int
    created_at: datetime
    updated_at: datetime


class PaginatedAlertsResponse(BaseModel):
    items: list[HealthAlertResponse]
    total: int
    page: int
    page_size: int

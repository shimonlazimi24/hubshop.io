from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreateDraftRequest(BaseModel):
    campaign_type: str
    product_ids: list[str] | None = None
    daily_budget: float
    roi_target: float | None = None
    notes: str | None = None


class LinkDraftRequest(BaseModel):
    ads_manager_campaign_id: str


class DraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    campaign_type: str
    product_ids: list[str] | None = None
    daily_budget: float
    roi_target: float | None = None
    status: str
    ads_manager_campaign_id: str | None = None
    created_by: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class DeepLinkResponse(BaseModel):
    url: str
    campaign_type: str

from datetime import datetime

from pydantic import BaseModel, ConfigDict

# --- Ad Account ---


class AdAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    advertiser_id: str
    advertiser_name: str
    currency: str | None = None
    timezone: str | None = None
    last_sync_at: datetime | None = None
    created_at: datetime


# --- Campaign ---


class CampaignSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_campaign_id: str
    campaign_name: str
    objective_type: str | None = None
    budget_mode: str | None = None
    budget: str | None = None
    operation_status: str
    secondary_status: str | None = None
    created_at: datetime
    updated_at: datetime


class CampaignDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_campaign_id: str
    campaign_name: str
    objective_type: str | None = None
    budget_mode: str | None = None
    budget: str | None = None
    operation_status: str
    secondary_status: str | None = None
    detail_json: dict | None = None
    created_at: datetime
    updated_at: datetime


class CreateCampaignRequest(BaseModel):
    ad_account_id: str
    campaign_name: str
    objective_type: str
    budget_mode: str
    budget: str | None = None


class UpdateCampaignRequest(BaseModel):
    campaign_name: str | None = None
    budget_mode: str | None = None
    budget: str | None = None


# --- Ad Group ---


class AdGroupSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_adgroup_id: str
    adgroup_name: str
    placement_type: str | None = None
    bid_type: str | None = None
    bid_amount: str | None = None
    budget: str | None = None
    optimization_goal: str | None = None
    operation_status: str
    created_at: datetime
    updated_at: datetime


class AdGroupDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_adgroup_id: str
    adgroup_name: str
    placement_type: str | None = None
    bid_type: str | None = None
    bid_amount: str | None = None
    budget: str | None = None
    optimization_goal: str | None = None
    operation_status: str
    targeting_json: dict | None = None
    detail_json: dict | None = None
    created_at: datetime
    updated_at: datetime


class CreateAdGroupRequest(BaseModel):
    ad_account_id: str
    campaign_id: str
    adgroup_name: str
    placement_type: str = "PLACEMENT_TYPE_AUTOMATIC"
    bid_type: str | None = None
    bid_amount: str | None = None
    budget: str | None = None
    optimization_goal: str | None = None
    targeting: dict | None = None


class UpdateAdGroupRequest(BaseModel):
    adgroup_name: str | None = None
    bid_type: str | None = None
    bid_amount: str | None = None
    budget: str | None = None
    optimization_goal: str | None = None
    targeting: dict | None = None


# --- Ad ---


class AdSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_ad_id: str
    ad_name: str
    ad_format: str | None = None
    ad_text: str | None = None
    call_to_action: str | None = None
    landing_page_url: str | None = None
    image_url: str | None = None
    operation_status: str
    created_at: datetime
    updated_at: datetime


class AdDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_ad_id: str
    ad_name: str
    ad_format: str | None = None
    ad_text: str | None = None
    call_to_action: str | None = None
    landing_page_url: str | None = None
    image_url: str | None = None
    operation_status: str
    detail_json: dict | None = None
    created_at: datetime
    updated_at: datetime


class CreateAdRequest(BaseModel):
    ad_account_id: str
    adgroup_id: str
    ad_name: str
    ad_format: str | None = None
    ad_text: str | None = None
    call_to_action: str | None = None
    landing_page_url: str | None = None


class UpdateAdRequest(BaseModel):
    ad_name: str | None = None
    ad_text: str | None = None
    call_to_action: str | None = None
    landing_page_url: str | None = None


# --- Status Update (shared) ---


class StatusUpdateRequest(BaseModel):
    operation_status: str


# --- Report ---


class ReportRequest(BaseModel):
    ad_account_id: str
    report_type: str = "BASIC"
    data_level: str = "AUCTION_CAMPAIGN"
    date_start: str
    date_end: str
    metrics: list[str] = []
    dimensions: list[str] = []


class ReportRowResponse(BaseModel):
    dimensions: dict
    metrics: dict


class ReportResponse(BaseModel):
    rows: list[ReportRowResponse]
    total_rows: int


class AsyncReportTaskResponse(BaseModel):
    task_id: str


class AsyncReportStatusResponse(BaseModel):
    task_id: str
    status: str
    download_url: str | None = None


# --- Audience ---


class AudienceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_audience_id: str
    name: str
    audience_type: str
    size: int | None = None
    status: str
    detail_json: dict | None = None
    created_at: datetime
    updated_at: datetime


class CreateCustomAudienceRequest(BaseModel):
    ad_account_id: str
    name: str
    file_paths: list[str] | None = None


class CreateLookalikeAudienceRequest(BaseModel):
    ad_account_id: str
    name: str
    source_audience_id: str
    lookalike_ratio: float = 0.01


# --- Pixel ---


class PixelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_pixel_id: str
    name: str
    pixel_code: str | None = None
    detail_json: dict | None = None
    created_at: datetime
    updated_at: datetime


class CreatePixelRequest(BaseModel):
    ad_account_id: str
    name: str


# --- Catalog ---


class CatalogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_catalog_id: str
    name: str
    product_count: int
    status: str
    detail_json: dict | None = None
    created_at: datetime
    updated_at: datetime


class CreateCatalogRequest(BaseModel):
    ad_account_id: str
    name: str


class AddProductsToCatalogRequest(BaseModel):
    product_ids: list[str]


# --- Business Center ---


class InviteMemberRequest(BaseModel):
    ad_account_id: str
    emails: list[str]
    role: str


class UpdateMemberRequest(BaseModel):
    ad_account_id: str
    role: str


class AddPartnerRequest(BaseModel):
    ad_account_id: str
    partner_bc_id: str
    relationship_type: str = "PARTNER"


class AssignAssetRequest(BaseModel):
    ad_account_id: str
    asset_ids: list[str]
    member_ids: list[str]


class CreateBCAdAccountRequest(BaseModel):
    ad_account_id: str
    advertiser_name: str
    timezone: str
    currency: str
    industry_id: str | None = None


# --- BC Finance ---


class ProcessPaymentRequest(BaseModel):
    ad_account_id: str
    advertiser_id: str
    transfer_type: str
    amount: float


class CreateBillingGroupRequest(BaseModel):
    ad_account_id: str
    billing_group_name: str
    advertiser_ids: list[str] | None = None


# --- Creative Upload ---


class UploadVideoRequest(BaseModel):
    ad_account_id: str
    video_url: str
    video_name: str | None = None


class UploadImageRequest(BaseModel):
    ad_account_id: str
    image_url: str
    image_name: str | None = None

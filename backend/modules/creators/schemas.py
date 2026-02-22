from datetime import datetime

from pydantic import BaseModel, ConfigDict

# --- Creator Profile ---


class CreatorProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_creator_id: str
    username: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    follower_count: int
    following_count: int
    likes_count: int
    video_count: int
    tier: str | None = None
    categories: dict | None = None
    engagement_rate: str | None = None
    is_saved: bool
    created_at: datetime
    updated_at: datetime


class CreatorDetailResponse(CreatorProfileResponse):
    audience_demographics: dict | None = None
    detail_json: dict | None = None


# --- Creator Campaign ---


class CreatorCampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    status: str
    budget: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    target_categories: dict | None = None
    requirements: dict | None = None
    created_at: datetime
    updated_at: datetime


class CreateCreatorCampaignRequest(BaseModel):
    name: str
    description: str | None = None
    budget: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    target_categories: list[str] | None = None
    requirements: dict | None = None


class UpdateCreatorCampaignRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    budget: str | None = None


# --- Creator Invitation ---


class CreatorInvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str
    creator_id: str
    status: str
    message: str | None = None
    offered_amount: str | None = None
    responded_at: datetime | None = None
    created_at: datetime


class InviteCreatorRequest(BaseModel):
    creator_id: str
    message: str | None = None
    offered_amount: str | None = None


# --- Content Authorization (Spark Ads) ---


class ContentAuthorizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    creator_id: str
    platform_video_id: str | None = None
    authorization_code: str | None = None
    status: str
    expires_at: datetime | None = None
    created_at: datetime


class RequestAuthorizationRequest(BaseModel):
    creator_id: str
    platform_video_id: str


# --- Discovery ---


class SearchCreatorsRequest(BaseModel):
    query: str | None = None
    min_followers: int | None = None
    max_followers: int | None = None
    categories: list[str] | None = None


# --- Invitation Status Update ---


class UpdateInvitationStatusRequest(BaseModel):
    status: str  # ACCEPTED, DECLINED


# --- Campaign Stats ---


class CampaignStatsResponse(BaseModel):
    total_invitations: int
    pending: int
    accepted: int
    declined: int
    total_offered_amount: str | None = None
    acceptance_rate: float


# --- Save Creator from Discovery ---


class SaveCreatorRequest(BaseModel):
    creator_data: dict

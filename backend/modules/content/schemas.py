from datetime import datetime

from pydantic import BaseModel, ConfigDict

# --- Video ---


class VideoSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_video_id: str
    title: str | None = None
    description: str | None = None
    cover_url: str | None = None
    duration: int | None = None
    status: str
    view_count: int
    like_count: int
    comment_count: int
    share_count: int
    create_time: datetime | None = None
    created_at: datetime
    updated_at: datetime


class VideoDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform_video_id: str
    title: str | None = None
    description: str | None = None
    cover_url: str | None = None
    video_url: str | None = None
    embed_link: str | None = None
    duration: int | None = None
    status: str
    view_count: int
    like_count: int
    comment_count: int
    share_count: int
    create_time: datetime | None = None
    detail_json: dict | None = None
    created_at: datetime
    updated_at: datetime


# --- Video Metrics ---


class VideoMetricsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    date: str
    views: int
    likes: int
    comments: int
    shares: int
    avg_watch_time: float | None = None
    reach: int | None = None


# --- Publish ---


class PublishVideoRequest(BaseModel):
    video_url: str
    title: str | None = None
    privacy_level: str = "PUBLIC_TO_EVERYONE"
    disable_duet: bool = False
    disable_comment: bool = False
    disable_stitch: bool = False
    brand_content_toggle: bool = False
    brand_organic_toggle: bool = False


class PublishStatusResponse(BaseModel):
    publish_id: str
    status: str
    uploaded_bytes: int | None = None
    error_msg: str | None = None


# --- Creator Info ---


class CreatorInfoResponse(BaseModel):
    creator_username: str | None = None
    creator_avatar_url: str | None = None
    privacy_level_options: list[str] = []
    comment_disabled: bool = False
    duet_disabled: bool = False
    stitch_disabled: bool = False
    max_video_post_duration_sec: int = 0


# --- Content Publish Job ---


class ContentPublishJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    publish_id: str
    title: str | None = None
    video_url: str | None = None
    privacy_level: str
    status: str
    platform_video_id: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


# --- Calendar ---


class CalendarEntry(BaseModel):
    date: str
    video_count: int
    videos: list[VideoSummaryResponse]

"""Pydantic schemas for the organic module — accounts, posts, mentions, hashtags."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel

# --- Profile ---


class OrganicProfileResponse(BaseModel):
    username: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    follower_count: int = 0
    following_count: int = 0
    likes_count: int = 0
    video_count: int = 0
    bio: str | None = None


# --- Posts ---


class OrganicPostResponse(BaseModel):
    post_id: str
    title: str | None = None
    description: str | None = None
    cover_url: str | None = None
    video_url: str | None = None
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    view_count: int = 0
    created_at: str | None = None


class OrganicPostListResponse(BaseModel):
    posts: list[OrganicPostResponse] = []
    total: int = 0
    page: int = 1
    page_size: int = 20


# --- Publishing ---


class PublishVideoRequest(BaseModel):
    connected_account_id: uuid.UUID
    video_config: dict[str, Any]


class PublishPhotoRequest(BaseModel):
    connected_account_id: uuid.UUID
    photo_config: dict[str, Any]


class PublishStatusResponse(BaseModel):
    publish_id: str
    status: str
    video_id: str | None = None


# --- Benchmarks ---


class BenchmarkResponse(BaseModel):
    category: str | None = None
    metrics: dict[str, Any] = {}


# --- Hashtag Recommendations ---


class HashtagRecommendationResponse(BaseModel):
    hashtags: list[str] = []


# --- Brand Mentions ---


class MentionPostResponse(BaseModel):
    post_id: str
    username: str | None = None
    description: str | None = None
    like_count: int = 0
    comment_count: int = 0
    view_count: int = 0
    created_at: str | None = None


class MentionKeywordResponse(BaseModel):
    keyword: str
    count: int = 0


class MentionHashtagResponse(BaseModel):
    hashtag: str
    count: int = 0


class CommentMentionResponse(BaseModel):
    comment_id: str
    text: str
    username: str | None = None
    like_count: int = 0
    created_at: str | None = None


# --- Mention Actions ---


class ReplyToMentionRequest(BaseModel):
    connected_account_id: uuid.UUID
    comment_id: str
    text: str


class EnableBrandHashtagRequest(BaseModel):
    connected_account_id: uuid.UUID
    hashtag: str


class BrandHashtagResponse(BaseModel):
    hashtag: str
    enabled: bool = True
    created_at: str | None = None

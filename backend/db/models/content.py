import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.models.base import Base, TimestampMixin, UUIDMixin


class VideoStatus(str, enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    FRIENDS_ONLY = "FRIENDS_ONLY"
    PENDING = "PENDING"
    FAILED = "FAILED"


class Video(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "videos"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    connected_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("connected_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    platform_video_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    embed_link: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    duration: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Duration in seconds"
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PUBLIC")
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    like_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    share_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    create_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    detail_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Full API snapshot"
    )

    metrics: Mapped[list["VideoMetrics"]] = relationship(
        back_populates="video", lazy="noload"
    )

    __table_args__ = (
        Index("ix_videos_workspace_status", "workspace_id", "status"),
        Index("ix_videos_workspace_created", "workspace_id", "created_at"),
    )


class VideoMetrics(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "video_metrics"

    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date: Mapped[datetime] = mapped_column(
        Date, nullable=False, comment="Metrics snapshot date"
    )
    views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    likes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    comments: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    shares: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_watch_time: Mapped[float | None] = mapped_column(Float, nullable=True)
    reach: Mapped[int | None] = mapped_column(Integer, nullable=True)

    video: Mapped["Video"] = relationship(back_populates="metrics")

    __table_args__ = (
        Index("ix_video_metrics_video_date", "video_id", "date", unique=True),
    )


class PublishStatus(str, enum.Enum):
    PENDING = "PENDING"
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


class ContentPublishJob(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "content_publish_jobs"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    connected_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("connected_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    publish_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="TikTok publish_id from direct post API",
    )
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    privacy_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PUBLIC_TO_EVERYONE",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING",
    )
    platform_video_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Populated once publish completes",
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    disable_duet: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    disable_comment: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    disable_stitch: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    brand_content_toggle: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    brand_organic_toggle: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    __table_args__ = (
        Index("ix_content_publish_jobs_workspace_status", "workspace_id", "status"),
    )


class ContentSyncCursor(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "content_sync_cursors"

    connected_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("connected_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    sync_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="videos or video_metrics",
    )
    cursor_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index(
            "ix_content_sync_cursors_account_type",
            "connected_account_id",
            "sync_type",
            unique=True,
        ),
    )


class Comment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "comments"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_comment_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    parent_comment_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Platform ID of parent comment for replies",
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    author_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_avatar_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    comment_create_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    detail_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_comments_video_parent", "video_id", "parent_comment_id"),
    )

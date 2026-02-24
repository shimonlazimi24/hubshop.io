import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.models.base import Base, TimestampMixin, UUIDMixin

# --- Enums ---


class TrendType(str, enum.Enum):
    HASHTAG = "hashtag"
    SOUND = "sound"
    PRODUCT = "product"


# --- Models ---


class TrendSnapshot(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "trend_snapshots"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    trend_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    engagement_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    region: Mapped[str | None] = mapped_column(String(10), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_trend_snapshots_workspace_type_captured",
            "workspace_id",
            "trend_type",
            "captured_at",
        ),
    )


class CompetitorTracker(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "competitor_trackers"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    platform_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index(
            "ix_competitor_trackers_workspace_username",
            "workspace_id",
            "username",
            unique=True,
        ),
    )


class CompetitorContent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "competitor_content"

    tracker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competitor_trackers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    video_id: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metrics: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    hashtags: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index(
            "ix_competitor_content_tracker_video",
            "tracker_id",
            "video_id",
            unique=True,
        ),
    )


class ResearchQuery(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "research_queries"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    query_params: Mapped[dict] = mapped_column(JSONB, nullable=False)
    last_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

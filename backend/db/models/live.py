import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.models.base import Base, TimestampMixin, UUIDMixin

# --- Enums ---


class SessionStatus(str, enum.Enum):
    MONITORING = "monitoring"
    ENDED = "ended"
    ERROR = "error"


class LiveEventType(str, enum.Enum):
    COMMENT = "comment"
    GIFT = "gift"
    LIKE = "like"
    FOLLOW = "follow"
    SHARE = "share"
    JOIN = "join"
    LIVE_END = "live_end"
    COMMERCE = "commerce"


# --- Models ---


class LiveSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "live_sessions"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    unique_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="TikTok username",
    )
    room_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=SessionStatus.MONITORING.value,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index(
            "ix_live_sessions_workspace_status",
            "workspace_id",
            "status",
        ),
    )


class LiveEvent(Base, UUIDMixin):
    """Live event record. Does NOT use TimestampMixin — events have their own timestamp."""

    __tablename__ = "live_events"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("live_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_live_events_session_event_type",
            "session_id",
            "event_type",
        ),
        Index(
            "ix_live_events_session_timestamp",
            "session_id",
            "timestamp",
        ),
    )


class LiveAnalytics(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "live_analytics"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("live_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    total_viewers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    peak_concurrent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_comments: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_likes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_shares: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_follows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    gift_revenue: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    engagement_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    top_commenters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    top_gifters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

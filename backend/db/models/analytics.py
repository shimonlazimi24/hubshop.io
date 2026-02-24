import enum
import hashlib
import secrets
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
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


class ReportFrequency(str, enum.Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class ReportFormat(str, enum.Enum):
    CSV = "CSV"
    XLSX = "XLSX"
    JSON = "JSON"


class NotificationType(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class NotificationChannel(str, enum.Enum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"
    WEBHOOK = "WEBHOOK"


# --- Models ---


class UnifiedKpiSnapshot(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "unified_kpi_snapshots"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
        comment="Snapshot date",
    )
    # Commerce KPIs
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_revenue: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="0",
        comment="Revenue as string to avoid precision issues",
    )
    average_order_value: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="0",
    )
    # Advertising KPIs
    active_campaigns: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_ad_spend: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="0",
    )
    total_impressions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_clicks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Content KPIs
    total_videos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_likes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_shares: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # Creator KPIs
    saved_creators: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active_creator_campaigns: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    # Computed metrics
    roas: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Return on ad spend",
    )
    ctr: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Click-through rate",
    )

    __table_args__ = (
        Index(
            "ix_kpi_snapshots_workspace_date",
            "workspace_id",
            "date",
            unique=True,
        ),
    )


class ScheduledReport(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "scheduled_reports"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    modules: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment='List of modules to include: ["commerce", "advertising", "content", "creators"]',
    )
    metrics: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Specific metrics to include in report",
    )
    frequency: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="WEEKLY",
    )
    format: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="CSV",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    next_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_result_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Result of last report generation",
    )

    __table_args__ = (
        Index("ix_scheduled_reports_workspace_active", "workspace_id", "is_active"),
    )


class Notification(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notifications"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    notification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="INFO",
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    module: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Source module: commerce, advertising, content, creators",
    )
    action_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_notifications_user_read", "user_id", "is_read"),
        Index("ix_notifications_workspace_created", "workspace_id", "created_at"),
    )


class NotificationPreference(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notification_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    module: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Module: commerce, advertising, content, creators, system",
    )
    channel: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="IN_APP",
    )
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index(
            "ix_notification_prefs_user_module",
            "user_id",
            "module",
            "channel",
            unique=True,
        ),
    )


class ApiKey(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "api_keys"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key_prefix: Mapped[str] = mapped_column(
        String(12),
        nullable=False,
        comment="First 8 chars of key for identification",
    )
    key_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
        comment="SHA-256 hash of the full API key",
    )
    scopes: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment='Allowed scopes: ["commerce:read", "ads:read", "content:read"]',
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_api_keys_workspace_active", "workspace_id", "is_active"),
    )

    @staticmethod
    def generate_key() -> tuple[str, str, str]:
        """Generate a new API key, returning (full_key, prefix, hash)."""
        raw = secrets.token_urlsafe(32)
        full_key = f"frodo_{raw}"
        prefix = full_key[:12]
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        return full_key, prefix, key_hash

    @staticmethod
    def hash_key(key: str) -> str:
        """Hash an API key for comparison."""
        return hashlib.sha256(key.encode()).hexdigest()

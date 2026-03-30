import uuid
from datetime import date, datetime

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


class SpsSnapshot(Base, UUIDMixin, TimestampMixin):
    """Daily shop performance score (SPS) snapshot for trend analysis."""

    __tablename__ = "sps_snapshots"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    estimated_score: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="0.0-5.0",
    )
    return_rate: Mapped[str | None] = mapped_column(String(10), nullable=True)
    cancellation_rate: Mapped[str | None] = mapped_column(String(10), nullable=True)
    otdr: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        comment="on-time delivery rate",
    )
    im_dissatisfaction_rate: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )
    after_sales_handling_hours: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )
    review_rate: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        comment="manual input",
    )
    settlement_tier_eligible: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="INTRODUCTORY/STANDARD/ACCELERATED/EXPRESS/DEFERRED",
    )

    __table_args__ = (Index("ix_sps_snapshots_workspace_date", "workspace_id", "date"),)


class ViolationRecord(Base, UUIDMixin, TimestampMixin):
    """Shop policy violation records — tracked for point accumulation."""

    __tablename__ = "violation_records"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=False,
    )
    violation_type: Mapped[str] = mapped_column(String(255), nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="90 days from occurred_at",
    )
    resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="MANUAL or WEBHOOK",
    )
    detail_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_violations_workspace_resolved", "workspace_id", "resolved"),
    )


class HealthAlert(Base, UUIDMixin, TimestampMixin):
    """Alerts generated when shop health metrics cross thresholds."""

    __tablename__ = "health_alerts"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=False,
    )
    alert_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="SPS_DROP/VIOLATION_THRESHOLD/CS_DEGRADATION/OTDR_WARNING",
    )
    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="INFO/WARNING/CRITICAL",
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    current_value: Mapped[str] = mapped_column(String(20), nullable=False)
    threshold_value: Mapped[str] = mapped_column(String(20), nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        Index("ix_health_alerts_workspace_severity", "workspace_id", "severity"),
    )


class UnifiedDailyMetrics(Base, UUIDMixin, TimestampMixin):
    """Aggregated daily commerce metrics for a shop."""

    __tablename__ = "unified_daily_metrics"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    total_gmv: Mapped[str] = mapped_column(String(20), nullable=False)
    order_count: Mapped[int] = mapped_column(Integer, nullable=False)
    return_count: Mapped[int] = mapped_column(Integer, nullable=False)
    cancellation_count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_order_value: Mapped[str | None] = mapped_column(String(20), nullable=True)
    affiliate_gmv: Mapped[str | None] = mapped_column(String(20), nullable=True)
    paid_gmv: Mapped[str | None] = mapped_column(String(20), nullable=True)
    organic_gmv: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cs_response_rate: Mapped[str | None] = mapped_column(String(20), nullable=True)
    active_promotions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active_campaigns: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index(
            "ix_unified_metrics_workspace_date",
            "workspace_id",
            "date",
            unique=True,
        ),
    )

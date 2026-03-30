import enum
import uuid
from datetime import date

from sqlalchemy import (
    Date,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.models.base import Base, TimestampMixin, UUIDMixin

# --- Enums ---


class CampaignType(enum.StrEnum):
    PRODUCT = "PRODUCT"
    LIVE = "LIVE"


class DraftStatus(enum.StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    LINKED = "LINKED"
    ARCHIVED = "ARCHIVED"


# --- Models ---


class GmvMaxDraft(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "gmvmax_drafts"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    campaign_type: Mapped[CampaignType] = mapped_column(
        Enum(CampaignType, name="gmvmax_campaign_type_enum"),
        nullable=False,
    )
    product_ids: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of product IDs to promote",
    )
    daily_budget: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Daily budget in account currency",
    )
    roi_target: Mapped[float | None] = mapped_column(
        Numeric(8, 2),
        nullable=True,
        comment="Target ROI ratio",
    )
    status: Mapped[DraftStatus] = mapped_column(
        Enum(DraftStatus, name="gmvmax_draft_status_enum"),
        nullable=False,
        default=DraftStatus.DRAFT,
    )
    ads_manager_campaign_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Linked Ads Manager campaign ID after submission",
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        Index("ix_gmvmax_drafts_workspace_status", "workspace_id", "status"),
    )


class GmvMaxReport(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "gmvmax_reports"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    campaign_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Ads Manager campaign ID",
    )
    draft_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("gmvmax_drafts.id", ondelete="SET NULL"),
        nullable=True,
    )
    report_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    spend: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )
    total_gmv: Mapped[float] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=0,
    )
    paid_gmv: Mapped[float] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=0,
    )
    organic_gmv: Mapped[float] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=0,
    )
    orders: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    roi: Mapped[float] = mapped_column(
        Numeric(8, 2),
        nullable=False,
        default=0,
    )
    impressions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    clicks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    __table_args__ = (
        Index("ix_gmvmax_reports_workspace_date", "workspace_id", "report_date"),
    )

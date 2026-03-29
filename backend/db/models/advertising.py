import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.models.base import Base, TimestampMixin, UUIDMixin

# --- Enums ---


class CampaignObjective(str, enum.Enum):
    TRAFFIC = "TRAFFIC"
    CONVERSIONS = "CONVERSIONS"
    APP_INSTALL = "APP_INSTALL"
    REACH = "REACH"
    VIDEO_VIEWS = "VIDEO_VIEWS"
    LEAD_GENERATION = "LEAD_GENERATION"
    CATALOG_SALES = "CATALOG_SALES"
    ENGAGEMENT = "ENGAGEMENT"
    PRODUCT_SALES = "PRODUCT_SALES"
    WEB_CONVERSIONS = "WEB_CONVERSIONS"
    APP_PROMOTION = "APP_PROMOTION"


class BudgetMode(str, enum.Enum):
    BUDGET_MODE_TOTAL = "BUDGET_MODE_TOTAL"
    BUDGET_MODE_DAY = "BUDGET_MODE_DAY"
    BUDGET_MODE_INFINITE = "BUDGET_MODE_INFINITE"


class OperationStatus(str, enum.Enum):
    ENABLE = "ENABLE"
    DISABLE = "DISABLE"
    DELETE = "DELETE"


class AdFormat(str, enum.Enum):
    SINGLE_IMAGE = "SINGLE_IMAGE"
    SINGLE_VIDEO = "SINGLE_VIDEO"
    CAROUSEL = "CAROUSEL"
    COLLECTION = "COLLECTION"
    SPARK_ADS = "SPARK_ADS"


# --- Models ---


class AdAccount(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ad_accounts"

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
    advertiser_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="TikTok advertiser ID",
    )
    advertiser_name: Mapped[str] = mapped_column(String(255), nullable=False)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    campaigns: Mapped[list["Campaign"]] = relationship(
        back_populates="ad_account", lazy="noload"
    )


class Campaign(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "campaigns"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ad_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ad_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_campaign_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    campaign_name: Mapped[str] = mapped_column(String(500), nullable=False)
    objective_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Campaign objective (TRAFFIC, CONVERSIONS, etc.)",
    )
    budget_mode: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="BUDGET_MODE_TOTAL, BUDGET_MODE_DAY, BUDGET_MODE_INFINITE",
    )
    budget: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Budget amount as string to avoid precision issues",
    )
    operation_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="ENABLE",
        comment="ENABLE, DISABLE, DELETE",
    )
    secondary_status: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Detailed delivery status from TikTok",
    )
    detail_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Full API snapshot"
    )

    ad_account: Mapped["AdAccount"] = relationship(
        back_populates="campaigns", lazy="selectin"
    )
    ad_groups: Mapped[list["AdGroup"]] = relationship(
        back_populates="campaign", lazy="noload"
    )

    __table_args__ = (
        Index("ix_campaigns_workspace_status", "workspace_id", "operation_status"),
        Index("ix_campaigns_ad_account_status", "ad_account_id", "operation_status"),
        Index("ix_campaigns_workspace_created", "workspace_id", "created_at"),
    )


class AdGroup(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ad_groups"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ad_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ad_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_adgroup_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    adgroup_name: Mapped[str] = mapped_column(String(500), nullable=False)
    placement_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="PLACEMENT_TYPE_AUTOMATIC or PLACEMENT_TYPE_NORMAL",
    )
    bid_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="BID_TYPE_NO_BID, BID_TYPE_CUSTOM, etc."
    )
    bid_amount: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="Bid amount as string"
    )
    budget: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="Ad group budget as string"
    )
    optimization_goal: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="CLICK, CONVERT, REACH, etc."
    )
    operation_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="ENABLE"
    )
    targeting_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Targeting configuration"
    )
    detail_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Full API snapshot"
    )

    campaign: Mapped["Campaign"] = relationship(
        back_populates="ad_groups", lazy="selectin"
    )
    ads: Mapped[list["Ad"]] = relationship(back_populates="ad_group", lazy="noload")

    __table_args__ = (
        Index("ix_ad_groups_workspace_status", "workspace_id", "operation_status"),
        Index("ix_ad_groups_ad_account_status", "ad_account_id", "operation_status"),
        Index("ix_ad_groups_workspace_created", "workspace_id", "created_at"),
    )


class Ad(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ads"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ad_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ad_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    adgroup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ad_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_ad_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    ad_name: Mapped[str] = mapped_column(String(500), nullable=False)
    ad_format: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="SINGLE_IMAGE, SINGLE_VIDEO, etc."
    )
    ad_text: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    call_to_action: Mapped[str | None] = mapped_column(String(100), nullable=True)
    landing_page_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    operation_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="ENABLE"
    )
    detail_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Full API snapshot"
    )

    ad_group: Mapped["AdGroup"] = relationship(back_populates="ads", lazy="selectin")

    __table_args__ = (
        Index("ix_ads_workspace_status", "workspace_id", "operation_status"),
        Index("ix_ads_ad_account_status", "ad_account_id", "operation_status"),
        Index("ix_ads_workspace_created", "workspace_id", "created_at"),
    )


class AdSyncCursor(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ad_sync_cursors"

    ad_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ad_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    sync_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="campaigns, ad_groups, or ads",
    )
    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        Index(
            "ix_ad_sync_cursors_account_type",
            "ad_account_id",
            "sync_type",
            unique=True,
        ),
    )


class AudienceType(str, enum.Enum):
    CUSTOM = "CUSTOM"
    LOOKALIKE = "LOOKALIKE"


class Audience(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "audiences"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ad_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ad_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_audience_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    audience_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="CUSTOM or LOOKALIKE"
    )
    size: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ENABLE")
    detail_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Full API snapshot"
    )

    __table_args__ = (
        Index("ix_audiences_workspace_type", "workspace_id", "audience_type"),
    )


class Pixel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "pixels"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ad_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ad_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_pixel_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    pixel_code: Mapped[str | None] = mapped_column(
        nullable=True, comment="JavaScript pixel code snippet"
    )
    detail_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Full API snapshot"
    )


class Catalog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "catalogs"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ad_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ad_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_catalog_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    product_count: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")
    detail_json: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Full API snapshot"
    )


class ReportCache(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "report_cache"

    ad_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ad_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    report_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="BASIC, AUDIENCE, PLAYABLE"
    )
    data_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="AUCTION_CAMPAIGN, AUCTION_ADGROUP, AUCTION_AD",
    )
    date_range_start: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="YYYY-MM-DD"
    )
    date_range_end: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="YYYY-MM-DD"
    )
    report_data: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Cached report rows"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Cache expiry (1h TTL)",
    )

    __table_args__ = (
        Index(
            "ix_report_cache_lookup",
            "ad_account_id",
            "report_type",
            "data_level",
            "date_range_start",
            "date_range_end",
        ),
    )

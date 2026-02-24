import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.models.base import Base, TimestampMixin, UUIDMixin

# --- Enums ---


class CreatorTier(str, enum.Enum):
    NANO = "NANO"
    MICRO = "MICRO"
    MID = "MID"
    MACRO = "MACRO"
    MEGA = "MEGA"


class CampaignStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class InvitationStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"


class AuthorizationStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


# --- Models ---


class CreatorProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "creator_profiles"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_creator_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="TikTok creator/user ID",
    )
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    follower_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    following_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    likes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    video_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tier: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="NANO, MICRO, MID, MACRO, MEGA",
    )
    categories: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Content categories/niches",
    )
    audience_demographics: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Age, gender, location breakdown",
    )
    engagement_rate: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Average engagement rate as string",
    )
    is_saved: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        comment="Whether creator is saved to workspace list",
    )
    detail_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Full API snapshot",
    )

    invitations: Mapped[list["CreatorInvitation"]] = relationship(
        back_populates="creator",
        lazy="noload",
    )
    authorizations: Mapped[list["ContentAuthorization"]] = relationship(
        back_populates="creator",
        lazy="noload",
    )

    __table_args__ = (
        Index(
            "ix_creator_profiles_workspace_platform",
            "workspace_id",
            "platform_creator_id",
            unique=True,
        ),
        Index("ix_creator_profiles_workspace_saved", "workspace_id", "is_saved"),
    )


class CreatorCampaign(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "creator_campaigns"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="DRAFT",
    )
    budget: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Total campaign budget as string",
    )
    start_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    target_categories: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Target content categories",
    )
    requirements: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Creator requirements (min followers, engagement, etc.)",
    )

    invitations: Mapped[list["CreatorInvitation"]] = relationship(
        back_populates="campaign",
        lazy="noload",
    )

    __table_args__ = (
        Index("ix_creator_campaigns_workspace_status", "workspace_id", "status"),
    )


class CreatorInvitation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "creator_invitations"

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("creator_campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("creator_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING",
    )
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    offered_amount: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Payment offer as string",
    )
    responded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    campaign: Mapped["CreatorCampaign"] = relationship(back_populates="invitations")
    creator: Mapped["CreatorProfile"] = relationship(back_populates="invitations")

    __table_args__ = (
        Index(
            "ix_creator_invitations_campaign_creator",
            "campaign_id",
            "creator_id",
            unique=True,
        ),
    )


class ContentAuthorization(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "content_authorizations"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("creator_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform_video_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="TikTok video ID authorized for Spark Ads",
    )
    authorization_code: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Spark Ads authorization code",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING",
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    creator: Mapped["CreatorProfile"] = relationship(back_populates="authorizations")

    __table_args__ = (
        Index(
            "ix_content_auth_workspace_status",
            "workspace_id",
            "status",
        ),
    )

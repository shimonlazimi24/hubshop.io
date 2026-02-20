import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.models.base import Base, TimestampMixin, UUIDMixin


class CollaborationType(str, enum.Enum):
    OPEN = "OPEN"
    TARGET = "TARGET"


class CollaborationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"


class InviteStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class ApplicationStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class AffiliateProduct(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "affiliate_products"

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
    product_id: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="TikTok product ID"
    )
    commission_rate: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="Commission rate as string (e.g. '10.5')"
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="ACTIVE"
    )
    detail_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_affiliate_products_shop_product", "shop_id", "product_id", unique=True),
    )


class OpenCollaboration(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "open_collaborations"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[str] = mapped_column(String(255), nullable=False)
    commission_rate: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="ACTIVE"
    )
    detail_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class TargetCollaboration(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "target_collaborations"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[str] = mapped_column(String(255), nullable=False)
    creator_id: Mapped[str] = mapped_column(String(255), nullable=False)
    commission_rate: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="ACTIVE"
    )
    invite_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PENDING"
    )
    detail_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class CreatorApplication(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "creator_applications"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    collaboration_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        comment="Open/Target collaboration ID",
    )
    creator_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PENDING"
    )
    detail_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

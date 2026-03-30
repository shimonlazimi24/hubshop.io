import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.models.base import Base, TimestampMixin, UUIDMixin


class Coupon(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "coupons"

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
    platform_coupon_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    code: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="2-8 char coupon code"
    )
    discount_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="PERCENTAGE or FIXED_AMOUNT"
    )
    discount_value: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="% or $ amount as string"
    )
    min_order_amount: Mapped[str | None] = mapped_column(String(20), nullable=True)
    validity_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    validity_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    total_claim_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    per_user_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    claimed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    used_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="ACTIVE",
        comment="ACTIVE, EXPIRED, DEPLETED",
    )

    __table_args__ = (
        Index("ix_coupons_workspace_status", "workspace_id", "status"),
        Index("ix_coupons_shop_code", "shop_id", "code"),
    )

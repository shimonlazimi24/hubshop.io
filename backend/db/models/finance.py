import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.models.base import Base, TimestampMixin, UUIDMixin


class Settlement(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "settlements"

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
    platform_settlement_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    amount: Mapped[str] = mapped_column(String(20), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    detail_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Phase B1: enhanced settlement fields
    net_sales: Mapped[str | None] = mapped_column(String(20), nullable=True)
    shipping_total: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fees_total: Mapped[str | None] = mapped_column(String(20), nullable=True)
    adjustments_total: Mapped[str | None] = mapped_column(String(20), nullable=True)
    payout_amount: Mapped[str | None] = mapped_column(String(20), nullable=True)
    settlement_tier: Mapped[str | None] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        Index("ix_settlements_workspace_status", "workspace_id", "status"),
    )


class Transaction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "transactions"

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
    platform_transaction_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    transaction_type: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="ORDER_PAYMENT, REFUND, COMMISSION, etc."
    )
    amount: Mapped[str] = mapped_column(String(20), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    order_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    detail_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Phase B2: enhanced transaction fields
    fee_breakdown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    net_amount: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sku_id: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Payment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "payments"

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
    platform_payment_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    amount: Mapped[str] = mapped_column(String(20), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    detail_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class Withdrawal(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "withdrawals"

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
    platform_withdrawal_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    amount: Mapped[str] = mapped_column(String(20), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    requested_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    detail_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

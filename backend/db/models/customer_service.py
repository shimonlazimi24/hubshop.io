import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.models.base import Base, TimestampMixin, UUIDMixin


class CsPerformanceSnapshot(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "cs_performance_snapshots"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
    )
    shop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shops.id"),
        nullable=False,
    )
    date: Mapped[date | None] = mapped_column(Date, nullable=True)
    response_rate_24h: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resolution_rate: Mapped[str | None] = mapped_column(String(50), nullable=True)
    satisfaction_score: Mapped[str | None] = mapped_column(String(50), nullable=True)
    total_conversations: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_response_time_seconds: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

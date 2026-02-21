import enum
import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.models.base import Base, TimestampMixin, UUIDMixin


class SocialProvider(str, enum.Enum):
    TIKTOK = "tiktok"
    GOOGLE = "google"


class SocialIdentity(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "social_identities"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Social login provider: tiktok or google",
    )
    provider_user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="User ID from the social provider",
    )
    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Email from the social provider",
    )
    display_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Display name from the social provider",
    )
    avatar_url: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
        comment="Avatar URL from the social provider",
    )

    user: Mapped["User"] = relationship(back_populates="social_identities")  # noqa: F821

    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_social_provider_user"),
    )

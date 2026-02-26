import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.models.base import Base, TimestampMixin, UUIDMixin


class Platform(str, enum.Enum):
    SHOP = "shop"
    DEVELOPER = "developer"
    MARKETING = "marketing"
    LIVE = "live"
    RESEARCH = "research"


class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    ERROR = "error"
    DISCONNECTED = "disconnected"
    REFRESHING = "refreshing"


class SyncJobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ConnectedAccount(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "connected_accounts"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform: Mapped[Platform] = mapped_column(
        Enum(Platform, name="platform_enum"),
        nullable=False,
    )
    platform_account_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="The account ID on the TikTok platform (e.g., seller_id, advertiser_id)",
    )
    platform_account_name: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus, name="account_status_enum"),
        nullable=False,
        default=AccountStatus.ACTIVE,
    )
    identity_group_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="UUID grouping linked accounts across platforms for the same TikTok identity",
    )
    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Platform-specific metadata (e.g., shop_cipher list for Shop, scopes for Developer)",
    )

    workspace: Mapped["Workspace"] = relationship(
        back_populates="connected_accounts"
    )  # noqa: F821
    token_vault: Mapped["TokenVault | None"] = relationship(
        back_populates="connected_account",
        uselist=False,
        lazy="noload",
    )


class TokenVault(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "token_vault"

    connected_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("connected_accounts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    encrypted_access_token: Mapped[str] = mapped_column(Text, nullable=False)
    encrypted_refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    access_token_expires_at: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="ISO 8601 datetime of access token expiry",
    )
    refresh_token_expires_at: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="ISO 8601 datetime of refresh token expiry",
    )
    scopes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Comma-separated list of granted scopes",
    )

    connected_account: Mapped["ConnectedAccount"] = relationship(
        back_populates="token_vault",
    )


class PlatformAppCredential(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "platform_app_credentials"

    platform: Mapped[Platform] = mapped_column(
        Enum(Platform, name="platform_enum", create_type=False),
        unique=True,
        nullable=False,
    )
    app_id: Mapped[str] = mapped_column(String(255), nullable=False)
    encrypted_app_secret: Mapped[str] = mapped_column(Text, nullable=False)
    redirect_uri: Mapped[str] = mapped_column(String(512), nullable=False)
    extra_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class SyncJob(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sync_jobs"

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
        index=True,
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    sync_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of sync: orders, products, campaigns, videos, etc.",
    )
    status: Mapped[SyncJobStatus] = mapped_column(
        Enum(SyncJobStatus, name="sync_job_status_enum"),
        nullable=False,
        default=SyncJobStatus.PENDING,
    )
    items_synced: Mapped[int] = mapped_column(Integer, default=0)
    items_total: Mapped[int | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __init__(self, **kwargs: object) -> None:
        if "items_synced" not in kwargs:
            kwargs["items_synced"] = 0
        super().__init__(**kwargs)

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.models.base import Base, TimestampMixin, UUIDMixin

# --- Enums ---


class MessageDirection(str, enum.Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class ConversationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class AutoMessageType(str, enum.Enum):
    WELCOME = "WELCOME"
    SUGGESTED_QUESTION = "SUGGESTED_QUESTION"
    CHAT_PROMPT = "CHAT_PROMPT"


# --- Models ---


class Conversation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "conversations"

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
    tiktok_conversation_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="TikTok platform conversation ID",
    )
    participant_user_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="TikTok user ID of the conversation participant",
    )
    participant_display_name: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Display name of the conversation participant",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=ConversationStatus.ACTIVE.value,
        comment="ACTIVE or ARCHIVED",
    )
    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of the most recent message",
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", lazy="noload"
    )

    __table_args__ = (
        Index(
            "ix_conversations_workspace_status",
            "workspace_id",
            "status",
        ),
    )


class Message(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tiktok_message_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="TikTok platform message ID",
    )
    direction: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="INBOUND or OUTBOUND",
    )
    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Text content of the message",
    )
    media_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
        comment="URL of attached media (image, video, etc.)",
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the message was sent on TikTok",
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")

    __table_args__ = (
        Index(
            "ix_messages_conversation_sent_at",
            "conversation_id",
            "sent_at",
        ),
    )


class AutoMessage(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "auto_messages"

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
    tiktok_auto_message_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        comment="TikTok platform auto-message ID",
    )
    message_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="WELCOME, SUGGESTED_QUESTION, or CHAT_PROMPT",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Auto-message text content",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether the auto-message is currently enabled",
    )

    __table_args__ = (
        Index(
            "ix_auto_messages_workspace_type",
            "workspace_id",
            "message_type",
        ),
    )

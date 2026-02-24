import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.models.base import Base, TimestampMixin, UUIDMixin

# --- Enums ---


class MentionType(str, enum.Enum):
    POST = "POST"
    COMMENT = "COMMENT"


# --- Models ---


class BrandMention(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "brand_mentions"

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
    tiktok_post_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="TikTok post ID where the brand was mentioned",
    )
    mention_type: Mapped[MentionType] = mapped_column(
        String(50),
        nullable=False,
        comment="POST or COMMENT",
    )
    author_username: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="TikTok username of the mention author",
    )
    content_snippet: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Truncated text of the post or comment",
    )
    engagement_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total engagement (likes + comments + shares)",
    )
    mentioned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="When the mention occurred on TikTok",
    )
    metadata_: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Extra metadata from the TikTok API",
    )


class MentionKeyword(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "mention_keywords"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    keyword: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Keyword or hashtag to monitor",
    )
    is_hashtag: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="True if this keyword is a hashtag",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether this keyword is actively being monitored",
    )

    __table_args__ = (
        Index(
            "ix_mention_keywords_workspace_keyword",
            "workspace_id",
            "keyword",
            unique=True,
        ),
    )


class OrganicComment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "organic_comments"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tiktok_comment_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="Unique TikTok comment ID",
    )
    tiktok_post_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="TikTok post ID this comment belongs to",
    )
    author_username: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="TikTok username of the comment author",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Full comment text",
    )
    like_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    reply_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    is_hidden: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether the comment is hidden",
    )
    commented_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="When the comment was posted on TikTok",
    )

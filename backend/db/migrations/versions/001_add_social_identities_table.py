"""add social_identities table and make user password nullable

Revision ID: 001_social_auth
Revises:
Create Date: 2026-02-21

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_social_auth"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "social_identities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "provider",
            sa.String(50),
            nullable=False,
            comment="Social login provider: tiktok or google",
        ),
        sa.Column(
            "provider_user_id",
            sa.String(255),
            nullable=False,
            comment="User ID from the social provider",
        ),
        sa.Column(
            "email",
            sa.String(255),
            nullable=True,
            comment="Email from the social provider",
        ),
        sa.Column(
            "display_name",
            sa.String(255),
            nullable=True,
            comment="Display name from the social provider",
        ),
        sa.Column(
            "avatar_url",
            sa.String(1024),
            nullable=True,
            comment="Avatar URL from the social provider",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "provider", "provider_user_id", name="uq_social_provider_user"
        ),
    )

    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(255),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(255),
        nullable=False,
    )
    op.drop_table("social_identities")

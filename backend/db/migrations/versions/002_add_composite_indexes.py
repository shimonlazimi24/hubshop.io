"""add composite indexes for query performance

Revision ID: 002_composite_indexes
Revises: 001_social_auth
Create Date: 2026-03-29

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_composite_indexes"
down_revision: str | None = "001_social_auth"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- Ad-account-scoped lookups (campaigns/ad_groups/ads filtered by account) ---
    op.create_index(
        "ix_campaigns_ad_account_status",
        "campaigns",
        ["ad_account_id", "operation_status"],
    )
    op.create_index(
        "ix_ad_groups_ad_account_status",
        "ad_groups",
        ["ad_account_id", "operation_status"],
    )
    op.create_index(
        "ix_ads_ad_account_status",
        "ads",
        ["ad_account_id", "operation_status"],
    )

    # --- Workspace + created_at for time-range queries ---
    op.create_index(
        "ix_campaigns_workspace_created",
        "campaigns",
        ["workspace_id", "created_at"],
    )
    op.create_index(
        "ix_ad_groups_workspace_created",
        "ad_groups",
        ["workspace_id", "created_at"],
    )
    op.create_index(
        "ix_ads_workspace_created",
        "ads",
        ["workspace_id", "created_at"],
    )
    op.create_index(
        "ix_videos_workspace_created",
        "videos",
        ["workspace_id", "created_at"],
    )
    op.create_index(
        "ix_products_workspace_created",
        "products",
        ["workspace_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_products_workspace_created", table_name="products")
    op.drop_index("ix_videos_workspace_created", table_name="videos")
    op.drop_index("ix_ads_workspace_created", table_name="ads")
    op.drop_index("ix_ad_groups_workspace_created", table_name="ad_groups")
    op.drop_index("ix_campaigns_workspace_created", table_name="campaigns")
    op.drop_index("ix_ads_ad_account_status", table_name="ads")
    op.drop_index("ix_ad_groups_ad_account_status", table_name="ad_groups")
    op.drop_index("ix_campaigns_ad_account_status", table_name="campaigns")

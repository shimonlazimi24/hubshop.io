-- Shops: raw TikTok GetAuthorizedShops row snapshot for debugging.
ALTER TABLE shops ADD COLUMN IF NOT EXISTS discovery_snapshot_json JSONB;

-- One connected_account per TikTok seller identity per workspace + platform.
CREATE UNIQUE INDEX IF NOT EXISTS uq_connected_accounts_workspace_platform_account
ON connected_accounts (workspace_id, platform, platform_account_id);

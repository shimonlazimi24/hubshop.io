# TikTok Shop — staging validation checklist

Use this after deploying the Shop vertical slice (OAuth → vault → discovery → optional **products/orders read sync**) to staging. Scope excludes Ads/content/analytics/mutations beyond enqueue sync jobs.

## Recommended staging sequence (commands)

Use **`DATABASE_URL`** for all CLI steps (Supabase pooler or direct is fine for read-only checks). If only a migration URL is available locally, **`DATABASE_MIGRATION_URL`** is accepted by `db:check` and validation scripts as a fallback — **`DATABASE_URL`** is still required for API/worker at runtime.

| Step | Command / action |
|------|------------------|
| 1 | `pnpm db:check` |
| 2 | `pnpm db:migrate` |
| 3 | `pnpm build` |
| 4 | `pnpm test` |
| 5 | `pnpm lint` |
| 6 | Start API, worker, web with valid env (including **`DATABASE_URL`**) |
| 7 | Complete **Shop Connect** for the target workspace |
| 8 | `DATABASE_URL=… pnpm validate:shop-connect -- --workspace "<uuid>"` |
| 9 | Run **Sync products** / **Sync orders** (or POST commerce endpoints) |
| 10 | `DATABASE_URL=… pnpm validate:shop-commerce -- --workspace "<uuid>" --shop "<shops.id>"` |

Supabase/Railway connection strings: **`docs/v2/ENVIRONMENT.md`**. Multi-service Railway layout: **`docs/v2/RAILWAY_DEPLOYMENT.md`**. Cutover-oriented checklist: **`docs/v2/CUTOVER_RUNBOOK.md`**.

## TikTok Partner app settings

- App type supports **TikTok Shop** authorization (Partner Center).
- **OAuth redirect URI** registered exactly as deployed (scheme, host, path, no trailing slash unless intentional):

  `https://<your-api-host>/api/connect/shop/callback`

  Local development typically uses the API host from `apps/api` (e.g. `http://localhost:8001`):

  `http://localhost:8001/api/connect/shop/callback`

- Required credentials available in Partner Center: **App key**, **App secret**, **Service ID** (authorize URL).
- Scopes / capabilities match what Shop Open API needs for **Get Authorized Shops**, **product search/list**, and **order search** (read-only paths used by workers — verify Partner Center for your app version).

## Environment variables

### API (`apps/api`)

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Postgres for Drizzle |
| `JWT_SECRET` or `SHOP_OAUTH_STATE_SECRET` | HMAC for OAuth `state` |
| `TOKEN_ENCRYPTION_KEY` | AES-GCM vault for Shop tokens |
| `TIKTOK_SHOP_APP_KEY` | Partner app key |
| `TIKTOK_SHOP_APP_SECRET` | Partner app secret |
| `TIKTOK_SHOP_SERVICE_ID` | Authorize URL `service_id` |
| `TIKTOK_SHOP_REDIRECT_URI` | Must match Partner redirect URI exactly |
| `TIKTOK_SHOP_AUTH_BASE` | Optional; default TikTok authorize base |
| `TIKTOK_TOKEN_URL` | Optional; default token exchange URL |
| `PUBLIC_WEB_ORIGIN` | SPA origin for post-OAuth redirect (`/connect/shop/result`) |
| `AWS_REGION`, `SQS_QUEUE_URL` | Job enqueue (required unless dev skip flags) |

### Worker (`apps/worker`)

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Same DB as API |
| `TOKEN_ENCRYPTION_KEY` | Decrypt vault access token |
| `TIKTOK_SHOP_APP_KEY`, `TIKTOK_SHOP_APP_SECRET` | Signed Open API requests |
| `TIKTOK_OPEN_API_BASE` | Optional; default global Shop Open API base |
| Redis URL (if used) | Optional pub/sub; publish failures are non-fatal |

## Automated validation (recommended)

After a successful OAuth + discovery run, validate DB state for a workspace:

```bash
DATABASE_URL="$DATABASE_URL" pnpm validate:shop-connect -- --workspace "<workspace-uuid>"
```

- Exit code **0** = all checks passed; **1** = one or more checks failed; **2** = usage/config error (e.g. missing `DATABASE_URL`).
- The script never prints vault ciphertext or access tokens; it only checks **envelope shape** (base64 JSON with `ciphertext` / `iv` / `authTag`) and row presence.

### Internal HTTP snapshot (optional)

When the API is running:

- **Non-production** (`APP_ENV` ≠ `production`):  
  `GET /api/internal/debug/shop-connect-status?workspaceId=<uuid>` — no auth header required.
- **Production**: same path **only** if `INTERNAL_CRON_SECRET` is set **and** the request includes header `X-Cron-Secret: <same secret>`. If the secret is not configured in prod, the route responds **404** (hidden). Wrong/missing secret → **401**.

Response is JSON only: `summary`, `checks[]`, `meta` (IDs, counts, job status). No tokens or encrypted blobs.

### Commerce validation (products + orders)

After running **Sync products** / **Sync orders** from the UI (or calling the commerce POST endpoints), validate DB rows and latest sync jobs for a specific Frodo shop row (`shops.id` UUID from `/api/connect/shop/status` or SQL):

```bash
DATABASE_URL="$DATABASE_URL" pnpm validate:shop-commerce -- \
  --workspace "<workspace-uuid>" \
  --shop "<shops.id uuid>"
```

- Exit codes match `validate:shop-connect` (**0** pass / **1** fail / **2** usage).
- Checks include: no **failed** product/order sync jobs; row counts (informational); `api_snapshot_json` present on all rows when rows exist.
- Run both sync buttons (or POST endpoints) before expecting non-zero counts — empty product/order lists can still be valid if TikTok returns no data.

## Local test steps

1. Run Postgres + apply migrations; set all API/worker env vars (see `docs/v2/ENVIRONMENT.md`).
2. Start API and worker; ensure SQS queue exists and `SQS_QUEUE_URL` points to it (or use documented dev skip only for local experiments).
3. Log into the web app, select workspace, open **Connect TikTok Shop**, complete Partner login.
4. Confirm browser lands on `{PUBLIC_WEB_ORIGIN}/connect/shop/result?status=connected`.
5. Watch worker logs for redacted `authorized_shops` payload (no raw access tokens).
6. Run `pnpm validate:shop-connect -- --workspace "<uuid>"` or query DB manually (SQL below).

## Staging test steps

1. Deploy API + worker with staging Partner app + redirect URI **exactly** matching staging API URL + `/api/connect/shop/callback`.
2. Set `PUBLIC_WEB_ORIGIN` to staging web origin.
3. Run through OAuth once per workspace/seller you care about.
4. Verify worker processes job once per connect (dedupe key `shop_discovery:<connected_account_id>`).
5. Confirm shops appear via authenticated status API or DB.

### Phase C — products / orders sync (minimal)

1. Open **Shops** (`/shops`), pick a linked shop → **Shop detail** (`/shops/:shopId`).
2. Click **Sync products**, wait for worker; refresh — products tab should fill; **Products sync** line should show `completed`.
3. Click **Sync orders** — same for orders tab (may stay empty if no orders in the TikTok time window).
4. Worker logs: `shop_api post request` / `shop_api post ok` with **pathname + redacted query only** (never full URLs with tokens).
5. On failure, `sync_jobs.error_message` prefixes with `tiktok_shop_products_sync_failed:` or `tiktok_shop_orders_sync_failed:`.

**API routes** (JWT + `X-Workspace-Id`, Frodo `shops.id` in path):

- `POST /api/commerce/shops/:shopId/sync-products`
- `POST /api/commerce/shops/:shopId/sync-orders`
- `GET /api/commerce/shops/:shopId/sync-status`
- `GET /api/commerce/shops/:shopId/products`
- `GET /api/commerce/shops/:shopId/orders`

**SQS jobs**: `sync_shop_products` / `sync_shop_orders` include `workspaceId`, `connectedAccountId`, `shopId` (internal UUID), `dedupeKey` (hourly bucket via SHA-256), optional `cursor` / `createTimeGe` / `createTimeLe` for orders.

**Failure modes (commerce)**

| Symptom | Likely cause |
|---------|----------------|
| HTTP 404 on commerce routes | Shop UUID wrong or shop not in workspace. |
| `tiktok_shop_products_sync_failed` / HTTP path errors | TikTok changed API path/version (`TIKTOK_SHOP_PRODUCT_SEARCH_PATH` / order path in `@frodo/domain`); wrong `shop_cipher`; missing product scope. |
| Empty product list but job completed | Seller has zero products; or API returned alternate list field — check `api_snapshot_json` / logs. |
| Orders empty | No orders in default **90-day** window; widen window later via job payload if needed. |
| Dedupe skip every hour | Same workspace/shop/kind enqueued within the same UTC hour — intentional idempotency. |

## Expected logs

**API**

- After successful token exchange: `Shop token exchange ok` with **redacted** JSON (no access/refresh tokens or secrets in clear text).
- On state failure: debug line with state length only (no raw state logged).
- On SQS failure after persist: error with redacted cause; connected account row rolled back (vault cascades).

**Worker**

- `shop_api authorized_shops request` — pathname + **redacted** query (`access_token`, `sign` → `[redacted]`).
- `shop_discovery authorized_shops redacted=...` — redacted response snapshot.
- Dedupe skip: `Shop discovery dedupe skip shop_discovery:...`
- Redis publish failure: `redis publish failed (non-fatal)` with redacted detail.
- Commerce: `shop_api post request` / `shop_api post ok` with redacted JSON bodies (no access tokens in query logs).

### Successful end-to-end pattern (what “good” looks like)

1. Browser hits `/connect/shop/result?status=connected`.
2. API logs: `Shop token exchange ok` + redacted payload shape (may show seller-related keys redacted).
3. Worker logs: one run that performs `authorized_shops` (unless dedupe skip on retry); response log line shows `code: 0` and shop list with sensitive fields redacted (e.g. `cipher`).
4. No API log line enqueue rollback after connect (that would indicate `sqs_enqueue_failed`).

## Expected SQS job lifecycle (Shop slice)

1. **Enqueue** (API): After OAuth, API sends one message with type `shop_discovery_after_connect`, including `workspaceId`, `connectedAccountId`, and `dedupeKey` `shop_discovery:<connected_account_id>`.
2. **Consume** (worker): Worker receives message, inserts into `worker_dedupe_keys` (conflict → skip entire handler).
3. **Discovery**: Worker calls TikTok Get Authorized Shops, upserts `shops`, inserts `sync_jobs` row (`sync_type = shop_discovery`, `status = completed`, `items_synced` = shop count).
4. **Dedupe**: A second delivery with the same `dedupeKey` does **not** re-run discovery; logs show `Shop discovery dedupe skip ...`.

If the message never arrives, check API IAM/SQS config and that enqueue did not throw (Shop connect rolls back DB on enqueue failure).

## DB rows to verify

After **successful** OAuth:

- `connected_accounts`: `platform = 'shop'`, `status = 'active'`, `platform_account_id` = TikTok seller identifier from token payload.
- `token_vault`: one row per connected account; `encrypted_access_token` is opaque base64 JSON (not plaintext token).

After **successful** discovery:

- `shops`: rows per authorized shop; `discovery_snapshot_json` populated from TikTok payload.
- `sync_jobs`: row with `sync_type = 'shop_discovery'`, `status = 'completed'`, `items_synced` = shop count.
- `worker_dedupe_keys`: key `shop_discovery:<connected_account_id>` present.

After **failed** discovery:

- `sync_jobs` with `status = 'failed'`, `error_message` prefixed with `tiktok_shop_discovery_failed:`.

## SQL reference (replace `:workspace_id`)

**Latest Shop `connected_account` for workspace**

```sql
SELECT id, workspace_id, platform, platform_account_id, status, updated_at
FROM connected_accounts
WHERE workspace_id = :workspace_id
  AND platform = 'shop'
ORDER BY updated_at DESC
LIMIT 1;
```

**Vault row for that account** (replace `:connected_account_id`)

```sql
SELECT id, connected_account_id,
       length(encrypted_access_token) AS access_blob_len,
       (encrypted_refresh_token IS NOT NULL) AS has_refresh,
       updated_at
FROM token_vault
WHERE connected_account_id = :connected_account_id;
```

**Latest shop discovery job**

```sql
SELECT id, status, sync_type, items_synced, error_message, completed_at, created_at
FROM sync_jobs
WHERE workspace_id = :workspace_id
  AND connected_account_id = :connected_account_id
  AND sync_type = 'shop_discovery'
ORDER BY created_at DESC
LIMIT 1;
```

**Shops for workspace + account**

```sql
SELECT shop_id, shop_name, region,
       (discovery_snapshot_json IS NOT NULL) AS has_snapshot,
       updated_at
FROM shops
WHERE workspace_id = :workspace_id
  AND connected_account_id = :connected_account_id
ORDER BY updated_at DESC;
```

**Worker dedupe key** (bind parameter `shop_discovery:<connected_account_uuid>` as text)

```sql
SELECT dedupe_key, created_at
FROM worker_dedupe_keys
WHERE dedupe_key = $1;
```

**Manual envelope check (optional)** — decoded JSON should contain keys `ciphertext`, `iv`, `authTag` (base64 strings). Do **not** paste production blobs into tickets.

## Stable error codes (OAuth redirect `error=` query param)

These appear as the `error` query parameter on `{PUBLIC_WEB_ORIGIN}/connect/shop/result`. The SPA maps them to short explanations.

| Code | Typical cause |
|------|----------------|
| `missing_params` | Missing `code` or `state` on callback URL |
| `tiktok_state_invalid` | Expired/tampered `state`, or wrong signing secret |
| `tiktok_token_exchange_failed` | HTTP/business error from token endpoint |
| `tiktok_token_missing_seller_identity` | Token JSON missing expected seller / open id fields |
| `sqs_enqueue_failed` | SQS send failed after DB write; account rolled back |

**Worker / discovery (not redirect codes)**

| Code / prefix | Meaning |
|---------------|---------|
| `vault_decrypt_failed` | Worker could not decrypt `token_vault.encrypted_access_token` (usually `TOKEN_ENCRYPTION_KEY` mismatch vs API). |
| `tiktok_shop_discovery_failed:` | Prefix on `sync_jobs.error_message` when TikTok API or handler failed after dedupe claim. |

## Common failure modes

| Symptom | Likely cause |
|---------|----------------|
| Partner shows redirect error / `redirect_uri_mismatch` | `TIKTOK_SHOP_REDIRECT_URI` does not match Partner Center **exactly** (http vs https, path, port). |
| `tiktok_state_invalid` | Clock skew; secret rotation (`JWT_SECRET` / `SHOP_OAUTH_STATE_SECRET`); user took >15m; tampered `state`. |
| `tiktok_token_exchange_failed` | Wrong app key/secret; wrong `TIKTOK_TOKEN_URL`; auth code reused/expired. |
| `tiktok_token_missing_seller_identity` | TikTok response shape changed; sandbox vs prod mismatch; inspect **redacted** success log for shape. |
| Signing error / 401 on Open API | Wrong `TIKTOK_SHOP_APP_SECRET`; wrong `TIKTOK_OPEN_API_BASE`; clock skew on `timestamp`. |
| `sqs_enqueue_failed` | Missing queue URL/region; IAM policy; network from API to AWS. |
| Worker cannot decrypt / `vault_decrypt_failed` | `TOKEN_ENCRYPTION_KEY` differs between API and worker; corrupted vault row. |

## References

- Environment overview: `docs/v2/ENVIRONMENT.md`
- Cutover / operations: `docs/v2/CUTOVER_RUNBOOK.md`

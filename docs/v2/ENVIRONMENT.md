# Frodo v2 — environment variables

Use these in Railway, Docker, or local `.env` for the TypeScript monorepo (`apps/*`, `packages/*`).

**Local dev checklist:** `docs/v2/LOCAL_DEVELOPMENT.md` (includes `apps/api/.env.example`).

Validation is centralized in `@frodo/config` (`loadApiEnv`, `loadWorkerEnv`, `loadSchedulerEnv`). Required keys depend on `APP_ENV` (`development` | `staging` | `production`).

## PostgreSQL URLs (Supabase and others)

Frodo uses **managed PostgreSQL only** from Supabase in this setup: **do not** enable or rely on Supabase Auth, Realtime, or Storage for v2 yet. Use your own JWT (`JWT_SECRET`) and app-layer auth.

| Variable | Used by | Purpose |
|----------|---------|---------|
| **`DATABASE_URL`** | **API, worker** (required at runtime) | Connection string the Node services use for Drizzle `createDb()`. Set this to the URL appropriate for **many short-lived connections** (typically Supabase **pooler / transaction mode** when running serverless or multiple Railway replicas). |
| **`DATABASE_MIGRATION_URL`** | **Drizzle CLI** (`pnpm db:generate`, `pnpm db:studio`), **`pnpm db:migrate`** | Optional. When set, migrations use this URL instead of `DATABASE_URL`. Use when runtime must use the **pooler** but migrations must use a **direct** session (see below). If unset, migrations fall back to `DATABASE_URL`. |

**Rules**

- **Runtime** (`apps/api`, `apps/worker`) must receive **`DATABASE_URL` only** for Postgres — they do not read `DATABASE_MIGRATION_URL`.
- **Migrations** resolve the URL as: `DATABASE_MIGRATION_URL` → else `DATABASE_URL`. If **both** are unset, `pnpm db:migrate` and Drizzle Kit fail with a clear error.
- **`pnpm db:check`** prefers `DATABASE_URL`, then `DATABASE_MIGRATION_URL`, so you can probe connectivity without duplicating values.

### Supabase: create a project

1. In [Supabase](https://supabase.com), create a project and wait until the database is ready.
2. Open **Project Settings → Database**. You will see:
   - **Connection string (URI)** — often labeled for **transaction pooler** (port **6543**, host like `aws-0-…pooler.supabase.com`) vs **direct** (port **5432**, host like `db.<project-ref>.supabase.co`).
3. Use **`sslmode=require`** (or equivalent) in production URLs unless your platform injects SSL another way.

### Direct vs pooler (summary)

- **Direct** (`db.<ref>.supabase.co:5432`): full PostgreSQL session semantics; best for **DDL** and **migrations** when the pooler disallows or complicates them.
- **Pooler / transaction mode** (Supabase **PgBouncer**, port **6543**): ideal for **API and worker** under concurrency; use this for **`DATABASE_URL`** when recommended by Supabase for app servers.

If a single URL works for both app and migrations in your environment, set only **`DATABASE_URL`** and leave **`DATABASE_MIGRATION_URL`** unset.

### Railway

1. Create a **PostgreSQL** service **or** use Supabase externally (recommended for managed backups/upgrades as documented by Supabase).
2. For **API** and **worker** services, set **`DATABASE_URL`** to the runtime connection string (often pooler).
3. Optionally set **`DATABASE_MIGRATION_URL`** on a **one-off** deploy / local shell to the **direct** URI when running `pnpm db:migrate`, **or** run migrations locally against direct Supabase with the same env pair.
4. Never commit secrets; use Railway **Variables** (encrypted).

### Diagnostics

- **`pnpm db:check`** — connects (using `DATABASE_URL` or fallback), prints `current_database()`, `current_user`, server version, presence of core v2 tables, and latest Drizzle migration metadata **without** printing passwords or full connection strings.

## App environment (`APP_ENV`)

| Variable | Services | Purpose |
|----------|----------|---------|
| `APP_ENV` | api, worker, scheduler | `development` \| `staging` \| `production`. Drives which env vars are required (SQS, Redis, async skip). |

## Shared

| Variable | Services | Purpose |
|----------|----------|---------|
| `DATABASE_URL` | **api, worker** (required), `db:check`, validation CLIs (preferred) | PostgreSQL connection for **runtime** and general tooling |
| `DATABASE_MIGRATION_URL` | Drizzle Kit, `pnpm db:migrate`, optional `db:check` / validation fallback | Optional **direct** or migration-friendly URI (see PostgreSQL URLs above) |
| `JWT_SECRET` | api | HS256 signing key for access/refresh JWTs (**required** in validated config) |
| `JWT_ACCESS_EXPIRE_MINUTES` | api | Default `15` |
| `JWT_REFRESH_EXPIRE_DAYS` | api | Default `7` |
| `TOKEN_ENCRYPTION_KEY` | api | Secret for AES-256-GCM token vault (`@frodo/domain`) |
| `PUBLIC_WEB_ORIGIN` | api (CORS) | SPA origin, e.g. `http://localhost:5173` |
| `REDIS_URL` | api, worker | Token blacklist, realtime pub/sub, rate limits; **required in staging/production** when `REQUIRE_REDIS_FOR_AUTH` is true (default on for those envs) |
| `REQUIRE_REDIS_FOR_AUTH` | api | If `true`, API fails startup when Redis is unreachable or `REDIS_URL` is missing. Default: `true` for `staging`/`production`, overridable. |
| `ALLOW_ASYNC_SKIP` | api | **Development only.** When `true`, enqueue may fail with 503 if SQS is unset (no silent DB writes without jobs). **Rejected** for `staging`/`production`. |

## AWS SQS

| Variable | Services | Purpose |
|----------|----------|---------|
| `AWS_REGION` | api, worker | e.g. `us-east-1` (**required** with `SQS_QUEUE_URL` in staging/production) |
| `AWS_ACCESS_KEY_ID` | api, worker | IAM user or role credentials |
| `AWS_SECRET_ACCESS_KEY` | api, worker | |
| `SQS_QUEUE_URL` | api, worker | Primary Standard queue URL (**required** in staging/production unless local dev with `ALLOW_ASYNC_SKIP=true`) |

## Worker (polling / shutdown)

| Variable | Services | Purpose |
|----------|----------|---------|
| `SQS_VISIBILITY_TIMEOUT_SECONDS` | worker | Optional SQS queue visibility timeout hint |
| `SQS_VISIBILITY_EXTENSION_SECONDS` | worker | If set, worker extends visibility while processing long jobs |
| `WORKER_SHUTDOWN_DRAIN_SECONDS` | worker | Grace period after SIGINT/SIGTERM to finish in-flight work |

## Realtime (SSE)

Browser `EventSource` cannot send `Authorization` headers. Clients must use a stream URL that supports cookies **or** use `fetch` + `ReadableStream` with `Authorization: Bearer`. Tenant streams require **verified workspace membership** (not workspace id alone).

## Scheduler (cron sidecar)

| Variable | Services | Purpose |
|----------|----------|---------|
| `CRON_BASE_URL` | scheduler | API public base URL |
| `INTERNAL_CRON_SECRET` | api, scheduler | Shared secret header `X-Cron-Secret` |

## TikTok Shop (OAuth + signed Open API)

Required on **API** to start Shop OAuth (`GET /api/connect/shop/authorize`). Required on **worker** to run `shop_discovery_after_connect` (same app key/secret as Partner Center).

| Variable | Services | Purpose |
|----------|----------|---------|
| `TIKTOK_SHOP_APP_KEY` | api, worker | Partner Center application **app key** |
| `TIKTOK_SHOP_APP_SECRET` | api, worker | Partner Center **app secret** (never log) |
| `TIKTOK_SHOP_SERVICE_ID` | api | Service / application ID used in authorize URL |
| `TIKTOK_SHOP_REDIRECT_URI` | api | Must exactly match registered redirect, e.g. `http://localhost:8001/api/connect/shop/callback` |
| `TIKTOK_SHOP_AUTH_BASE` | api | Optional authorize host override (default `https://services.tiktokshop.com/open/authorize`; US sellers may use `https://services.us.tiktokshop.com/open/authorize`) |
| `TIKTOK_TOKEN_URL` | api | Token exchange GET base (default `https://auth.tiktok-shops.com/api/v2/token/get`) |
| `TIKTOK_OPEN_API_BASE` | worker | Signed API host (default `https://open-api.tiktokglobalshop.com`) |
| `SHOP_OAUTH_STATE_SECRET` | api | Optional separate HMAC secret for OAuth `state`; defaults to `JWT_SECRET` |

`TOKEN_ENCRYPTION_KEY` must be set on the API before storing Shop tokens (same key on worker to decrypt for discovery).

### TikTok Shop webhooks (`POST /api/webhooks/shop`)

Verification follows [TikTok webhook signature docs](https://developers.tiktok.com/doc/webhooks-verification): header **`TikTok-Signature`** with value `t=<unix_seconds>,s=<hex_hmac>` where HMAC-SHA256 is computed over **`${t}.${exact_raw_json_body}`** using the **same app secret** as Partner Center (**`TIKTOK_SHOP_APP_SECRET`**).

| Variable | Services | Purpose |
|----------|----------|---------|
| `TIKTOK_SHOP_APP_SECRET` | api | **Required** for signature verification in staging/production (same value as OAuth/Open API). Boot fails if missing when `APP_ENV` is `staging` or `production`. |
| `TIKTOK_WEBHOOK_MAX_SKEW_SECONDS` | api | Optional replay window for `t` vs server time (default **300**). |
| `ALLOW_UNVERIFIED_WEBHOOKS` | api | **Development only.** If `true` and `APP_ENV=development`, skips signature verification (local tooling only). **Forbidden** for staging/production. |

The API captures **raw POST bytes** for `/api/webhooks/*` in Express `verify` so the signature matches TikTok’s payload exactly.

See also: `docs/v2/CUTOVER_RUNBOOK.md` (redirect URI checklist).

## Railway deployment

Step-by-step services, build/start commands, health checks, SQS IAM, and staging order: **`docs/v2/RAILWAY_DEPLOYMENT.md`**.

## Commerce probe (integration tests)

| Variable | Services | Purpose |
|----------|----------|---------|
| `TIKTOK_COMMERCE_PROBE_URL` | worker | If set, `fetchWithRetry` hits this URL during sync jobs (contract testing) |

## Web (Vite)

| Variable | Services | Purpose |
|----------|----------|---------|
| `VITE_API_URL` | web | Empty string uses dev proxy; in prod set to `https://api.example.com` |
| `VITE_API_PROXY` | web (dev) | Target for `vite.config` proxy (default `http://localhost:8001`) |
| `PORT` | web (`pnpm start`) | Railway preview: `vite preview` listens on `PORT` (default `4173` locally) |

Production hosting often uses a static CDN (see **`docs/v2/RAILWAY_DEPLOYMENT.md`**) instead of `vite preview`.

## Staging deploy checklist

1. Configure **`DATABASE_URL`** (and optionally **`DATABASE_MIGRATION_URL`**) per **PostgreSQL URLs** above. Run Alembic migrations on PostgreSQL (legacy) if applicable, then `pnpm --filter @frodo/db build && pnpm db:check && pnpm db:migrate` for v2 additive tables.
2. Create SQS queue + DLQ; attach IAM policy for `SendMessage` / `ReceiveMessage` / `DeleteMessage`.
3. Set `PORT` for API if platform requires it (Railway injects `PORT`).

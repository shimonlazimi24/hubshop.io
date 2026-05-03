# Frodo v2 — Railway deployment (staging / production)

Deploy the TypeScript monorepo **without** Railway’s Postgres plugin: database is **Supabase** (or any external Postgres). Redis is **optional** but recommended for staging/production JWT blacklist unless you explicitly disable `REQUIRE_REDIS_FOR_AUTH`.

**Async jobs (canonical plan):** per **[ADR-001](./ADR-001-frodo-v2-stack.md)**, durable work flows through **AWS SQS** — the **API enqueues**, the **`apps/worker` service polls** the same **`SQS_QUEUE_URL`**. **Staging and production must set `AWS_REGION`, `SQS_QUEUE_URL`, and IAM credentials** on both API and worker. Redis is **not** the job broker. **`ALLOW_ASYNC_SKIP`** exists **only** for local `APP_ENV=development` and must stay **off** in Railway.

See **`ENVIRONMENT.md`** for variable semantics (`DATABASE_URL` vs `DATABASE_MIGRATION_URL`, TikTok, SQS IAM, etc.).

**Config-as-code:** copy-ready **`railway.toml`** files live under **`infra/railway/`** (`api`, `web`, `worker`). See **`infra/railway/README.md`** for wiring each Railway service (Config file path, root directory `.`, deleting legacy Python Docker services).

The legacy Python stack is **`Dockerfile.legacy`** (used only by root **`docker compose`**). There is **no** root `Dockerfile`, so Railway defaults to **Railpack** instead of building the wrong image.

---

## 1. Railway services (recommended layout)

| Service | Purpose | Public HTTP |
|---------|---------|-------------|
| **frodo-api** | NestJS API | Yes (custom domain) |
| **frodo-worker** | SQS consumer loop | **No** |
| **frodo-web** | Static SPA (`vite preview` on Railway) | Yes (custom domain) |

**Cron:** use **Railway Cron** → `POST /api/internal/cron/tick` with `X-Cron-Secret` (see §7). Do **not** add a separate **`frodo-scheduler`** service unless you explicitly want `apps/scheduler` as a one-shot container.

**Do not** add Railway **PostgreSQL**. Use Supabase connection strings as **`DATABASE_URL`** on API + worker.

**Redis:** Optional Railway **Redis** plugin (or Upstash) only if you need **`REDIS_URL`** for logout blacklist / auth (`REQUIRE_REDIS_FOR_AUTH` defaults on for `staging`/`production`). If you omit Redis, set **`REQUIRE_REDIS_FOR_AUTH=false`** only if you accept the trade-offs documented in `ENVIRONMENT.md`.

---

## 2. Monorepo basics on Railway

For every Node service, Railway should:

- **Root directory:** repository root (`.`).
- Use **pnpm** (declared in root `package.json` → `packageManager`).
- Run commands **from the repo root** so workspace packages resolve.

Suggested **install** (all Node services):

```bash
pnpm install --frozen-lockfile
```

---

## 3. Service configuration table

| Setting | API | Worker | Web | Scheduler |
|---------|-----|--------|-----|-----------|
| **Install command** | `pnpm install --frozen-lockfile` | same | same | same |
| **Build command** | See §4 | See §5 | See §6 | See §7 |
| **Start command** | See §4 | See §5 | See §6 | See §7 |
| **Health check path** | `/api/health` | — | `/` or omit | — |

---

## 4. API service (`frodo-api`)

### Build command (minimal deps)

From repo root:

```bash
pnpm install --frozen-lockfile && pnpm --filter @frodo/contracts build && pnpm --filter @frodo/config build && pnpm --filter @frodo/db build && pnpm --filter @frodo/domain build && pnpm --filter @frodo/api build
```

(Full root `pnpm build` also works but builds worker/web/scheduler too.)

### Start command

Railway sets **`PORT`** — Nest reads `process.env.PORT` in `main.ts`.

```bash
pnpm --filter @frodo/api start
```

(equivalent to `node dist/main.js` in `apps/api` with workspace `node_modules`.)

### Health check

- **HTTP GET** `https://<api-host>/api/health`
- Expected JSON includes `"ok":true` and `"service":"frodo-api"`.

### Domains & CORS

- Attach a **public domain** on the API service (e.g. `api.staging.example.com`).
- Set **`PUBLIC_WEB_ORIGIN`** to the **exact** browser origin of the SPA (scheme + host + port), e.g. `https://app.staging.example.com` — Nest CORS allows only this origin.

### Required env vars (typical staging)

| Variable | Notes |
|----------|--------|
| `APP_ENV` | `staging` or `production` |
| `DATABASE_URL` | Supabase **runtime** URI (often pooler `:6543`) |
| `JWT_SECRET` | ≥ 16 chars |
| `AWS_REGION` | e.g. `us-east-1` |
| `SQS_QUEUE_URL` | Main queue URL |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | IAM user or OIDC per Railway/AWS docs |
| `TOKEN_ENCRYPTION_KEY` | Shop vault + worker decrypt |
| `INTERNAL_CRON_SECRET` | **Required** for `/api/internal/cron/tick` — same value as scheduler/cron job |
| `REDIS_URL` | Recommended default for staging/prod auth blacklist |

Plus TikTok Shop vars if using Shop Connect: **`TIKTOK_SHOP_APP_KEY`**, **`TIKTOK_SHOP_APP_SECRET`** (required in staging/prod on API — also used for **`POST /api/webhooks/shop`** signature verification), **`TIKTOK_SHOP_SERVICE_ID`**, **`TIKTOK_SHOP_REDIRECT_URI`**, **`TOKEN_ENCRYPTION_KEY`**; worker **`TIKTOK_OPEN_API_BASE`** as needed.

**Never** set `DATABASE_MIGRATION_URL` on the API — migrations-only.

---

## 5. Worker service (`frodo-worker`)

### Build command

```bash
pnpm install --frozen-lockfile && pnpm --filter @frodo/contracts build && pnpm --filter @frodo/config build && pnpm --filter @frodo/db build && pnpm --filter @frodo/domain build && pnpm --filter @frodo/worker build
```

### Start command

```bash
pnpm --filter @frodo/worker start
```

No HTTP server — **do not** expose a public domain.

### Required env vars

| Variable | Notes |
|----------|--------|
| `APP_ENV` | Match API |
| `DATABASE_URL` | Same logical DB as API |
| `AWS_REGION`, `SQS_QUEUE_URL` | Same queue as API |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | **ReceiveMessage**, **DeleteMessage**, **ChangeMessageVisibility** |
| `TOKEN_ENCRYPTION_KEY` | Same as API |
| `TIKTOK_SHOP_APP_KEY`, `TIKTOK_SHOP_APP_SECRET`, `TIKTOK_OPEN_API_BASE` | Shop discovery / commerce sync |

Optional: `REDIS_URL` for commerce pub/sub (failures are non-fatal if absent).

### SQS IAM (worker)

Worker polling requires **`sqs:ReceiveMessage`**, **`sqs:DeleteMessage`**, **`sqs:ChangeMessageVisibility`**. Optionally **`sqs:GetQueueAttributes`** for tuning/monitoring.

API user policy covers **`sqs:SendMessage`**; worker policy must include receive/delete.

### Logging & graceful shutdown

- Worker handles **SIGINT** / **SIGTERM**: stops the poll loop and drains in-flight receives according to SQS visibility.
- Log **message fingerprints** / job types — never log tokens or raw TikTok signed URLs.
- Configure Railway **restart policy**; pair queue with **DLQ** for poison messages.

---

## 6. Web service (`frodo-web`)

### Build command

Build-time embed of API URL:

```bash
pnpm install --frozen-lockfile && VITE_API_URL=https://api.staging.example.com pnpm --filter @frodo/web build
```

Replace with your real API origin (**no** trailing slash needed if your client uses paths like `/api/...` consistently — current client uses `prefix + '/api/...'` patterns; set `VITE_API_URL` to the API origin only, e.g. `https://api.staging.example.com`).

### Hosting options

**A — Railway “static” / Node preview (simple)**  

Serve built assets with:

```bash
pnpm --filter @frodo/web start
```

(`start` runs `vite preview` bound to **`0.0.0.0`** and **`PORT`**.) Suitable for staging.

**B — Cloudflare Pages / Netlify (recommended for prod SPA)**

- Build command: same as above (without Railway-specific start).
- Publish directory: `apps/web/dist`.
- Configure SPA fallback: all routes → `index.html` (e.g. Cloudflare `_redirects` or Netlify redirects).

### Env vars

| Variable | When |
|----------|------|
| `VITE_API_URL` | **Required** in prod/staging static build — full API origin |
| `PORT` | Railway preview server only |

---

## 7. Scheduler / cron

### Option A — Railway **Cron** → API (fewer moving parts)

- Schedule: e.g. every 5–15 minutes.
- **HTTP POST** `https://<api-host>/api/internal/cron/tick`
- Header: **`X-Cron-Secret: <INTERNAL_CRON_SECRET>`**
- API must have **`INTERNAL_CRON_SECRET`** set (same string).

Success response shape includes `enqueued: "token_refresh_tick"`. API logs debug line from `SqsService` when enqueue succeeds.

### Option B — **`frodo-scheduler` service** (apps/scheduler)

Runs one HTTP POST then exits (good for Railway “run once” or cron job type).

**Build:**

```bash
pnpm install --frozen-lockfile && pnpm --filter @frodo/config build && pnpm --filter @frodo/scheduler build
```

**Start:**

```bash
pnpm --filter @frodo/scheduler start
```

**Env:**

| Variable | Purpose |
|----------|---------|
| `CRON_BASE_URL` | Public API base **without** trailing slash, e.g. `https://api.staging.example.com` |
| `INTERNAL_CRON_SECRET` | Same as API |

### Verify ticks enqueue SQS

1. Call tick (cron or manual `curl` with header).
2. API logs: `Enqueued token_refresh_tick` (debug) or 503 if SQS misconfigured.
3. Worker logs show processing (or temporarily inspect queue depth / DLQ in AWS).

---

## 8. Supabase

| Where | Variable |
|-------|----------|
| **API + Worker** (Railway services) | **`DATABASE_URL`** = runtime connection (often **pooler**) |
| **Local / CI / one-off migrate** | **`DATABASE_MIGRATION_URL`** = optional **direct** `:5432` if pooler blocks DDL; else omit |

**Never** commit secrets.

### `pnpm db:check`

From dev machine or CI (with network to Supabase):

```bash
export DATABASE_URL='postgresql://...'   # or DATABASE_MIGRATION_URL as fallback
pnpm install --frozen-lockfile && pnpm --filter @frodo/db build && pnpm db:check
```

### `pnpm db:migrate`

```bash
export DATABASE_URL='postgresql://...'
# optional: export DATABASE_MIGRATION_URL='postgresql://...@db.<ref>.supabase.co:5432/...'
pnpm install --frozen-lockfile && pnpm --filter @frodo/db build && pnpm db:migrate
```

Run migrations **before** or **after** first deploy as long as API/worker start only once schema is applied.

---

## 9. SQS

### AWS env vars (API + worker)

- `AWS_REGION`
- `SQS_QUEUE_URL` (primary queue)
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (or instance role if Railway supports it)

### Minimum IAM actions

Policy example (split across **producer** vs **consumer** users if you prefer least privilege):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage",
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:ChangeMessageVisibility",
        "sqs:GetQueueAttributes"
      ],
      "Resource": "arn:aws:sqs:<region>:<account-id>:<queue-name>"
    }
  ]
}
```

- **API** needs at least **`sqs:SendMessage`** (plus **`GetQueueAttributes`** if you use tooling).
- **Worker** needs **`ReceiveMessage`**, **`DeleteMessage`**, **`ChangeMessageVisibility`**.

### DLQ

Create a **dead-letter queue**, set redrive policy on the **main** queue (max receives), monitor DLQ depth in staging before production.

---

## 10. Staging validation order

Execute in this order after Supabase + AWS exist:

1. **`pnpm db:check`** — connectivity + core tables + migration metadata (no secrets printed).
2. **`pnpm db:migrate`** — apply Drizzle migrations.
3. **Deploy** API → worker → web (scheduler/cron last).
4. **Health:** `GET /api/health` on API public URL.
5. **Shop Connect** — full OAuth once for a test workspace.
6. **`pnpm validate:shop-connect -- --workspace "<uuid>"`**
7. **Products / orders sync** (UI or commerce POST endpoints).
8. **`pnpm validate:shop-commerce -- --workspace "<uuid>" --shop "<shops.id>"`**

Detailed TikTok steps: **`TIKTOK_SHOP_STAGING_VALIDATION.md`**.

---

## Env var matrix (quick reference)

| Variable | API | Worker | Web build | Scheduler / Cron |
|----------|:---:|:------:|:---------:|:----------------:|
| `DATABASE_URL` | ✅ | ✅ | — | — |
| `DATABASE_MIGRATION_URL` | ❌ | ❌ | — | — (migrate CLI only) |
| `JWT_SECRET` | ✅ | — | — | — |
| `AWS_REGION`, `SQS_QUEUE_URL` | ✅ | ✅ | — | — |
| `AWS_ACCESS_KEY_ID` / `SECRET` | ✅ send | ✅ recv | — | — |
| `TOKEN_ENCRYPTION_KEY` | ✅ | ✅ | — | — |
| `INTERNAL_CRON_SECRET` | ✅ | — | — | ✅ / cron header |
| `CRON_BASE_URL` | — | — | — | ✅ scheduler service |
| `PUBLIC_WEB_ORIGIN` | ✅ | — | — | — |
| `REDIS_URL` | ✅ recommended | optional | — | — |
| `VITE_API_URL` | — | — | ✅ build-time | — |
| TikTok `TIKTOK_*` | OAuth | Open API | — | — |

---

## Optional: Railway watch paths

To reduce rebuilds, set **watch paths** per service (examples):

- API: `apps/api/**`, `packages/**`
- Worker: `apps/worker/**`, `packages/**`
- Web: `apps/web/**`
- Scheduler: `apps/scheduler/**`, `packages/config/**`

Exact UI labels vary by Railway version; adjust to match your project settings.

# Railway — Frodo v2 (Node monorepo)

Railway picks **Dockerfile** over Railpack when a root `Dockerfile` exists. This repo keeps the Python stack in **`Dockerfile.legacy`** only for `docker compose`, so Railway uses **Railpack + pnpm**.

Root **`pyproject.toml`** is legacy Python metadata only. **`railpack.json`** sets **`provider`: `"node"`** so Railpack still installs Node and pnpm (via Corepack); otherwise detection can choose Python and **`pnpm: not found`** during build.

## What to run on Railway

| Deploy | Use |
|--------|-----|
| **API** | Config file `/infra/railway/api/railway.toml` |
| **Web** | Config file `/infra/railway/web/railway.toml` |
| **Worker** | Config file `/infra/railway/worker/railway.toml` |

Do **not** deploy the legacy Python image (`Dockerfile.legacy`) or duplicate “Dockerfile builder” services for v2.

### AWS SQS (required — ADR-001)

The **API** and **worker** must share one **Standard** queue (plus a **DLQ** in AWS, per your ops setup):

| Variable | API | Worker |
|----------|-----|--------|
| `AWS_REGION` | ✅ | ✅ |
| `AWS_ACCESS_KEY_ID` | ✅ (send) | ✅ (receive/delete/visibility) |
| `AWS_SECRET_ACCESS_KEY` | ✅ | ✅ |
| `SQS_QUEUE_URL` | ✅ | ✅ (same URL) |

Do **not** set **`ALLOW_ASYNC_SKIP`** on Railway (`APP_ENV` must be `staging` or `production`). Cron ticks enqueue via the API → SQS → worker — see **`docs/v2/RAILWAY_DEPLOYMENT.md`** §7 and **`docs/v2/ENVIRONMENT.md`** § AWS SQS.

### Remove unused services

In the Railway project canvas, **delete** any service that was built from the old root Dockerfile / uvicorn / Celery. v2 replaces that with **three** Node services above (plus cron below).

### Per-service setup

1. **Root directory:** `.` (repository root) for API, Web, and Worker.
2. **Config-as-code:** Service → Settings → set path to the matching file above (leading slash as Railway expects for repo-relative paths, e.g. `/infra/railway/api/railway.toml`).
3. **Variables:** See `docs/v2/RAILWAY_DEPLOYMENT.md` and `docs/v2/ENVIRONMENT.md`.
4. **Web:** Define **`VITE_API_URL`** (public API URL). **API:** Define **`PUBLIC_WEB_ORIGIN`** to the SPA’s browser origin so CORS matches.

### Cron instead of a scheduler container

Prefer **Railway Cron** calling `POST https://<api-host>/api/internal/cron/tick` with header `X-Cron-Secret: <INTERNAL_CRON_SECRET>` instead of a fourth long-running service. See §7 in `docs/v2/RAILWAY_DEPLOYMENT.md`.

### API migrations

`infra/railway/api/railway.toml` runs **`pnpm db:migrate`** as `preDeployCommand`. Omit or adjust if you run migrations manually.

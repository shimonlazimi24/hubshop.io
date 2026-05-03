# Contributing to Frodo (v2)

**Active stack:** TypeScript monorepo — **`apps/api`** (NestJS), **`apps/worker`** (SQS consumer), **`apps/web`** (Vite + React), **`packages/*`**.  
Async jobs follow **[ADR-001](./v2/ADR-001-frodo-v2-stack.md)** (**AWS SQS**, not Celery / not Redis as broker).

> **Do not mix** with the legacy Python / FastAPI tree (`backend/`, `frontend/`, pytest). That stack is **archive-only** — see **[docs/legacy/README.md](./legacy/README.md)**.

## Quick start (v2)

1. Read **[docs/v2/README.md](./v2/README.md)** (plan index).
2. Follow **[docs/v2/LOCAL_DEVELOPMENT.md](./v2/LOCAL_DEVELOPMENT.md)** — install, Postgres, `apps/api/.env`, `pnpm dev:api`, `pnpm dev:web`, optional `pnpm dev:worker`.
3. Env semantics: **[docs/v2/ENVIRONMENT.md](./v2/ENVIRONMENT.md)**.
4. Deploy (Railway): **[docs/v2/RAILWAY_DEPLOYMENT.md](./v2/RAILWAY_DEPLOYMENT.md)** + **[infra/railway/README.md](../infra/railway/README.md)**.

## Prerequisites (v2)

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | ≥ 20 | API, worker, web, packages |
| pnpm | 9.x (see root `packageManager`) | Workspaces |
| PostgreSQL | 16+ (or Supabase) | Drizzle / Nest |
| AWS account | — | **SQS** queue shared by API + worker (staging/prod; recommended for local parity) |

Docker is optional — use it only to run Postgres/Redis locally if you prefer containers over managed DB.

## Repo layout (v2-focused)

```
apps/api/          NestJS HTTP API (enqueues to SQS)
apps/worker/       Long-poll worker (same SQS_QUEUE_URL)
apps/web/          Vite SPA
packages/contracts packages/config packages/db packages/domain …
```

## Tests & quality (v2)

From repo root (after `pnpm install --frozen-lockfile`):

```bash
pnpm lint
pnpm test
pnpm build
```

Python / pytest under `tests/` applies **only** to the **legacy** stack — see **[docs/legacy/CONTRIB_PYTHON_ARCHIVE.md](./legacy/CONTRIB_PYTHON_ARCHIVE.md)** if you must run it.

## Git & commits

- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, etc.
- No secrets in repo — use `apps/api/.env` (gitignored) and platform secrets.

## Legacy archive

Full old contributor guide (Python, Next.js `frontend/`, docker-compose services table): **[docs/legacy/CONTRIB_PYTHON_ARCHIVE.md](./legacy/CONTRIB_PYTHON_ARCHIVE.md)**.

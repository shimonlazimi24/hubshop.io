# Frodo / Hubshop — v2 platform (canonical)

## Product

Unified TikTok SaaS dashboard (Shop, Developer, Marketing, LIVE): auth, token vault, commerce sync, agency workspaces.

## Canonical stack ([ADR-001](./docs/v2/ADR-001-frodo-v2-stack.md))

| Layer | Technology |
|-------|------------|
| API | **NestJS** — `apps/api` |
| Worker | **Node** — `apps/worker`, polls **AWS SQS** (same `SQS_QUEUE_URL` as API) |
| ORM / migrations | **Drizzle** + Postgres — `packages/db` |
| Web | **Vite + React + React Router** — `apps/web` |
| Shared domain | `packages/domain`, `packages/contracts`, `packages/config` |
| Cache / realtime | **Redis** optional — not the job broker |
| Async jobs | **SQS** only (API enqueue → worker consume); Railway Cron → API tick → SQS |

**Legacy** Python FastAPI (`backend/`), Next.js `frontend/`, root `docker-compose` + `Dockerfile.legacy`, pytest — **frozen / archive**. Do **not** document or operate them alongside v2 as one path. See **[docs/legacy/README.md](./docs/legacy/README.md)**.

## Doc map (use these)

| Doc | Purpose |
|-----|---------|
| [docs/v2/README.md](./docs/v2/README.md) | **Start here** — v2 index |
| [docs/v2/LOCAL_DEVELOPMENT.md](./docs/v2/LOCAL_DEVELOPMENT.md) | pnpm, env, dev servers |
| [docs/v2/ENVIRONMENT.md](./docs/v2/ENVIRONMENT.md) | Variables (SQS, DB, JWT, …) |
| [docs/v2/RAILWAY_DEPLOYMENT.md](./docs/v2/RAILWAY_DEPLOYMENT.md) | Production layout |
| [docs/CONTRIB.md](./docs/CONTRIB.md) | Contributing (v2-only entry) |
| [infra/railway/README.md](./infra/railway/README.md) | Railway config-as-code |

## Project structure (v2)

```
apps/api/
apps/worker/
apps/web/
apps/scheduler/          # optional cron helper
packages/contracts/
packages/config/
packages/db/
packages/domain/
```

Legacy directories (`backend/`, `frontend/`, `tests/` pytest) remain in-repo for migration reference — not part of the v2 plan.

## Development (v2)

```bash
pnpm install --frozen-lockfile
cp apps/api/.env.example apps/api/.env   # then edit DATABASE_URL, JWT_SECRET, SQS…
pnpm db:migrate                          # from repo root with DATABASE_URL set
pnpm dev:api                             # http://localhost:8001
pnpm dev:web                             # http://localhost:5173
pnpm dev:worker                          # needs AWS_REGION + SQS_QUEUE_URL + IAM
```

Details: [docs/v2/LOCAL_DEVELOPMENT.md](./docs/v2/LOCAL_DEVELOPMENT.md).

## Tests

```bash
pnpm test
pnpm lint
```

## Conventions

- TypeScript strict in apps/packages; match existing Nest/Drizzle patterns.
- No secrets committed; use platform env + `apps/api/.env`.
- Conventional commits.

## Documentation index

| Doc | Notes |
|-----|-------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Historical / broad system doc — prefer **docs/v2** for active decisions |
| [docs/RUNBOOK.md](./docs/RUNBOOK.md) | Ops — may still mention legacy services; align procedures with v2 where deploying Node |

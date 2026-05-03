# Frodo v2 — canonical plan & docs

This directory is the **single source of truth** for the **original v2 platform**: TypeScript monorepo, **NestJS API**, **SQS-backed worker**, **Vite/React SPA**, **Drizzle + Postgres**.  
Legacy Python / FastAPI / Next.js `frontend/` material lives under **[docs/legacy/](../legacy/README.md)** — read it only for archaeology or strangler migration; **do not blend** with v2 setup.

## Core documents

| Doc | What it covers |
|-----|----------------|
| [ADR-001-frodo-v2-stack.md](./ADR-001-frodo-v2-stack.md) | Stack decisions (SQS, no Redis as job broker, etc.) |
| [LOCAL_DEVELOPMENT.md](./LOCAL_DEVELOPMENT.md) | Local pnpm workflow, `apps/api` env, worker, web |
| [ENVIRONMENT.md](./ENVIRONMENT.md) | Env vars for API, worker, scheduler |
| [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) | Railway services + SQS |
| [MODULE_INVENTORY.md](./MODULE_INVENTORY.md) | Legacy → v2 module mapping |
| [CUTOVER_RUNBOOK.md](./CUTOVER_RUNBOOK.md) | Cutover / rollback notes |

## Infra as code

| Path | Purpose |
|------|---------|
| [../../infra/railway/README.md](../../infra/railway/README.md) | Railway config-as-code (`railway.toml` per service) |

## Application entrypoints (v2)

- **API:** `apps/api`
- **Worker:** `apps/worker` (polls **same `SQS_QUEUE_URL` as API**)
- **Web:** `apps/web`
- **Shared packages:** `packages/*`

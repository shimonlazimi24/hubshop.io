# Legacy stack (frozen reference)

This folder documents the **previous** Frodo implementation — **Python 3.12 / FastAPI**, **`backend/`**, **`frontend/`** (Next.js), Alembic, optional Celery modules under `backend/workers/`, and the root **`docker-compose.yml`** + **`Dockerfile.legacy`**.

It is **not** the product roadmap. **Do not mix** these instructions with v2 day-to-day work.

## Canonical v2 plan (active)

| Doc | Purpose |
|-----|---------|
| [docs/v2/README.md](../v2/README.md) | Index — ADR-001, local dev, env, Railway |
| [docs/v2/ADR-001-frodo-v2-stack.md](../v2/ADR-001-frodo-v2-stack.md) | Architecture decisions (Nest, Drizzle, Vite, **SQS**) |
| [docs/v2/LOCAL_DEVELOPMENT.md](../v2/LOCAL_DEVELOPMENT.md) | pnpm, `apps/api`, `apps/worker`, `apps/web` |

## Legacy docs in this folder

| File | Contents |
|------|----------|
| [CONTRIB_PYTHON_ARCHIVE.md](./CONTRIB_PYTHON_ARCHIVE.md) | Old full contributor guide (Python setup, pytest, docker compose services) |

## Repo paths that remain for archive / migration only

- `backend/`, `frontend/`, `tests/` (pytest), root `docker-compose.yml`, `Dockerfile.legacy`, `tiktok-shop-sdk/` sidecar used by legacy compose.

When in doubt, follow **docs/v2** only.

# Frodo — Unified TikTok SaaS Platform

## Quick Context

Frodo unifies TikTok's fragmented ecosystem (Shop, Developer, Marketing, LIVE) into one SaaS dashboard for agencies. It handles cross-platform auth, token management, data sync, and analytics — letting agencies manage all TikTok operations from a single workspace.

> Deep dive: [ARCHITECTURE.md](./ARCHITECTURE.md) | Setup: [docs/CONTRIB.md](./docs/CONTRIB.md) | Ops: [docs/RUNBOOK.md](./docs/RUNBOOK.md)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy async, Pydantic v2 |
| Database | PostgreSQL 16 (multi-tenant, JSONB) |
| Cache/Broker | Redis 7 (token cache, Celery broker, rate limits, pub/sub) |
| Task Queue | Celery 5 (worker + beat) |
| Frontend | Next.js 15 (App Router), React 19, Tailwind v4, TypeScript |
| SDK Sidecar | Node.js 20, Fastify — TikTok Shop HMAC signing proxy |
| Infra | Docker Compose (postgres, redis, backend, frontend, celery worker, celery beat) |

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI app factory, router registration
│   ├── config.py            # All env vars (pydantic-settings BaseSettings)
│   ├── dependencies.py      # FastAPI DI (CurrentUser, DBSession, get_workspace_id)
│   ├── auth/                # JWT, social login (TikTok + Google), RBAC
│   ├── db/models/           # 18 ORM model files, one per domain
│   ├── middleware/           # CORS, tenant isolation, request logging
│   ├── modules/             # 11 domain modules (see Module Pattern below)
│   ├── tiktok/              # Platform clients + gateway facade
│   ├── utils/               # Shared utilities
│   └── workers/             # Celery tasks (sync, token refresh, webhooks)
├── frontend/
│   └── src/
│       ├── app/(auth)/      # Login, register, OAuth callbacks
│       ├── app/(dashboard)/ # 13 dashboard sections (ads, commerce, content, etc.)
│       ├── components/      # dashboard/, landing/, ui/ component libraries
│       ├── hooks/           # WebSocket, platform filter, workspace context
│       └── lib/             # api.ts (1500-line client), auth.ts, utils.ts
├── tiktok-shop-sdk/         # Node.js sidecar for Shop API HMAC signing
├── tests/                   # 879 tests (conftest.py at root)
├── docs/                    # CONTRIB.md, RUNBOOK.md, CODEMAPS/, plans/
└── knowledge-base/          # 60-file TikTok API research library
```

> Detailed maps: [docs/CODEMAPS/](./docs/CODEMAPS/) (architecture, backend, frontend, data)

## Development Commands

### Backend
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
cd frontend && npm install && npm run dev    # localhost:3000
```

### SDK Sidecar
```bash
cd tiktok-shop-sdk && npm ci && npm run build && npm run dev    # localhost:4000
```

### Database
```bash
docker compose up -d postgres redis
alembic upgrade head                    # run migrations
alembic revision --autogenerate -m ""   # create migration
```

### Docker (full stack)
```bash
docker compose up        # all 6 services
docker compose down
```

### Tests
```bash
pytest                                          # all 879 tests
pytest -m unit                                  # 842 unit tests
pytest -m integration                           # 37 integration tests
pytest --cov=backend --cov-report=term-missing  # with coverage
pytest tests/path/to/test_file.py -v            # specific file
```

### Quality
```bash
ruff format backend/ tests/          # format
ruff check backend/ tests/ --fix     # lint + autofix
mypy backend/                        # type check
bandit -r backend/                   # security scan
```

## Architecture Patterns

### Module Pattern
Each domain module in `backend/modules/` follows:
```
modules/<domain>/
├── __init__.py
├── routes/          # FastAPI routers (may have multiple route files)
├── services/        # Business logic
├── schemas.py       # Pydantic request/response models
└── webhook_handlers.py  # (if applicable)
```

### TikTok Gateway
`backend/tiktok/gateway.py` is the unified facade for all 4 platforms:
- Platform-specific clients: `shop/`, `developer/`, `marketing/`, `live/`, `research/`
- Middleware chain: Rate Limiter (Redis token bucket) → Circuit Breaker → Retry (exponential backoff, 3x)
- SDK sidecar client: `shop/sdk_client.py` proxies through Node.js for HMAC signing

### Auth & Multi-Tenancy
- JWT: HS256, 15min access / 7-day refresh, HttpOnly cookies
- Claims: `user_id`, `organization_id`, `role`
- 5-tier RBAC: owner > admin > manager > member > viewer
- Social login: TikTok + Google OAuth
- Hierarchy: Organization → Workspace → Membership
- `workspace_id` on all tenant-scoped tables

### Token Security
- AES-256-GCM encryption in `TokenVault` model
- Celery Beat auto-refresh: Shop every 24h, Developer every 12h, Marketing daily health check

### Background Tasks
- `backend/workers/celery_app.py` — config + 20 periodic beat schedules
- Domain sync workers: ad, analytics, content, creator, data, intelligence, live, messaging
- Token refresh + webhook processor

### Real-Time
- WebSocket via Redis pub/sub for commerce events and sync progress
- Hooks: `useCommerceWebSocket`, `useSyncWebSocket`

## Key Files

| File | Purpose |
|------|---------|
| `backend/main.py` | App factory, router registration, middleware stack |
| `backend/config.py` | All env vars via pydantic-settings |
| `backend/dependencies.py` | FastAPI DI: CurrentUser, DBSession, get_workspace_id |
| `backend/db/models/base.py` | SQLAlchemy base, common mixins |
| `backend/tiktok/gateway.py` | Unified TikTok API facade |
| `backend/workers/celery_app.py` | Celery config + 20 beat schedules |
| `frontend/src/lib/api.ts` | 1500-line typed API client |
| `frontend/src/lib/auth.ts` | Auth helpers, token management |
| `frontend/src/app/(dashboard)/layout.tsx` | Auth guard + workspace context provider |
| `frontend/src/config/navigation.ts` | Sidebar nav configuration |
| `tiktok-shop-sdk/src/` | Fastify sidecar for Shop HMAC signing |

## Conventions

- **Python**: PEP 8, type annotations everywhere, ruff format + lint, mypy strict
- **Git**: conventional commits — `feat|fix|refactor|docs|test|chore|perf|ci: description`
- **Tests**: pytest, markers (`unit`/`integration`/`e2e`), target 80%+ coverage
- **New modules**: follow `routes/ + services/ + schemas.py` pattern
- **Frontend**: Tailwind utility classes via `cn()`, component libs in `components/ui/`
- **No secrets in code**: use `.env` + `backend/config.py` (pydantic-settings)

## Documentation Index

| Doc | What's Inside |
|-----|---------------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Full system design, data model DDL, phasing |
| [docs/CONTRIB.md](./docs/CONTRIB.md) | Setup guide, env vars, dev scripts, project structure |
| [docs/RUNBOOK.md](./docs/RUNBOOK.md) | Ops procedures, monitoring, troubleshooting |
| [docs/CODEMAPS/](./docs/CODEMAPS/) | Auto-generated architecture maps (4 files) |
| [docs/plans/](./docs/plans/) | 19 implementation plan files |
| [knowledge-base/](./knowledge-base/) | 60-file TikTok API research library |

## Current State

- **Status**: Pre-production, actively developing
- **Branch**: chore/bootstrap-claude-md
- **Version**: 0.1.0
- **Tests**: 879 (842 unit + 37 integration)
- **Migrations**: alembic (social_identities + nullable password)
- **Last session**: 2026-03-04 — Created 5-doc engineering handover package in docs/handover/ (talking points, architecture, process flows, zero-to-schema, production readiness)
- **Next**: Commit handover docs, production readiness execution, Phase 7 Intelligence platform, SDK sidecar integration tests

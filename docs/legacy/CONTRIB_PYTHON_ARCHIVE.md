# Archived: Contributing — legacy Python / FastAPI stack

> **Not part of the v2 plan.** This file is a frozen copy of the old contributor guide (Python backend, Next.js `frontend/`, Celery, root `docker compose`).  
> **Active development:** [docs/v2/README.md](../v2/README.md) and [docs/CONTRIB.md](../CONTRIB.md).

---

# Contributing to Frodo (archived snapshot)

> Unified TikTok SaaS Platform - "One platform to rule them all"

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Backend runtime |
| Node.js | 20+ | Frontend runtime |
| Docker & Docker Compose | Latest | Local services (PostgreSQL, Redis) |
| Git | Latest | Version control |

## Environment Setup

### 1. Clone and install backend

```bash
git clone <repo-url> && cd frodo
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. Install frontend

```bash
cd frontend
npm install
cd ..
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your values (see Environment Variables below)
```

### 4. Start infrastructure

```bash
docker compose up -d postgres redis
```

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start development servers

```bash
# Terminal 1: Backend API
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

Background jobs for **Frodo v2** follow **ADR-001**: **`apps/api`** → **AWS SQS** → **`apps/worker`** (same **`SQS_QUEUE_URL`**). The legacy Python tree still contains Celery modules only for rare maintenance — prefer the Node worker + SQS.

Or start everything via Docker Compose:

```bash
docker compose up
```

## Environment Variables

> Source of truth: `.env.example`

| Variable | Purpose | Format | Required |
|----------|---------|--------|----------|
| `APP_NAME` | Application name | String | Yes |
| `APP_ENV` | Environment (`development`, `staging`, `production`) | String | Yes |
| `DEBUG` | Enable debug mode | `true`/`false` | Yes |
| `SECRET_KEY` | App-level secret key | Random string | Yes |
| `FRONTEND_URL` | Frontend origin for CORS | URL | Yes |
| `BACKEND_URL` | Backend base URL | URL | Yes |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:port/db` | Yes |
| `REDIS_URL` | Redis connection string | `redis://host:port/db` | Yes |
| `JWT_SECRET_KEY` | JWT signing secret | Random string | Yes |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | Integer (default: 15) | Yes |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | Integer (default: 7) | Yes |
| `TOKEN_VAULT_KEY` | AES-256 encryption key for token vault | Base64-encoded 32-byte key | Yes |
| `TIKTOK_SHOP_APP_KEY` | TikTok Shop app key | String | For Shop features |
| `TIKTOK_SHOP_APP_SECRET` | TikTok Shop app secret | String | For Shop features |
| `TIKTOK_DEVELOPER_CLIENT_KEY` | TikTok Developer client key | String | For Developer features |
| `TIKTOK_DEVELOPER_CLIENT_SECRET` | TikTok Developer client secret | String | For Developer features |
| `TIKTOK_MARKETING_APP_ID` | TikTok Marketing app ID | String | For Ads features |
| `TIKTOK_MARKETING_APP_SECRET` | TikTok Marketing app secret | String | For Ads features |
| `TIKTOK_RESEARCH_CLIENT_KEY` | TikTok Research API client key | String | For Intelligence features |
| `TIKTOK_RESEARCH_CLIENT_SECRET` | TikTok Research API client secret | String | For Intelligence features |
| `CELERY_BROKER_URL` | Celery broker (Redis) | `redis://host:port/db` | Yes |
| `CELERY_RESULT_BACKEND` | Celery result store (Redis) | `redis://host:port/db` | Yes |

## Available Scripts

### Backend (Python)

| Command | Description |
|---------|-------------|
| `uvicorn backend.main:app --reload` | Start FastAPI dev server (port 8000) |
| `alembic upgrade head` | Run database migrations |
| `alembic revision --autogenerate -m "description"` | Generate new migration |
| `alembic downgrade -1` | Rollback last migration |
| `pytest` | Run all tests (879 tests) |
| `pytest tests/unit` | Run unit tests only |
| `pytest tests/integration` | Run integration tests only |
| `pytest --cov=backend --cov-report=term-missing` | Run tests with coverage |
| `black backend/ tests/` | Format code |
| `isort backend/ tests/` | Sort imports |
| `ruff check backend/ tests/` | Lint code |
| `ruff check --fix backend/ tests/` | Auto-fix lint issues |
| `mypy backend/` | Type checking |
| `bandit -r backend/` | Security scanning |

### Frontend (Node.js / Next.js)

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Next.js dev server (port 3000) |
| `npm run build` | Production build |
| `npm run start` | Start production server |
| `npm run lint` | ESLint check |

### Docker Compose

| Command | Description |
|---------|-------------|
| `docker compose up` | Start api, postgres, redis, tiktok-shop-sdk (legacy Python API) |
| `docker compose up -d postgres redis` | Start infrastructure only |
| `docker compose down` | Stop all services |
| `docker compose down -v` | Stop and remove volumes (destroys data) |
| `docker compose logs -f api` | Follow API logs |
| `docker compose logs -f tiktok-shop-sdk` | Follow Shop SDK sidecar logs |

## Docker Services

| Service | Image / Build | Port | Healthcheck |
|---------|--------------|------|-------------|
| `api` | Custom (`Dockerfile.legacy`) | 8000 | `curl -f http://localhost:8000/health` |
| `tiktok-shop-sdk` | `./tiktok-shop-sdk` | 4000 | HTTP `/health` |
| `postgres` | `postgres:16-alpine` | 5432 | `pg_isready -U frodo` |
| `redis` | `redis:7-alpine` | 6379 | `redis-cli ping` |

## Project Structure

```
frodo/
  backend/
    main.py                 # FastAPI app factory
    config.py               # pydantic-settings
    dependencies.py         # DI (DB sessions, current user)
    auth/                   # JWT, RBAC, passwords, routes
    db/
      models/               # SQLAlchemy ORM models (17 files, 120+ entity classes)
        advertising.py      #   AdAccount, Campaign, AdGroup, Ad, Audience, Pixel, Catalog, Creative, SplitTest
        affiliate.py        #   AffiliateProduct, OpenCollaboration, TargetCollaboration
        analytics.py        #   ScheduledReport, Notification, ApiKey, UnifiedKpiSnapshot
        commerce.py         #   Shop, Product, Order, Return, Promotion, Fulfillment
        content.py          #   Video, VideoMetrics, ContentPublishJob
        creators.py         #   Creator, CreatorCampaign, CreatorInvitation, ContentAuthorization
        finance.py          #   Settlement, Transaction, Payment
        intelligence.py     #   TrendSnapshot, CompetitorTracker, CompetitorContent, ResearchQuery
        live.py             #   LiveSession, LiveEvent, LiveAnalytics
        messaging.py        #   Conversation, Message, AutoMessage
        organic.py          #   BrandMention, MentionKeyword, OrganicComment
        organization.py     #   Workspace, WorkspaceMember
        social_identity.py  #   SocialIdentity
    tiktok/                 # Platform clients (5 clients)
      shop_client.py        #   TikTokShopClient (HMAC-SHA256)
      developer_client.py   #   TikTokDeveloperClient (OAuth 2.0)
      marketing_client.py   #   TikTokMarketingClient (SDK adapter)
      research_client.py    #   TikTokResearchClient (client credentials)
      live_client.py        #   TikTokLiveClientWrapper (WebSocket)
      gateway.py            #   PlatformGateway (rate limiter, circuit breaker, retry)
    modules/
      connect/              # TikTok OAuth flows, account management
      commerce/             # Shop: products, orders, fulfillment, returns, affiliate, promotions, finance
      advertising/          # Marketing: campaigns, ad groups, ads, reports, audiences, pixels, catalogs, creatives, search, symphony, split tests, leads, automation, comments
      content/              # Developer: videos, publishing, calendar
      creators/             # TTCM: discovery, profiles, campaigns, invitations, Spark Ads
      analytics/            # Cross-platform: KPIs, reports, notifications, API keys
      intelligence/         # Research: trends, competitors, creator insights, data sources
      live/                 # LIVE: stream monitoring, sessions, analytics
      messaging/            # Messaging: conversations, auto-messages
      organic/              # Organic: brand mentions, keywords, comments
      webhooks/             # Webhook ingestion + signature verification
    workers/                # Celery tasks (12 modules)
      token_refresh.py      #   Token refresh (Shop, Developer, Marketing)
      webhook_processor.py  #   Async webhook processing
      data_sync.py          #   Commerce data sync (orders, products)
      ad_sync.py            #   Advertising sync (accounts, campaigns, ad groups, ads)
      content_sync.py       #   Content sync (videos, metrics)
      creator_sync.py       #   Creator metrics sync
      analytics_sync.py     #   Analytics aggregation
      intelligence_sync.py  #   Trend + competitor sync
      live_sync.py          #   Live stream monitoring + cleanup
      messaging_sync.py     #   Conversation sync
    middleware/             # Tenant, logging middleware
    utils/                  # Crypto, pagination
  frontend/
    src/app/(auth)/         # Login, register pages
    src/app/(dashboard)/    # 74 dashboard pages with sidebar layout
      overview/             #   KPI dashboard + Quick Actions
      connect/              #   Account connection
      commerce/             #   Products, orders, returns, analytics, affiliate, promotions, finance
      ads/                  #   Campaigns (list/detail/wizard), ad groups, ads, creatives, reports, audiences, pixels, catalogs, search, symphony, split tests, leads, automation, comments
      content/              #   Videos, publish, calendar
      creatives/            #   Creative Hub: library, performance, generate
      creators/             #   Discover, profiles, campaigns, spark ads
      intelligence/         #   Trends, competitors, creator insights, research
      live/                 #   Monitor, sessions, analytics, history
      messaging/            #   Conversations, auto-messages
      organic/              #   Mentions, keywords, publish
      analytics/            #   Overview, reports, notifications, API keys
      settings/             #   User settings
    src/components/
      ui/                   #   Component library (20 components with barrel export)
      dashboard/            #   Page header, sidebar, top bar
    src/config/             # Navigation config (14 sidebar items)
    src/hooks/              # Custom hooks (usePlatformFilter, useCommerceWebSocket, useSidebarState)
    src/lib/                # API client, auth helpers, toast store
  tests/
    unit/                   # Unit tests by module
    integration/            # Integration tests (routes, sync, webhooks, WebSocket)
  knowledge-base/           # TikTok API research (60 markdown files)
  docs/                     # Project documentation
```

## Testing

### Running tests

```bash
# All tests (879 passing)
pytest

# Unit tests only
pytest tests/unit -v

# Integration tests only
pytest tests/integration -v

# With coverage report
pytest --cov=backend --cov-report=term-missing

# Specific module
pytest tests/unit/advertising -v
pytest tests/unit/commerce -v
pytest tests/unit/content -v
pytest tests/unit/creators -v
pytest tests/unit/analytics -v
pytest tests/unit/intelligence -v
pytest tests/unit/live -v
pytest tests/unit/messaging -v
pytest tests/unit/organic -v
```

### Test markers

```bash
pytest -m unit         # Unit tests
pytest -m integration  # Integration tests
pytest -m e2e          # E2E tests
```

### Test coverage by module

| Module | Test Count | Areas Covered |
|--------|-----------|---------------|
| Advertising | 136 | Ad accounts, campaigns, ad groups, ads, reports, audiences, pixels, search, symphony, split tests, automation |
| Content | 68 | Content models, publish service, video sync, photo publish |
| Creators | 55 | Campaigns, profiles, creator models, discovery, invitations |
| Commerce | 54 | Products, orders, schemas, webhook handlers, analytics, fulfillment, returns |
| Analytics | 47 | KPIs, reports, notifications, API keys, models |
| Intelligence | 42 | Trends, competitors, research queries, data sources |
| Models | 39 | DB model schema tests across all entity types |
| TikTok Clients | 38 | Platform clients (Shop, Developer, Marketing, Research, LIVE) |
| Workers | 31 | Celery task scheduling, sync workers |
| LIVE | 26 | Sessions, events, analytics, stream monitoring |
| Organic | 17 | Mentions, keywords, comments |
| Messaging | 16 | Conversations, messages, auto-messages |
| Integration | 37 | Route integration, sync pipelines, webhooks, WebSocket |

## Code Quality

### Formatting & linting

```bash
black backend/ tests/        # Format
isort backend/ tests/        # Sort imports
ruff check backend/ tests/   # Lint
ruff check --fix backend/    # Auto-fix
```

### Configuration (pyproject.toml)

| Tool | Config |
|------|--------|
| black | line-length=88, target py312 |
| isort | profile=black, line-length=88 |
| ruff | E, F, W, I, N, UP, S, B, A, C4, SIM rules |
| mypy | strict mode, pydantic plugin |
| pytest | asyncio_mode=auto, testpaths=tests |

## Development Workflow

1. Create a feature branch from `main`
2. Write tests first (TDD approach)
3. Implement the feature
4. Run `black`, `isort`, `ruff check`, `mypy`
5. Run `pytest --cov=backend`
6. Commit with conventional commit format: `feat:`, `fix:`, `refactor:`, etc.
7. Open a pull request

## API Documentation

When running in debug mode (`DEBUG=true`), interactive API docs are available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

### API Route Prefixes

| Prefix | Module | Endpoints | Description |
|--------|--------|-----------|-------------|
| `/api/auth` | auth | 4 | Login, register, token refresh, profile |
| `/api/connect` | connect | 3 | TikTok OAuth flows, account management |
| `/api/commerce` | commerce | 43+ | Shops, products, orders, fulfillment, returns, analytics, affiliate, promotions, finance |
| `/api/ads` | advertising | 96+ | Ad accounts, campaigns (CRUD + wizard), ad groups, ads, reports, audiences, pixels, catalogs, creatives, search, symphony, split tests, leads, automation, comments |
| `/api/content` | content | 9+ | Video list/detail, metrics, publish, calendar |
| `/api/creators` | creators | 14+ | Discovery (TTCM), profiles, campaigns, invitations, Spark Ads |
| `/api/analytics` | analytics | 24+ | Overview KPIs, reports, notifications, API keys |
| `/api/intelligence` | intelligence | 13+ | Trends, competitors, creator insights, research queries |
| `/api/live` | live | 9+ | Stream monitoring, sessions, analytics |
| `/api/messaging` | messaging | 11+ | Conversations, messages, auto-messages |
| `/api/organic` | organic | 15+ | Brand mentions, keywords, comments |
| `/webhooks` | webhooks | 1 | TikTok webhook ingestion (no `/api` prefix) |

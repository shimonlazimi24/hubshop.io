# System Architecture Overview — Frodo Unified TikTok SaaS Platform

> **Audience:** Engineering team taking the platform to production
> **Freshness:** 2026-03-04
> **Status:** Pre-production, v0.1.0

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Service Architecture](#2-service-architecture)
3. [Tech Stack Deep Dive](#3-tech-stack-deep-dive)
4. [Backend Architecture](#4-backend-architecture)
5. [TikTok Gateway Pattern](#5-tiktok-gateway-pattern)
6. [Data Layer](#6-data-layer)
7. [Cache and Message Broker](#7-cache-and-message-broker)
8. [Task Queue](#8-task-queue)
9. [Frontend Architecture](#9-frontend-architecture)
10. [SDK Sidecar](#10-sdk-sidecar)
11. [Infrastructure](#11-infrastructure)
12. [Security Architecture](#12-security-architecture)

---

## 1. System Overview

### The Problem

TikTok's ecosystem is fragmented across four completely independent platforms — Shop, Developer, Marketing, and LIVE — each with its own authentication, signing mechanisms, webhook formats, rate limits, and developer portals. Agencies managing brands on TikTok must juggle multiple dashboards, credential sets, and integration patterns simultaneously.

### What Frodo Does

Frodo is the unification layer TikTok does not provide. It is a multi-tenant SaaS platform that lets agencies connect all their TikTok accounts once and manage commerce, advertising, content, creator partnerships, live operations, messaging, and analytics from a single workspace.

### Full System Diagram

```
 ┌─────────────────────────────────────────────────────────────────────┐
 │                      CLIENT TIER                                     │
 │                                                                       │
 │   ┌───────────────────────────┐    ┌──────────────────────────────┐  │
 │   │   Browser / Next.js 15    │    │    TikTok Platform Webhooks  │  │
 │   │   (port 3000)             │    │    (Shop, Developer, Mktg)   │  │
 │   └──────────────┬────────────┘    └──────────────┬───────────────┘  │
 └──────────────────┼──────────────────────────────  │ ────────────────┘
                    │ HTTPS/WS                        │ HTTPS POST
 ┌──────────────────▼─────────────────────────────────▼────────────────┐
 │                      API TIER                                         │
 │                                                                       │
 │   ┌─────────────────────────────────────────────────────────────┐    │
 │   │              FastAPI Backend  (port 8000)                    │    │
 │   │                                                               │    │
 │   │   Middleware: CORSMiddleware → TenantMiddleware →            │    │
 │   │               RequestLoggingMiddleware                        │    │
 │   │                                                               │    │
 │   │   /api/auth        /api/connect     /api/commerce            │    │
 │   │   /api/ads         /api/content     /api/creators            │    │
 │   │   /api/analytics   /api/intelligence /api/live               │    │
 │   │   /api/messaging   /api/organic     /webhooks/*              │    │
 │   └────────────────┬──────────────────────────────────────────────┘   │
 │                    │                                                   │
 │   ┌────────────────▼──────────────────────────────────────────────┐   │
 │   │               TikTok Platform Gateway                          │   │
 │   │                                                                │   │
 │   │  Rate Limiter → Circuit Breaker → Retry → Platform Client     │   │
 │   │                                                                │   │
 │   │  ┌─────────┐ ┌───────────┐ ┌────────────┐ ┌──────────────┐  │   │
 │   │  │  Shop   │ │ Developer │ │ Marketing  │ │   Research   │  │   │
 │   │  │ (HMAC)  │ │ (Bearer)  │ │ (Custom)   │ │  (OAuth CC)  │  │   │
 │   │  └────┬────┘ └─────┬─────┘ └─────┬──────┘ └──────┬───────┘  │   │
 │   └───────┼────────────┼─────────────┼────────────────┼───────────┘  │
 └───────────┼────────────┼─────────────┼────────────────┼──────────────┘
             │ HTTPS       │ HTTPS        │ HTTPS          │ HTTPS
 ┌───────────▼─────────────▼─────────────▼────────────────▼──────────────┐
 │                    TIKTOK EXTERNAL APIs                                 │
 │  open-api.tiktokglobalshop.com  |  open.tiktokapis.com/v2              │
 │  business-api.tiktok.com        |  (research endpoint)                 │
 └────────────────────────────────────────────────────────────────────────┘

 ┌──────────────────────────────────────────────────────────────────────┐
 │                      DATA / WORKER TIER                               │
 │                                                                        │
 │  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────────┐   │
 │  │  PostgreSQL 16   │  │    Redis 7        │  │  Celery Workers   │   │
 │  │  (port 5432)     │  │  (port 6379)      │  │  (concurrency 4)  │   │
 │  │                  │  │                   │  │                   │   │
 │  │  18 model files  │  │  DB 0: app cache  │  │  24 periodic      │   │
 │  │  120+ entities   │  │  DB 1: Celery     │  │  tasks (beat)     │   │
 │  │  multi-tenant    │  │       broker      │  │                   │   │
 │  │  via workspace_id│  │  DB 2: Celery     │  │  Celery Beat      │   │
 │  │                  │  │       results     │  │  (single inst.)   │   │
 │  └──────────────────┘  └──────────────────┘  └───────────────────┘   │
 └──────────────────────────────────────────────────────────────────────┘

 ┌─────────────────────────────────────────────────────────────────────┐
 │                      SIDECAR TIER                                    │
 │                                                                       │
 │   ┌──────────────────────────────────────────────────────────────┐   │
 │   │        TikTok Shop SDK Sidecar  (port 4000)                  │   │
 │   │        Node.js 20 + Fastify                                  │   │
 │   │        HMAC-SHA256 signing proxy for Shop API                │   │
 │   └──────────────────────────────────────────────────────────────┘   │
 └─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Service Architecture

Six services run in Docker Compose (seven counting the sidecar). Here is a table of every service:

| Service | Image / Build | Port | Role | Dependencies |
|---------|--------------|------|------|-------------|
| `api` | Project `Dockerfile` | 8000 | FastAPI backend, handles all HTTP and WebSocket traffic | postgres (healthy), redis (healthy), tiktok-shop-sdk (healthy) |
| `celery-worker` | Project `Dockerfile` | — | Executes async and periodic tasks at concurrency 4 | postgres (healthy), redis (healthy) |
| `celery-beat` | Project `Dockerfile` | — | Scheduler — fires tasks on cron schedule. Single instance only | postgres (healthy), redis (healthy) |
| `postgres` | `postgres:16-alpine` | 5432 | Primary data store. 18 model files, 120+ entities | — |
| `redis` | `redis:7-alpine` | 6379 | Cache, Celery broker (DB 1), results backend (DB 2), pub/sub | — |
| `tiktok-shop-sdk` | `./tiktok-shop-sdk` Dockerfile | 4000 | Node.js HMAC signing proxy for TikTok Shop API | — |

### Service Start Order

```
postgres + redis + tiktok-shop-sdk
          ↓
         api
          ↓
    celery-worker + celery-beat
```

### Health Checks

| Service | Health Endpoint | Interval |
|---------|----------------|---------|
| api | `GET /health` → `{"status":"healthy","version":"0.1.0"}` | 30s |
| postgres | `pg_isready -U frodo` | 5s |
| redis | `redis-cli ping` | 5s |
| tiktok-shop-sdk | `GET /health` (port 4000) | 15s |

---

## 3. Tech Stack Deep Dive

| Layer | Technology | Version | Why Chosen |
|-------|-----------|---------|-----------|
| **Backend language** | Python | 3.12 | Type annotation maturity, async ecosystem, rich data libs |
| **Backend framework** | FastAPI | latest | Async-native ASGI, automatic OpenAPI generation, Pydantic v2 integration, sub-10ms overhead |
| **ORM** | SQLAlchemy async | 2.x | Full async support, expression-based queries, Alembic migration compatibility |
| **Schema validation** | Pydantic v2 | 2.x | 5-17x faster than v1, JSON serialization, settings management |
| **Database** | PostgreSQL 16 | 16 | Multi-tenant via `workspace_id` scoping, JSONB for flexible platform data, strong ACID guarantees |
| **Cache / Broker** | Redis 7 | 7 | Token cache (fast O(1) lookup), rate-limit counters (INCR/EXPIRE), Celery broker, pub/sub for WebSocket fan-out |
| **Task queue** | Celery 5 | 5 | Battle-tested periodic scheduling (beat), distributed worker execution, dead letter support |
| **Frontend framework** | Next.js 15 | 15 | App Router (RSC), middleware-based auth, streaming SSR, TypeScript first |
| **UI layer** | React 19 | 19 | Concurrent rendering, server components, modern hooks |
| **Styling** | Tailwind CSS v4 | 4 | Utility-first, zero-runtime, co-located with markup |
| **Frontend language** | TypeScript | latest | Type safety across 1600+ line API client |
| **SDK Sidecar** | Node.js 20 + Fastify | 20 / 4.x | TikTok's official Shop SDK is Node.js-only. Fastify for low-overhead HTTP proxy |
| **Migrations** | Alembic | latest | SQLAlchemy-native, auto-generation, version history |
| **Containerization** | Docker Compose | v2 | Single-command local dev and staging stack |
| **Auth** | python-jose + bcrypt | — | JWT HS256, HttpOnly cookie delivery, bcrypt for password hashing |
| **Config** | pydantic-settings | 2.x | Type-safe env var loading, `.env` file support, fail-fast on missing required vars |

---

## 4. Backend Architecture

### App Factory (`backend/main.py`)

The backend is built around a factory function `create_app()` that wires together the middleware stack and all routers. This pattern enables clean testing — tests can import and call `create_app()` with test-specific overrides.

```python
def create_app() -> FastAPI:
    app = FastAPI(title="Frodo - Unified TikTok Platform", ...)

    # Middleware (last added = first executed in request pipeline)
    app.add_middleware(RequestLoggingMiddleware)   # innermost
    app.add_middleware(TenantMiddleware)
    app.add_middleware(CORSMiddleware, ...)        # outermost

    # Routers (all under /api prefix except webhooks)
    app.include_router(auth_router, prefix="/api")
    app.include_router(connect_router, prefix="/api")
    # ... 10 more routers

    # Webhooks at root — TikTok posts here directly, no /api prefix
    app.include_router(webhooks_router)

    return app
```

### Middleware Stack

Request processing order (outermost to innermost):

```
Incoming request
       ↓
  CORSMiddleware          — origin validation, preflight OPTIONS
       ↓
  TenantMiddleware        — extracts X-Workspace-Id header, injects workspace context
       ↓
  RequestLoggingMiddleware — assigns 8-char UUID request_id, logs start/end + timing
       ↓
  Route handler
       ↑
  (reverse order on response)
```

### Dependency Injection

FastAPI's DI system is used for three critical cross-cutting concerns:

```python
# Type aliases used in every route function
CurrentUser = Annotated[User, Depends(get_current_user)]
DBSession   = Annotated[AsyncSession, Depends(get_db)]

# Usage in routes:
async def list_orders(
    user: CurrentUser,
    db: DBSession,
    shop_id: UUID,
) -> list[OrderSummaryResponse]:
    ...
```

| Dependency | Type | What It Does |
|-----------|------|-------------|
| `get_db()` | `AsyncSession` | Opens async SQLAlchemy session, yields it, closes on exit |
| `get_current_user()` | `User` | Extracts Bearer JWT, validates type=access, looks up user in DB |
| `get_org_membership()` | `Membership` | Verifies user is member of the requested organization |

### Module Pattern

Every business domain lives in `backend/modules/<domain>/` and follows a strict structure:

```
modules/<domain>/
├── __init__.py
├── routes/               # FastAPI routers — thin layer, delegates to services
│   └── *.py
├── services/             # Business logic — all database interaction here
│   ├── *.py
│   └── unified_service.py   # (commerce, advertising) cross-platform aggregation
├── schemas.py            # Pydantic request/response DTOs
└── webhook_handlers.py   # (where applicable) webhook event processing
```

The 11 domain modules and their route prefixes:

| Module | Prefix | Description |
|--------|--------|-------------|
| `auth` | `/api/auth` | Login, register, token refresh, social OAuth, profile |
| `connect` | `/api/connect` | TikTok OAuth flows, account listing, identity linking, WebSocket sync |
| `commerce` | `/api/commerce` | Shops, products, orders, fulfillment, returns, promotions, affiliate, finance |
| `advertising` | `/api/ads` | Ad accounts, campaigns, ad groups, ads, reporting, audiences, pixels, catalogs |
| `content` | `/api/content` | Videos, publishing, calendar, analytics, Spark Ads bridge |
| `creators` | `/api/creators` | Creator discovery, profiles, campaigns, invitations, Spark Ads auth |
| `analytics` | `/api/analytics` | KPIs, scheduled reports, notifications, API keys |
| `intelligence` | `/api/intelligence` | Trends, competitor tracking, research queries |
| `live` | `/api/live` | LIVE session monitoring, analytics, history |
| `messaging` | `/api/messaging` | Conversations, messages, auto-message rules |
| `organic` | `/api/organic` | Brand mentions, keyword tracking, comments |
| `webhooks` | `/webhooks` | Platform webhook ingestion (no /api prefix — external callbacks) |

### Configuration (`backend/config.py`)

All environment variables are loaded via `pydantic-settings BaseSettings`. The single `settings` singleton is imported throughout:

```python
from backend.config import settings

# settings.database_url
# settings.redis_url
# settings.jwt_secret_key
# settings.token_vault_key
```

Config categories: App, Database, Redis, JWT, Token Vault, TikTok Shop, TikTok Shop SDK Sidecar, TikTok Developer, TikTok Marketing, TikTok Research, Google OAuth, TikTok Login (social), Celery.

---

## 5. TikTok Gateway Pattern

### The Core Problem: Three Incompatible Signing Mechanisms

Each TikTok platform requires a different authentication approach:

```
TikTok Shop (HMAC-SHA256)
  Base URL: https://open-api.tiktokglobalshop.com
  Sign:  HMAC-SHA256(app_secret, app_secret + path + sorted_params + body + app_secret)
  Header: x-tts-access-token: {access_token}

TikTok Developer API (OAuth 2.0 Bearer)
  Base URL: https://open.tiktokapis.com/v2
  Header: Authorization: Bearer {access_token}

TikTok Marketing API (Custom Header)
  Base URL: https://business-api.tiktok.com/open_api/v1.3
  Header: Access-Token: {access_token}

TikTok Research API (Client Credentials OAuth)
  Base URL: https://open.tiktokapis.com/v2/research
  Header: Authorization: Bearer {access_token}
```

### Gateway Architecture

`backend/tiktok/gateway.py` implements `PlatformGateway`, a unified facade that wraps every outbound API call through the same middleware chain regardless of which TikTok platform is targeted.

```
Service layer calls:
  gateway.get("/products", params={...})
                ↓
  1. Circuit Breaker check — is this platform circuit open?
                ↓
  2. Rate Limiter acquire — token bucket per (platform, account_id)
                ↓
  3. with_retry() — exponential backoff wrapper
                ↓
  4. Platform Client.request() — platform-specific signing + HTTP
                ↓
  5. circuit_breaker.record_success/failure()
                ↓
  Return result dict
```

### Middleware Chain Components

**Rate Limiter** (`backend/tiktok/rate_limiter.py`)
- Redis token-bucket algorithm, per (platform, account_id) pair
- Limits: Shop 50 QPS, Developer 10 QPS, Research 5 QPS, Marketing varies
- `acquire()` returns bool — hard stop if False (no queuing)

**Circuit Breaker** (`backend/tiktok/circuit_breaker.py`)
- Per-platform isolation — Shop circuit does not affect Developer circuit
- States: `CLOSED` (normal) → `OPEN` (failing) → `HALF_OPEN` (testing recovery)
- Thresholds: opens after 5 failures in 60s, half-opens after 30s

```
CLOSED ──(5 failures in 60s)──► OPEN
  ▲                               │
  │         (30s cooldown)        │
  └──(success)── HALF_OPEN ◄──────┘
```

**Retry** (`backend/tiktok/retry.py`)
- `with_retry()` decorator wrapping the actual HTTP call
- Exponential backoff: 1s, 2s, 4s
- Max 3 retries
- Only retries: HTTP 429, 500, 502, 503, 504

### Platform Clients

| Client | File | Auth Mechanism |
|--------|------|---------------|
| `TikTokShopClient` | `tiktok/shop/client.py` | HMAC-SHA256 query signing |
| `TikTokShopSDKClient` | `tiktok/shop/sdk_client.py` | HTTP proxy to Node.js sidecar |
| `TikTokDeveloperClient` | `tiktok/developer/client.py` | OAuth 2.0 Bearer |
| `TikTokMarketingClient` | `tiktok/marketing/client.py` | Custom `Access-Token` header |
| `TikTokResearchClient` | `tiktok/research/client.py` | Client credentials OAuth |
| `TikTokLiveClientWrapper` | `tiktok/live/client.py` | WebSocket (TikTokLive library) |

### Webhook Ingestion (Platform → Frodo)

Three separate inbound endpoints, each with platform-specific signature verification:

| Endpoint | Signature Header | Verification Method |
|----------|-----------------|-------------------|
| `POST /webhooks/shop` | `Authorization` | `HMAC-SHA256(app_secret, app_key + body)` |
| `POST /webhooks/developer` | `TikTok-Signature` | Parse `t=TS,s=SIG`, verify `HMAC-SHA256(client_secret, TS.body)` |
| `POST /webhooks/marketing` | Subscription-specific | Per-subscription config |

Webhook processing pipeline:

```
Receive → Verify signature → Deduplicate (Redis SETNX on idempotency_key)
  → Store in webhook_events (status=received)
  → Enqueue Celery task (backend.workers.webhook_processor)
  → Worker: parse + route to domain handler + update local DB
  → Publish to Redis pub/sub (WebSocket fan-out)
  → Mark processed
```

**Important:** Webhooks are supplemented by Celery polling jobs (every 15-30 min) as a reconciliation fallback. Do not rely solely on webhooks.

---

## 6. Data Layer

### Multi-Tenancy Model

Frodo uses a shared database, shared schema approach. Tenant isolation is enforced by `workspace_id` foreign key on every tenant-scoped table.

```
Organization (agency/brand account)
    └── Workspace (sub-account, e.g., per brand or region)
            └── Membership (user ↔ org/workspace with role)
            └── ConnectedAccount (TikTok platform connection)
                └── TokenVault (encrypted credentials)
                └── Shop / AdAccount / Video / ... (platform data)
```

Multi-tenant isolation strategy:
1. Every query in service layer includes `WHERE workspace_id = :workspace_id`
2. `TenantMiddleware` extracts `X-Workspace-Id` header and injects it into request state
3. `get_workspace_id()` dependency provides it to route handlers
4. PostgreSQL Row-Level Security is planned as defense-in-depth (referenced in architecture plan)

### Database Schema Overview

**Foundation tables (4):**
- `organizations` — agency/brand accounts with plan tier and settings JSONB
- `workspaces` — sub-accounts within an org (unique slug per org)
- `users` — platform users with bcrypt-hashed passwords
- `memberships` — M:N user↔org/workspace with role + permissions JSONB

**Platform connection tables (3):**
- `connected_accounts` — one row per TikTok platform per workspace. Holds `platform` enum (shop/developer/marketing/research), `identity_group_id` for cross-platform linking, `status`, and `metadata` JSONB
- `token_vault` — AES-256-GCM encrypted access and refresh tokens with expiry timestamps and refresh failure tracking
- `platform_app_credentials` — encrypted app keys/secrets per platform per environment

**Commerce tables (10 models):**
`Shop`, `Product`, `ProductSku`, `Order`, `OrderLineItem`, `Package`, `OrderStatusEvent`, `ReturnRequest`, `Promotion`, `SyncCursor`

**Advertising tables (9 models):**
`AdAccount`, `Campaign`, `AdGroup`, `Ad`, `AdSyncCursor`, `Audience`, `Pixel`, `Catalog`, `ReportCache`

**Content tables (5 models):**
`Video`, `VideoMetrics`, `ContentPublishJob`, `ContentSyncCursor`, `Comment`

**Creator tables (4 models):**
`CreatorProfile`, `CreatorCampaign`, `CreatorInvitation`, `ContentAuthorization`

**Analytics tables (5 models):**
`UnifiedKpiSnapshot`, `ScheduledReport`, `Notification`, `NotificationPreference`, `ApiKey`

**Affiliate tables (4 models):**
`AffiliateProduct`, `OpenCollaboration`, `TargetCollaboration`, `CreatorApplication`

**Finance tables (3 models):**
`Settlement`, `Transaction`, `Payment`

**Intelligence tables (4 models):**
`TrendSnapshot`, `CompetitorTracker`, `CompetitorContent`, `ResearchQuery`

**LIVE tables (3 models):**
`LiveSession`, `LiveEvent`, `LiveAnalytics`

**Messaging tables (3 models):**
`Conversation`, `Message`, `AutoMessage`

**Organic tables (3 models):**
`BrandMention`, `MentionKeyword`, `OrganicComment`

**Audit / event tables (2):**
- `webhook_events` — immutable append-only log with `idempotency_key UNIQUE` for deduplication
- `audit_log` — user action trail with IP address

### JSONB Usage

JSONB is used for fields that are platform-specific and schema-variable:

| Table | JSONB Column | Contents |
|-------|-------------|---------|
| `connected_accounts` | `metadata` | Platform-specific account data (e.g., shop_ciphers) |
| `token_vault` | `shop_ciphers` | Array of shop cipher strings for Shop API |
| `campaigns` | `metrics_snapshot` | Latest performance metrics (spend, impressions, clicks) |
| `ads` | `creative` | Ad creative blob (video_id, cover, text, call_to_action) |
| `ad_groups` | `targeting`, `placements`, `schedule` | Complex nested targeting config |
| `organizations` | `settings` | Feature flags, plan limits |
| `memberships` | `permissions` | Fine-grained permission overrides |
| `creator_profiles` | `audience_demographics` | Audience breakdown by age/gender/region |

### Migration Strategy

- Tool: Alembic
- Auto-generation: `alembic revision --autogenerate -m "<description>"`
- Apply: `alembic upgrade head`
- Two migrations exist: initial schema + `social_identities` table + nullable `password` column
- Migration files live in `backend/db/migrations/`

### Base Mixins

All models inherit from two mixins in `backend/db/models/base.py`:
- `UUIDMixin` — provides UUID primary key with `gen_random_uuid()` default
- `TimestampMixin` — provides `created_at` and `updated_at` with auto-update

### Entity Relationship Map

```
Organization ──1:N──► Workspace ──N:M──► User (via Membership)
                           │
                           ├──1:N──► ConnectedAccount ──1:1──► TokenVault
                           │              │
                           │              ├──1:N──► Shop ──1:N──► Product ──1:N──► ProductSku
                           │              │              └──1:N──► Order ──1:N──► OrderLineItem
                           │              │                              └──1:N──► Package
                           │              │                              └──1:N──► ReturnRequest
                           │              │
                           │              └──1:N──► AdAccount ──1:N──► Campaign
                           │                                               └──1:N──► AdGroup
                           │                                                              └──1:N──► Ad
                           │
                           ├──1:N──► Video ──1:N──► VideoMetrics
                           ├──1:N──► CreatorProfile
                           ├──1:N──► CreatorCampaign ──1:N──► CreatorInvitation
                           ├──1:N──► LiveSession ──1:1──► LiveAnalytics
                           ├──1:N──► Conversation ──1:N──► Message
                           └──1:N──► BrandMention
```

---

## 7. Cache and Message Broker

Redis 7 serves four distinct purposes, each using a separate DB index:

| DB | Purpose | Key Patterns |
|----|---------|-------------|
| 0 | Application cache: token cache, rate-limit counters, pub/sub | `rate:{platform}:{account_id}`, `token:{account_id}`, channel `ws:{workspace_id}` |
| 1 | Celery broker — task queue | Managed by Celery |
| 2 | Celery results backend — task result storage | Managed by Celery |

### Token Caching

Decrypted platform tokens are cached in Redis DB 0 with TTL matching token expiry. This avoids hitting PostgreSQL and decrypting AES-256 for every API call.

### Rate Limit Counters

Token-bucket implementation in `backend/tiktok/rate_limiter.py`:
- Key: `rate:{platform}:{account_id}`
- Operations: INCR + EXPIRE, evaluated atomically via Lua script
- Configured rate limits per platform:

| Platform | Limit |
|----------|-------|
| TikTok Shop | 50 QPS per account |
| TikTok Developer | 10 QPS per account |
| TikTok Research | 5 QPS per account |
| TikTok Marketing | Varies by endpoint |

### Webhook Deduplication

`SETNX idempotency_key 1 EX 86400` — atomic set-if-not-exists with 24h TTL. If key already exists, the webhook is a duplicate and is dropped before processing.

### Real-Time WebSocket Fan-out

Celery workers publish to Redis pub/sub channels after processing events:
- Channel: `ws:{workspace_id}:commerce` — order updates
- Channel: `ws:{workspace_id}:sync` — sync progress updates

The FastAPI WebSocket handler subscribes and streams to connected browser clients.

---

## 8. Task Queue

### Celery Configuration

```python
celery_app = Celery("frodo",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/2",
)

# Key settings
task_serializer = "json"          # No pickle — safer for distributed systems
task_acks_late = True             # Acknowledge after task completes, not when received
worker_prefetch_multiplier = 1    # Pull one task at a time — prevents starvation
task_track_started = True         # Track in-progress tasks for monitoring
timezone = "UTC"
```

`task_acks_late = True` is a critical safety setting. If a worker crashes mid-task, the task is re-queued rather than lost.

### Worker Topology

- **Celery Worker**: `celery -A backend.workers.celery_app worker --concurrency=4`
  - 4 concurrent processes per worker container
  - Scale horizontally by running multiple worker containers
- **Celery Beat**: `celery -A backend.workers.celery_app beat`
  - Single instance only — multiple beat instances cause duplicate task scheduling

### Beat Schedule (24 periodic tasks)

| Schedule | Task | Purpose |
|----------|------|---------|
| Every 15 min | `sync_shop_orders` | Order polling fallback |
| Every 30 min | `sync_shop_products` | Product catalog sync |
| Every 30 min | `sync_ad_campaigns` | Campaign metrics refresh |
| Every 30 min | `sync_ad_groups` | Ad group sync (offset +15 min) |
| Every 30 min | `sync_ads` | Ad-level sync (offset +5 min) |
| Every 30 min | `sync_all_videos` | Video content sync |
| Every 30 min | `sync_conversations` | Messaging inbox sync |
| Every 30 min | `run_scheduled_reports` | Check for due report jobs |
| Every hour | `cleanup_stale_sessions` | LIVE session cleanup |
| Every 2 hours | `sync_mentions` | Brand mention tracking |
| Every 4 hours | `sync_trends` | Intelligence trend data |
| Every 6 hours | `sync_all_ad_accounts` | Ad account metadata |
| Every 6 hours | `sync_competitor_content` | Competitor tracking |
| Every 6 hours | `sync_video_metrics` | Video performance metrics |
| Every 12 hours | `refresh_developer_tokens` | TikTok Developer token refresh |
| Every 12 hours | `refresh_creator_profiles` | Creator profile updates |
| Daily midnight | `refresh_shop_tokens` | TikTok Shop token refresh |
| Daily 1 AM | `take_daily_kpi_snapshots` | Cross-platform KPI aggregation |
| Daily 6 AM | `check_marketing_tokens` | Marketing token health check |

### Worker Modules

| Module | File | Responsibility |
|--------|------|---------------|
| `token_refresh` | `workers/token_refresh.py` | Developer/Shop/Marketing token lifecycle |
| `webhook_processor` | `workers/webhook_processor.py` | Async webhook event routing to domain handlers |
| `data_sync` | `workers/data_sync.py` | Commerce orders and products |
| `ad_sync` | `workers/ad_sync.py` | Ad accounts, campaigns, ad groups, ads |
| `content_sync` | `workers/content_sync.py` | Video ingestion and metrics |
| `creator_sync` | `workers/creator_sync.py` | Creator profile updates |
| `analytics_sync` | `workers/analytics_sync.py` | KPI aggregation, report generation |
| `intelligence_sync` | `workers/intelligence_sync.py` | Trends, competitor tracking |
| `live_sync` | `workers/live_sync.py` | Session monitoring and cleanup |
| `messaging_sync` | `workers/messaging_sync.py` | Conversations and mentions |

---

## 9. Frontend Architecture

### Framework: Next.js 15 App Router

The frontend uses the Next.js 15 App Router (not Pages Router). Key implications:
- Route groups `(auth)` and `(dashboard)` organize pages without affecting URL paths
- `layout.tsx` files define shared UI shells — the dashboard layout wraps all 70+ pages
- Server Components (RSC) are available but the project primarily uses client components for interactivity

### Directory Structure

```
frontend/src/
  app/
    layout.tsx                    # Root layout — Geist font, global metadata
    page.tsx                      # Landing page (marketing, 10 sections)
    (auth)/
      login/page.tsx              # Login form + social OAuth buttons
      register/page.tsx           # Registration form
      callback/page.tsx           # OAuth callback handler (all platforms)
    (dashboard)/
      layout.tsx                  # Auth guard + workspace context provider
      overview/page.tsx           # KPI cockpit
      connect/page.tsx            # Account connection wizard
      settings/page.tsx           # Workspace settings
      commerce/                   # 9 pages
      ads/                        # 17 pages
      content/                    # 5 pages
      creatives/                  # 4 pages
      creators/                   # 7 pages
      intelligence/               # 6 pages
      live/                       # 5 pages
      messaging/                  # 4 pages
      organic/                    # 4 pages
      analytics/                  # 8 pages
  components/
    ui/                           # 20 reusable primitive components
    dashboard/                    # 6 layout components (Sidebar, TopBar, etc.)
    landing/                      # 10 marketing section components
  hooks/                          # 3 custom hooks
  lib/
    api.ts                        # 1638-line typed API client
    auth.ts                       # Token management (localStorage + cookies)
    toast-store.ts                # Global toast notification state
    utils.ts                      # cn() utility (clsx + twMerge)
  config/
    navigation.ts                 # Sidebar navigation config (12 items + settings)
```

### Auth Guard

`app/(dashboard)/layout.tsx` is the auth guard. Every dashboard page is a child of this layout. On mount it calls `isAuthenticated()` from `lib/auth.ts` and redirects to `/login` if no valid token exists.

### API Client (`lib/api.ts`)

A 1638-line fully-typed API client with 100+ exported functions. Key patterns:

```typescript
// Base fetch wrapper with auth headers and error handling
async function apiFetch<T>(path: string, options?: RequestInit): Promise<T>

// Per-module typed wrappers — example:
export async function listOrders(shopId: string, params: OrderFilters): Promise<OrderListResponse>
export async function fulfillOrder(shopId: string, orderId: string, body: FulfillOrderBody): Promise<void>
```

All API types are defined in the same file — request bodies and response shapes mirror the backend Pydantic schemas.

### Component Architecture

**Layout Pattern — 3-Zone Performance Cockpit:**
```
┌─────────────────────────────────────────────────────┐
│  PageShell                                           │
│  ┌─────────────────────────────────────────────────┐│
│  │  MetricBar (top) — KPI cards                    ││
│  └─────────────────────────────────────────────────┘│
│  ┌──────────────────────────┐ ┌────────────────────┐│
│  │  Main content            │ │  InsightPanel      ││
│  │  (DataTable, charts,     │ │  (right sidebar    ││
│  │   forms)                 │ │   — AI insights,   ││
│  │                          │ │   quick stats)     ││
│  └──────────────────────────┘ └────────────────────┘│
└─────────────────────────────────────────────────────┘
```

**Platform Tab Layout:**
Used on pages with multi-platform data (e.g., advertising across multiple ad accounts). `PlatformTabLayout` renders platform filter tabs above feature navigation tabs, then the page content.

### Key UI Components

| Component | Purpose |
|-----------|---------|
| `DataTable<T>` | Generic paginated table with sort, filter, loading skeleton, empty state |
| `MetricCard` | KPI card with value, trend indicator, sparkline data |
| `StatusBadge` | Semantic status chip: active/draft/completed/error/syncing/warning |
| `PageShell` | 3-zone layout: MetricBar + content + InsightPanel |
| `Modal` | Controlled dialog with backdrop |
| `CommandPalette` | Cmd+K search with keyboard navigation |
| `FilterBar` | Search input + filter dropdowns + action buttons |

### Custom Hooks

| Hook | Purpose |
|------|---------|
| `usePlatformFilter` | Persists active platform filter in URL query params |
| `useSidebarState` | Collapsed/expanded state in localStorage |
| `useCommerceWebSocket` | WebSocket connection for real-time order updates |

### Design System

- **Primary color:** coral
- **Semantic palette:** success (green), warning (amber), danger (red), info (blue), purple
- **Animations:** Framer Motion — fade and spring presets, 150ms transitions
- **Shadows:** `shadow-card`, `shadow-panel`, `shadow-modal`
- **Utility merging:** `cn()` = `clsx()` + `twMerge()` for conditional Tailwind classes

---

## 10. SDK Sidecar

### Why It Exists

TikTok's official Shop API SDK (which handles HMAC-SHA256 request signing) is published only as a Node.js package. The signing algorithm is complex — it requires sorting query parameters, building a canonical string from app_secret + path + sorted params + body, then computing HMAC-SHA256. Reimplementing this in Python risks subtle bugs that cause all Shop API calls to fail silently.

The sidecar approach keeps the official SDK in its native environment while allowing the Python backend to offload signing entirely.

### How It Works

```
Backend service layer
        │
        │  HTTP POST to http://localhost:4000/sign-request
        │  Body: { method, path, params, body, access_token }
        │  Header: Authorization: Bearer {sidecar_auth_token}
        ▼
TikTok Shop SDK Sidecar (Node.js + Fastify, port 4000)
        │
        │  Signs request using @tiktok-api/shop-sdk
        │  Returns: { signed_url, headers }
        ▼
Backend issues signed HTTP request to TikTok Shop API
```

### Sidecar Authentication

The sidecar accepts requests only with a shared secret (`sidecar_auth_token` in `.env`). This is a service-to-service token — never exposed to the browser.

### Integration Points

- **Client class:** `backend/tiktok/shop/sdk_client.py` — `TikTokShopSDKClient`
- **Sidecar source:** `tiktok-shop-sdk/src/`
- **Framework:** Fastify (Node.js 20) for minimal overhead
- **Health endpoint:** `GET /health` (checked by Docker Compose)
- **Config:** `TIKTOK_SHOP_SDK_URL` and `SIDECAR_AUTH_TOKEN` env vars

### Alternative: Direct Python Client

`TikTokShopClient` (`backend/tiktok/shop/client.py`) implements HMAC signing directly in Python for use cases where the sidecar is not available or for testing. The gateway can use either client.

---

## 11. Infrastructure

### Docker Compose Layout

All six services share a single Docker Compose file at the project root. The Python services (`api`, `celery-worker`, `celery-beat`) all build from the same `Dockerfile` at the project root — they differ only in their `command`.

```yaml
# Service dependency graph
postgres  ──►
redis     ──►  api  ──►  (clients)
tiktok-shop-sdk ──►
               ├──► celery-worker
               └──► celery-beat
```

### Volume Mounts (Development)

In development, the project root is mounted as a volume into the `api` and worker containers (`.:/app`). This enables hot-reload without rebuilding images on every code change.

### Networking

All services are on the default Docker Compose bridge network. Services reference each other by service name:
- Backend connects to postgres at `postgres:5432`
- Backend connects to redis at `redis:6379`
- Backend connects to sidecar at `tiktok-shop-sdk:4000`

### Environment Variables

All configuration passes through `.env` at the project root, loaded by Docker Compose `env_file: .env`. See `backend/config.py` for the full list and types. Never commit `.env` — use `.env.example` as the template.

Critical production variables:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | FastAPI app secret (32+ random bytes) |
| `JWT_SECRET_KEY` | JWT signing key (separate from app secret) |
| `TOKEN_VAULT_KEY` | Base64-encoded 32-byte AES-256-GCM key for token encryption |
| `DATABASE_URL` | PostgreSQL connection string (asyncpg driver) |
| `REDIS_URL` | Redis connection string |
| `SIDECAR_AUTH_TOKEN` | Service-to-service token for SDK sidecar |
| `TIKTOK_SHOP_APP_KEY` | TikTok Shop app credentials |
| `TIKTOK_SHOP_APP_SECRET` | TikTok Shop app credentials |
| `TIKTOK_DEVELOPER_CLIENT_KEY` | Developer platform credentials |
| `TIKTOK_DEVELOPER_CLIENT_SECRET` | Developer platform credentials |
| `TIKTOK_MARKETING_APP_ID` | Marketing API credentials |
| `TIKTOK_MARKETING_APP_SECRET` | Marketing API credentials |

### Scaling Considerations

For production beyond Docker Compose:

| Component | Scaling Strategy |
|-----------|----------------|
| FastAPI backend | Horizontal: multiple instances behind load balancer |
| Celery workers | Horizontal: additional worker containers, increase `--concurrency` |
| Celery beat | Vertical only: single instance required |
| PostgreSQL | Vertical initially; read replicas for analytics queries |
| Redis | Redis Cluster or Redis Sentinel for HA |

---

## 12. Security Architecture

### Frodo User Authentication

JWT-based with two token types:

| Token | Algorithm | Lifetime | Delivery |
|-------|-----------|---------|---------|
| Access token | HS256 | 15 minutes | HTTP Authorization Bearer header |
| Refresh token | HS256 | 7 days | HttpOnly cookie |

JWT payload claims:
- `sub` — user UUID
- `organization_id` — org UUID (from `get_org_membership` dependency)
- `role` — RBAC role string
- `type` — "access" or "refresh" (validated in `get_current_user`)

### RBAC (Role-Based Access Control)

Five-tier role hierarchy in `backend/auth/rbac.py`:

```
OWNER > ADMIN > MANAGER > MEMBER > VIEWER
```

Roles are stored on the `Membership` record, scoped to organization+workspace. `require_role()` decorator enforces minimum role on sensitive routes. Fine-grained `permissions` JSONB on Membership allows per-user overrides beyond role defaults.

### Social Authentication

`backend/auth/social.py` — `SocialAuthService`:
- TikTok Login OAuth (distinct from TikTok platform connections)
- Google OAuth
- Creates or links `SocialIdentity` records to existing users by email

### TikTok Platform Token Security

All platform access and refresh tokens are encrypted at rest using AES-256-GCM before being stored in the `token_vault` table:

```
Plaintext token
       ↓
AES-256-GCM encrypt (key from TOKEN_VAULT_KEY env var)
       ↓
BYTEA column in PostgreSQL (access_token_enc, refresh_token_enc)
```

The encryption key itself should be stored in AWS Secrets Manager or HashiCorp Vault in production — never in the `.env` file on the server.

Token rotation:
- Celery Beat triggers refresh before expiry (Developer: 12h, Shop: 24h, Marketing: daily check)
- On refresh failure: increment `refresh_failure_count`, record `last_refresh_error`, mark account `status=error` after threshold
- User sees error state in dashboard and is prompted to reconnect

### Tenant Isolation

```
Request arrives with X-Workspace-Id header
         ↓
TenantMiddleware validates and injects workspace context
         ↓
get_workspace_id() dependency provides UUID to route handlers
         ↓
Every DB query in services filters WHERE workspace_id = :wid
         ↓
(Future) PostgreSQL RLS as defense-in-depth layer
```

### Webhook Signature Verification

All inbound webhooks from TikTok are signature-verified before processing. Signature validity is recorded in `webhook_events.signature_valid`. Events with `signature_valid=False` are logged but not processed.

### Audit Logging

Every user-initiated action writes to `audit_log` with:
- `organization_id`, `workspace_id`, `user_id`
- `action` (e.g., `order.fulfill`, `campaign.create`)
- `resource_type` and `resource_id`
- `details` JSONB for action parameters
- `ip_address` (INET type for both IPv4 and IPv6)

### Security Scanning

- Static analysis: `bandit -r backend/` in CI
- Secrets: `pydantic-settings` fails fast on missing required env vars (no defaults in production)
- No plaintext tokens in logs — crypto utilities sanitize output
- CORS: `allow_origins` restricted to `FRONTEND_URL` env var value only

---

## Appendix: Scale Metrics

| Metric | Count |
|--------|-------|
| Backend Python files | ~223 |
| Frontend pages | 70 |
| UI components | 20 |
| DB model files | 18 |
| DB entity classes | 120+ |
| API endpoints | 220+ |
| Celery periodic tasks | 24 |
| Tests | 879 (842 unit + 37 integration) |
| Test coverage target | 80%+ |

## Appendix: Key File Index

| File | Purpose |
|------|---------|
| `backend/main.py` | App factory, router registration, middleware stack |
| `backend/config.py` | All env vars via pydantic-settings (23 fields) |
| `backend/dependencies.py` | FastAPI DI: CurrentUser, DBSession, get_org_membership |
| `backend/db/models/base.py` | SQLAlchemy declarative base, UUIDMixin, TimestampMixin |
| `backend/db/models/*.py` | 18 model files, one per domain |
| `backend/tiktok/gateway.py` | PlatformGateway — unified API facade |
| `backend/tiktok/rate_limiter.py` | Redis token-bucket rate limiter |
| `backend/tiktok/circuit_breaker.py` | Per-platform circuit breaker |
| `backend/tiktok/retry.py` | Exponential backoff retry decorator |
| `backend/workers/celery_app.py` | Celery config + 24 beat schedules |
| `backend/utils/crypto.py` | AES-256-GCM encrypt/decrypt for token vault |
| `backend/auth/rbac.py` | Role enum, has_permission, require_role |
| `frontend/src/lib/api.ts` | 1638-line typed API client (100+ functions) |
| `frontend/src/lib/auth.ts` | Token management: getAccessToken, setTokens, clearTokens |
| `frontend/src/app/(dashboard)/layout.tsx` | Auth guard + workspace context provider |
| `frontend/src/config/navigation.ts` | Sidebar navigation config |
| `tiktok-shop-sdk/src/` | Fastify sidecar for TikTok Shop HMAC signing |
| `docker-compose.yml` | 6-service stack definition |
| `alembic.ini` | Alembic migration config |
| `.env.example` | Environment variable template |

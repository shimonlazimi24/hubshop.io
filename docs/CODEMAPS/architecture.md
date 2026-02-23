# Frodo Architecture Codemap

> Freshness: 2026-02-23 | Auto-generated

## System Overview

```
                    +-------------------+
                    |   Next.js 15 FE   |
                    |   (port 3000)     |
                    +--------+----------+
                             |
                    +--------v----------+
    Webhooks ------>|   FastAPI API      |
    (TikTok)       |   (port 8000)     |
                    +---+-------+-------+
                        |       |
              +---------+       +---------+
              v                           v
    +---------+--------+      +-----------+---------+
    | PostgreSQL 16    |      | Redis 7             |
    | (port 5432)      |      | (port 6379)         |
    | 120+ models      |      | cache/broker/limits |
    +------------------+      +-----+-----+---------+
                                    |     |
                              +-----+     +-----+
                              v                 v
                    +---------+------+  +-------+--------+
                    | Celery Worker  |  | Celery Beat    |
                    | (concurrency 4)|  | (single inst.) |
                    +----------------+  +----------------+
```

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Next.js (App Router) + TypeScript + Tailwind | 16.1.6 |
| Backend | Python + FastAPI + SQLAlchemy async | 3.12+ |
| Database | PostgreSQL | 16 |
| Cache/Broker | Redis | 7 |
| Workers | Celery (worker + beat) | latest |
| Migrations | Alembic | latest |
| Auth | JWT (python-jose) + bcrypt | - |
| Infra | Docker Compose | - |

## Platform Integrations (5)

| Platform | Client | Auth | Base URL |
|----------|--------|------|----------|
| TikTok Shop | `shop_client.py` | HMAC-SHA256 + access token (7d) | `open-api.tiktokglobalshop.com` |
| TikTok Developer | `developer_client.py` | OAuth 2.0 Bearer (24h/365d refresh) | `open.tiktokapis.com/v2` |
| TikTok Marketing | `marketing_client.py` | OAuth 2.0 long-term token | `business-api.tiktok.com/open_api/v1.3` |
| TikTok Research | `research_client.py` | Client credentials OAuth | `open.tiktokapis.com/v2/research` |
| TikTok LIVE | `live_client.py` | WebSocket (no auth) | TikTokLive library |

## Infrastructure Patterns

- **Rate Limiter**: Redis token bucket per platform/account (Shop 50 QPS, Developer 10 QPS, Research 5 QPS)
- **Circuit Breaker**: 5-failure threshold, 30s recovery, states: CLOSED -> OPEN -> HALF_OPEN
- **Retry**: Exponential backoff, 3 retries, retryable: 429/500/502/503/504
- **Gateway**: Unified `PlatformGateway` composing rate limiter + circuit breaker + retry

## Middleware Stack

1. `RequestLoggingMiddleware` - 8-char UUID request tracing, timing
2. `TenantMiddleware` - `X-Workspace-Id` header -> multi-tenant isolation
3. `CORSMiddleware` - Configurable origins

## Auth & RBAC

- JWT access (15min) + refresh (7d) tokens
- Social OAuth: TikTok, Google
- Role hierarchy: VIEWER < MEMBER < MANAGER < ADMIN < OWNER
- Token vault: AES-256-GCM encrypted platform tokens

## Module Map (11 business modules)

| Module | Route Prefix | Endpoints | Description |
|--------|-------------|-----------|-------------|
| auth | `/api/auth` | 4 | Login, register, refresh, profile |
| connect | `/api/connect` | 3 | OAuth flows, account management |
| commerce | `/api/commerce` | 43+ | Shops, products, orders, fulfillment, returns, analytics, affiliate, promotions, finance |
| advertising | `/api/ads` | 96+ | Campaigns, ad groups, ads, reports, audiences, pixels, catalogs, search, symphony, split tests |
| content | `/api/content` | 9+ | Videos, publishing, calendar |
| creators | `/api/creators` | 14+ | Discovery, campaigns, invitations, Spark Ads |
| analytics | `/api/analytics` | 24+ | KPIs, reports, notifications, API keys |
| intelligence | `/api/intelligence` | 13+ | Trends, competitors, research |
| live | `/api/live` | 9+ | Sessions, analytics, monitoring |
| messaging | `/api/messaging` | 11+ | Conversations, auto-messages |
| organic | `/api/organic` | 15+ | Mentions, keywords, comments |
| webhooks | `/webhooks` | 1 | Platform webhook ingestion |

## Worker Tasks (24 periodic)

| Schedule | Tasks |
|----------|-------|
| Every 15-30 min | Orders sync, products sync, campaigns/ads sync, conversations, reports |
| Every 1-2h | Analytics aggregation, session cleanup, brand mentions |
| Every 4-6h | Trends, competitors, video metrics, ad accounts, settlements |
| Every 12-24h | Token refresh (Developer/Shop/Marketing), creator profiles, KPI snapshots |

## Scale Metrics

| Metric | Count |
|--------|-------|
| Backend Python files | ~203 |
| Frontend pages | 74 |
| UI components | 20 |
| DB models | 120+ |
| API endpoints | 220+ |
| Celery tasks | 24 periodic |
| Tests | 878 (841 unit + 37 integration) |

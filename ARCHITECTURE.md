# Frodo Architecture Plan: Unified TikTok SaaS Platform

## Context

TikTok's ecosystem is fragmented across 4 completely separate platforms (Shop, Developer, Marketing, LIVE) with no cross-authentication, different signing mechanisms, different webhook formats, and different rate limits. Agencies managing brands on TikTok must juggle 3+ dashboards, 3+ developer portals, and 3+ sets of credentials.

**Frodo** solves this by building the unification layer that TikTok itself doesn't provide: a single SaaS dashboard where agencies connect all their TikTok accounts once and manage commerce, advertising, content, and creator partnerships from one place.

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | **Python 3.12 + FastAPI** | Async-native, type hints, OpenAPI generation |
| Database | **PostgreSQL 16** | Multi-tenant via RLS, JSONB for flexible platform data |
| Cache/Broker | **Redis 7** | Token cache, Celery broker, rate-limit counters, pub/sub |
| Task Queue | **Celery 5** | Token refresh, data sync, report generation |
| Frontend | **Next.js 15 (App Router)** | RSC, middleware auth, modern React |
| Object Storage | **S3 / Cloudflare R2** | Media, async reports |
| Secrets | **AWS Secrets Manager / Vault** | Encrypted token vault keys |
| Deploy | **Docker + Kubernetes** | Horizontal scaling |

---

## System Architecture

```
                     +--------------------+
                     |  Next.js Frontend  |
                     +--------+-----------+
                              |
                     +--------v-----------+
                     |  FastAPI Backend    |
                     |  (Auth + RBAC +    |
                     |   Rate Limiting)   |
                     +--------+-----------+
                              |
            +-----------------+------------------+
            |                 |                  |
    +-------v------+  +------v-------+  +-------v------+
    | Core Modules |  | Celery       |  | Webhook      |
    | - Commerce   |  | Workers      |  | Ingestion    |
    | - Advertising|  | - Token      |  | - /shop      |
    | - Content    |  |   refresh    |  | - /developer |
    | - Creators   |  | - Data sync  |  | - /marketing |
    | - Analytics  |  | - Reports    |  |              |
    +-------+------+  +------+-------+  +------+-------+
            |                |                  |
    +-------v----------------v------------------v-------+
    |          TikTok Platform Client Layer             |
    |  Shop (HMAC)  |  Developer (Bearer)  |  Marketing |
    |               |                      | (Custom Hdr)|
    +---------------------------------------------------+
            |                |                  |
    +-------v----+   +------v------+   +-------v-------+
    | PostgreSQL |   |    Redis    |   | S3 / R2       |
    +------------+   +-------------+   +---------------+
```

---

## 1. Unified Auth Layer

### Frodo User Auth
- Standard JWT (15min access, 7d refresh, HttpOnly cookies)
- Claims: `user_id`, `organization_id`, `role`

### TikTok Account Connection
Each platform gets its own `/connect/{platform}/authorize` + `/connect/{platform}/callback` pair:

| Platform | Auth URL | Token Exchange | Token Storage |
|----------|----------|---------------|---------------|
| **Shop** | `services.tiktokshops.us/open/authorize?service_id=X` | `GET auth.tiktok-shops.com/api/v2/token/get` | AES-256 encrypted. Also stores `shop_cipher` array. |
| **Developer** | `tiktok.com/v2/auth/authorize/` | `POST open.tiktokapis.com/v2/oauth/token/` | AES-256 encrypted |
| **Marketing** | Redirect to TikTok Ads auth page | `POST business-api.tiktok.com/open_api/v1.3/oauth2/access_token/` | AES-256 encrypted |

### Token Refresh Schedule (Celery Beat)

| Platform | Schedule | Token Expiry | Action |
|----------|----------|-------------|--------|
| Developer | Every 12h | 24h access, 365d refresh | Refresh access token, replace refresh token |
| Shop | Every 24h | 7d access, seller-set refresh | Refresh access token, replace refresh token |
| Marketing | Daily health check | Long-term (no expiry) | Verify token validity via API call |

**Failure handling:** 3 retries with backoff. After persistent failure, mark account `status=error`, notify user in dashboard.

### Cross-Platform Identity Linking
No TikTok API for this. User manually links accounts in Frodo UI. Stored as `identity_group_id` UUID on `connected_accounts` table.

---

## 2. API Gateway / Abstraction Layer

### Three Signing Mechanisms

```python
# Shop: HMAC-SHA256 query signing + x-tts-access-token header
class TikTokShopClient:
    base_url = "https://open-api.tiktokglobalshop.com"
    # Signs: HMAC-SHA256(app_secret, app_secret + path + sorted_params + body + app_secret)

# Developer: Standard Bearer token
class TikTokDeveloperClient:
    base_url = "https://open.tiktokapis.com/v2"
    # Header: Authorization: Bearer {access_token}

# Marketing: Custom header
class TikTokMarketingClient:
    base_url = "https://business-api.tiktok.com/open_api/v1.3"
    # Header: Access-Token: {access_token}
```

### Middleware Chain
Each client call passes through:
1. **Rate Limiter** (Redis token bucket) - Shop: 50 QPS, Developer: 600/min, Marketing: varies
2. **Circuit Breaker** - Open after 5 failures in 60s, half-open after 30s, per-platform isolation
3. **Retry** - Exponential backoff (1s, 2s, 4s), max 3 retries, only for 429/5xx

---

## 3. Data Model (Key Tables)

### Multi-Tenancy: `Organization > Workspace > Members`
- Shared DB + shared schema, `workspace_id` FK on all tenant-scoped tables
- PostgreSQL Row-Level Security for isolation
- Roles: `owner`, `admin`, `manager`, `member`, `viewer`

### Core Tables

```
organizations          -- Agency/brand accounts
workspaces             -- Sub-accounts within org (e.g., per brand)
users                  -- Frodo platform users
memberships            -- user <-> org/workspace with role

connected_accounts     -- TikTok platform connections (platform enum: shop/developer/marketing/live)
token_vault            -- Encrypted tokens per connected_account
platform_app_credentials -- Our TikTok app credentials (one per platform)

shops                  -- TikTok shops (from connected shop accounts)
products               -- Synced product catalog from Shop API
orders                 -- Synced orders with status tracking

ad_accounts            -- TikTok ad accounts (from marketing connections)
campaigns              -- Synced campaigns with metrics snapshots
ad_groups              -- Synced ad groups
ads                    -- Synced ads with creative data

tiktok_videos          -- Videos from Developer Display API
creator_profiles       -- Creators from TTCM/TikTok One

webhook_events         -- Immutable log of all webhook events (with idempotency key)
audit_log              -- User action audit trail
```

### Database Schema (SQL)

```sql
-- ============================================================
-- IDENTITY & MULTI-TENANCY
-- ============================================================

CREATE TABLE organizations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(100) UNIQUE NOT NULL,
    plan            VARCHAR(50) NOT NULL DEFAULT 'trial',
    settings        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE workspaces (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(100) NOT NULL,
    settings        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (organization_id, slug)
);

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(320) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    avatar_url      VARCHAR(1024),
    is_active       BOOLEAN NOT NULL DEFAULT true,
    email_verified  BOOLEAN NOT NULL DEFAULT false,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE memberships (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    workspace_id    UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    role            VARCHAR(50) NOT NULL DEFAULT 'member',
    permissions     JSONB NOT NULL DEFAULT '[]',
    invited_by      UUID REFERENCES users(id),
    accepted_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, organization_id, workspace_id)
);

-- ============================================================
-- TIKTOK CONNECTED ACCOUNTS & TOKEN VAULT
-- ============================================================

CREATE TYPE tiktok_platform AS ENUM ('shop', 'developer', 'marketing', 'live');

CREATE TABLE connected_accounts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id        UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    platform            tiktok_platform NOT NULL,
    platform_user_id    VARCHAR(255),
    platform_user_name  VARCHAR(255),
    platform_entity_type VARCHAR(50),
    identity_group_id   UUID,
    scopes              TEXT[] NOT NULL DEFAULT '{}',
    region              VARCHAR(10),
    status              VARCHAR(50) NOT NULL DEFAULT 'active',
    last_synced_at      TIMESTAMPTZ,
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (workspace_id, platform, platform_user_id)
);

CREATE INDEX idx_connected_accounts_workspace ON connected_accounts(workspace_id);
CREATE INDEX idx_connected_accounts_identity ON connected_accounts(identity_group_id);

CREATE TABLE token_vault (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connected_account_id    UUID NOT NULL REFERENCES connected_accounts(id) ON DELETE CASCADE,
    access_token_enc        BYTEA NOT NULL,
    refresh_token_enc       BYTEA,
    access_token_expires_at     TIMESTAMPTZ,
    refresh_token_expires_at    TIMESTAMPTZ,
    shop_ciphers            JSONB,
    last_refreshed_at       TIMESTAMPTZ,
    refresh_failure_count   INT NOT NULL DEFAULT 0,
    last_refresh_error      TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE platform_app_credentials (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform        tiktok_platform NOT NULL,
    environment     VARCHAR(20) NOT NULL DEFAULT 'production',
    app_key_enc     BYTEA NOT NULL,
    app_secret_enc  BYTEA NOT NULL,
    redirect_uri    VARCHAR(512) NOT NULL,
    service_id      VARCHAR(255),
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- TIKTOK SHOP DATA
-- ============================================================

CREATE TABLE shops (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connected_account_id UUID NOT NULL REFERENCES connected_accounts(id) ON DELETE CASCADE,
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    tiktok_shop_id  VARCHAR(100) NOT NULL,
    shop_cipher     VARCHAR(255) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    region          VARCHAR(10) NOT NULL,
    seller_type     VARCHAR(50),
    shop_code       VARCHAR(50),
    status          VARCHAR(50),
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (workspace_id, tiktok_shop_id)
);

CREATE TABLE products (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id             UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    workspace_id        UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    tiktok_product_id   VARCHAR(100) NOT NULL,
    title               VARCHAR(1000),
    description         TEXT,
    status              VARCHAR(50),
    category_id         VARCHAR(100),
    category_name       VARCHAR(500),
    images              JSONB,
    skus                JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    synced_at           TIMESTAMPTZ,
    UNIQUE (shop_id, tiktok_product_id)
);
CREATE INDEX idx_products_workspace ON products(workspace_id);

CREATE TABLE orders (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id             UUID NOT NULL REFERENCES shops(id) ON DELETE CASCADE,
    workspace_id        UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    tiktok_order_id     VARCHAR(100) NOT NULL,
    order_status        VARCHAR(50) NOT NULL,
    payment_status      VARCHAR(50),
    total_amount        DECIMAL(14, 2),
    currency            VARCHAR(10),
    buyer_message       TEXT,
    shipping_provider   VARCHAR(100),
    tracking_number     VARCHAR(255),
    line_items          JSONB,
    order_created_at    TIMESTAMPTZ,
    order_updated_at    TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    synced_at           TIMESTAMPTZ,
    UNIQUE (shop_id, tiktok_order_id)
);
CREATE INDEX idx_orders_workspace ON orders(workspace_id);
CREATE INDEX idx_orders_status ON orders(workspace_id, order_status);

-- ============================================================
-- TIKTOK ADS DATA
-- ============================================================

CREATE TABLE ad_accounts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connected_account_id UUID NOT NULL REFERENCES connected_accounts(id) ON DELETE CASCADE,
    workspace_id        UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    tiktok_advertiser_id VARCHAR(100) NOT NULL,
    name                VARCHAR(255),
    currency            VARCHAR(10),
    timezone            VARCHAR(100),
    status              VARCHAR(50),
    balance             DECIMAL(14, 2),
    business_center_id  VARCHAR(100),
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (workspace_id, tiktok_advertiser_id)
);

CREATE TABLE campaigns (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ad_account_id       UUID NOT NULL REFERENCES ad_accounts(id) ON DELETE CASCADE,
    workspace_id        UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    tiktok_campaign_id  VARCHAR(100) NOT NULL,
    name                VARCHAR(255),
    objective_type      VARCHAR(50),
    budget_mode         VARCHAR(50),
    budget              DECIMAL(14, 2),
    status              VARCHAR(50),
    campaign_type       VARCHAR(50),
    metrics_snapshot    JSONB,
    metrics_updated_at  TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    synced_at           TIMESTAMPTZ,
    UNIQUE (ad_account_id, tiktok_campaign_id)
);
CREATE INDEX idx_campaigns_workspace ON campaigns(workspace_id);

CREATE TABLE ad_groups (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id         UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    workspace_id        UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    tiktok_adgroup_id   VARCHAR(100) NOT NULL,
    name                VARCHAR(255),
    status              VARCHAR(50),
    bid_strategy        VARCHAR(50),
    budget              DECIMAL(14, 2),
    targeting           JSONB,
    placements          JSONB,
    schedule            JSONB,
    metrics_snapshot    JSONB,
    metrics_updated_at  TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    synced_at           TIMESTAMPTZ
);

CREATE TABLE ads (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ad_group_id         UUID NOT NULL REFERENCES ad_groups(id) ON DELETE CASCADE,
    workspace_id        UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    tiktok_ad_id        VARCHAR(100) NOT NULL,
    name                VARCHAR(255),
    ad_format           VARCHAR(50),
    status              VARCHAR(50),
    creative            JSONB,
    identity_type       VARCHAR(50),
    landing_page_url    VARCHAR(2048),
    is_spark_ad         BOOLEAN NOT NULL DEFAULT false,
    metrics_snapshot    JSONB,
    metrics_updated_at  TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    synced_at           TIMESTAMPTZ
);

-- ============================================================
-- TIKTOK CONTENT & CREATOR DATA
-- ============================================================

CREATE TABLE tiktok_videos (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connected_account_id UUID NOT NULL REFERENCES connected_accounts(id) ON DELETE CASCADE,
    workspace_id        UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    tiktok_video_id     VARCHAR(100) NOT NULL,
    title               VARCHAR(500),
    description         TEXT,
    duration            INT,
    cover_url           VARCHAR(2048),
    share_url           VARCHAR(2048),
    like_count          BIGINT DEFAULT 0,
    comment_count       BIGINT DEFAULT 0,
    share_count         BIGINT DEFAULT 0,
    view_count          BIGINT DEFAULT 0,
    published_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    synced_at           TIMESTAMPTZ
);

CREATE TABLE creator_profiles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id        UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    tiktok_creator_id   VARCHAR(100) NOT NULL,
    nickname            VARCHAR(255),
    avatar_url          VARCHAR(2048),
    follower_count      BIGINT,
    engagement_rate     DECIMAL(6, 3),
    avg_views           BIGINT,
    content_categories  TEXT[],
    country             VARCHAR(10),
    audience_demographics JSONB,
    collaboration_status VARCHAR(50),
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- WEBHOOK EVENT LOG & AUDIT
-- ============================================================

CREATE TABLE webhook_events (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id        UUID REFERENCES workspaces(id),
    platform            tiktok_platform NOT NULL,
    event_type          VARCHAR(100) NOT NULL,
    platform_event_id   VARCHAR(255),
    raw_payload         JSONB NOT NULL,
    signature_valid     BOOLEAN NOT NULL,
    status              VARCHAR(50) NOT NULL DEFAULT 'received',
    processed_at        TIMESTAMPTZ,
    error_message       TEXT,
    received_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    idempotency_key     VARCHAR(255) UNIQUE
);
CREATE INDEX idx_webhook_events_workspace ON webhook_events(workspace_id, received_at DESC);
CREATE INDEX idx_webhook_events_platform ON webhook_events(platform, event_type);

CREATE TABLE audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    workspace_id    UUID REFERENCES workspaces(id),
    user_id         UUID REFERENCES users(id),
    action          VARCHAR(100) NOT NULL,
    resource_type   VARCHAR(100),
    resource_id     VARCHAR(255),
    details         JSONB,
    ip_address      INET,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_log_org ON audit_log(organization_id, created_at DESC);
```

---

## 4. Webhook Ingestion

Three separate endpoints with platform-specific signature verification:

| Endpoint | Signature Location | Verification |
|----------|-------------------|-------------|
| `POST /webhooks/shop` | `Authorization` header | `HMAC-SHA256(app_secret, app_key + body)` |
| `POST /webhooks/developer` | `TikTok-Signature` header | Parse `t=TS,s=SIG`, verify `HMAC-SHA256(client_secret, TS.body)` |
| `POST /webhooks/marketing` | Subscription-specific | Verify per subscription config |

### Processing Pipeline
```
Receive -> Verify signature -> Deduplicate (Redis SETNX on idempotency key)
  -> Store in webhook_events (status=received)
  -> Enqueue Celery task
  -> Worker: parse + route to domain handler + update local DB + publish to Redis pub/sub
  -> Mark processed
```

### Webhook-to-Domain Mapping

| Platform | Event | Handler |
|----------|-------|---------|
| Shop type=1 | Order Status Change | `commerce.handle_order_update` |
| Shop type=5 | Product Status Change | `commerce.handle_product_update` |
| Shop type=6 | Seller Deauthorization | `connect.handle_account_revoked` |
| Shop type=7 | Auth Expiring | `connect.handle_auth_expiring_warning` |
| Shop type=12 | Return Status Change | `commerce.handle_return_update` |
| Developer | authorization.removed | `connect.handle_account_revoked` |
| Developer | video.publish.completed | `content.handle_video_published` |
| Marketing | ad_account_status | `advertising.handle_account_status` |
| Marketing | campaign_status | `advertising.handle_campaign_update` |

### Critical: Polling Fallback
Never rely solely on webhooks. Celery periodic tasks poll for orders/products as reconciliation (every 5-15 min), catching any missed webhooks.

---

## 5. Core Modules

### Commerce (`/commerce/*`) - TikTok Shop
Products, orders, fulfillment, returns, promotions, affiliate management, finance.

Key endpoints:
| Endpoint | Description | TikTok API |
|----------|-------------|------------|
| `GET /commerce/shops` | List connected shops | Local DB |
| `GET /commerce/shops/{id}/products` | List products | Product API |
| `GET /commerce/shops/{id}/orders` | List orders | Order API |
| `POST /commerce/shops/{id}/orders/{oid}/fulfill` | Fulfill order | Fulfillment API |
| `GET /commerce/shops/{id}/returns` | List returns | Returns API |
| `GET /commerce/shops/{id}/finance/statements` | Financial data | Finance API |
| `GET /commerce/shops/{id}/affiliate/creators` | Affiliate creators | Affiliate Seller API |

### Advertising (`/ads/*`) - Marketing API
Ad accounts, campaigns/ad groups/ads CRUD, reporting (sync + async), audiences, Business Center management, GMV Max, Spark Ads.

Key endpoints:
| Endpoint | Description | TikTok API |
|----------|-------------|------------|
| `GET /ads/accounts` | List ad accounts | Marketing OAuth |
| `GET /ads/accounts/{id}/campaigns` | List campaigns | Campaign Management |
| `POST /ads/accounts/{id}/campaigns` | Create campaign | Campaign Management |
| `POST /ads/accounts/{id}/report` | Generate report | Reporting |
| `GET /ads/bc` | List Business Centers | BC Management |
| `POST /ads/bc/{id}/report` | BC-level report | BC Reporting |

### Content (`/content/*`) - Developer API
Video listing with metrics, content posting/upload, content calendar.

### Creators (`/creators/*`) - TikTok One/TTCM
Creator discovery, profile insights, campaign management, Spark Ads authorization, content linking.

### Analytics (`/analytics/*`) - Cross-platform
Unified overview KPIs, per-module drill-down, async export (CSV/Excel).

### Connect (`/connect/*`) - Account management
OAuth flows for all platforms, account listing/status, identity linking.

---

## 6. Project Structure

```
frodo/
|-- backend/
|   |-- main.py                    # FastAPI app factory
|   |-- config.py                  # pydantic-settings
|   |-- dependencies.py            # DI (DB sessions, current user)
|   |-- db/
|   |   |-- engine.py              # Async SQLAlchemy
|   |   |-- base.py                # Declarative base, common mixins
|   |   |-- models/                # ORM models (user, org, shop, ads, etc.)
|   |   |-- migrations/            # Alembic
|   |-- auth/
|   |   |-- router.py              # /auth/* endpoints
|   |   |-- service.py             # JWT creation/validation
|   |   |-- rbac.py                # Role-based access control
|   |-- tiktok/                    # Platform integration layer
|   |   |-- base_client.py         # Abstract base client
|   |   |-- exceptions.py          # TikTok API error types
|   |   |-- shop/
|   |   |   |-- client.py          # HMAC signing client
|   |   |   |-- auth.py            # Shop OAuth flow
|   |   |   |-- webhooks.py        # Shop webhook verification
|   |   |-- developer/
|   |   |   |-- client.py          # Bearer token client
|   |   |   |-- auth.py            # Developer OAuth flow
|   |   |   |-- webhooks.py        # Developer webhook verification
|   |   |-- marketing/
|   |   |   |-- client.py          # Custom header client
|   |   |   |-- auth.py            # Marketing OAuth flow
|   |   |   |-- webhooks.py        # Marketing webhook handling
|   |   |-- gateway.py             # Unified gateway
|   |   |-- rate_limiter.py        # Redis token bucket
|   |   |-- circuit_breaker.py     # Per-platform circuit breaker
|   |   |-- retry.py               # Exponential backoff retry
|   |-- modules/                   # Business domain modules
|   |   |-- connect/               # OAuth flows, account linking
|   |   |   |-- router.py
|   |   |   |-- service.py
|   |   |-- commerce/              # Shop operations
|   |   |   |-- router.py
|   |   |   |-- service.py
|   |   |   |-- sync.py            # Background sync tasks
|   |   |-- advertising/           # Marketing API operations
|   |   |   |-- router.py
|   |   |   |-- service.py
|   |   |   |-- reporting.py       # Report generation
|   |   |-- content/               # Developer API operations
|   |   |   |-- router.py
|   |   |   |-- service.py
|   |   |-- creators/              # TTCM/TikTok One
|   |   |   |-- router.py
|   |   |   |-- service.py
|   |   |-- analytics/             # Cross-platform analytics
|   |   |   |-- router.py
|   |   |   |-- service.py
|   |   |   |-- aggregators.py     # Cross-platform data aggregation
|   |   |-- webhooks/              # Webhook ingestion
|   |       |-- router.py          # /webhooks/{platform} endpoints
|   |       |-- handlers.py        # Platform-specific processing
|   |       |-- dispatcher.py      # Fan-out to internal consumers
|   |-- workers/                   # Celery tasks
|   |   |-- celery_app.py
|   |   |-- token_refresh.py       # Scheduled token refresh
|   |   |-- data_sync.py           # Periodic data synchronization
|   |   |-- report_generation.py   # Async report generation
|   |-- middleware/
|   |   |-- tenant.py              # Multi-tenant context
|   |   |-- logging.py             # Structured logging
|   |   |-- rate_limit.py          # Frodo API rate limiting
|   |-- utils/
|       |-- crypto.py              # AES-256-GCM encryption
|       |-- pagination.py          # Cursor/offset pagination
|       |-- time.py                # Timezone utilities
|-- frontend/
|   |-- src/app/
|   |   |-- layout.tsx
|   |   |-- (auth)/                # Login, register
|   |   |-- (dashboard)/
|   |       |-- layout.tsx         # Sidebar, topbar
|   |       |-- overview/          # Unified dashboard
|   |       |-- connect/           # Account connection wizard
|   |       |-- commerce/          # Shop management
|   |       |-- ads/               # Campaign management
|   |       |-- content/           # Content management
|   |       |-- creators/          # Creator marketplace
|   |       |-- analytics/         # Dashboards
|   |       |-- settings/          # Org, workspace, team settings
|   |-- components/
|   |-- hooks/
|   |-- lib/
|   |-- types/
|-- tests/
|   |-- conftest.py
|   |-- factories/                 # Test data factories
|   |-- unit/
|   |-- integration/
|   |-- e2e/
|-- knowledge-base/                # Existing research (60 files)
|-- docker-compose.yml
|-- pyproject.toml
|-- alembic.ini
|-- .env.example
```

---

## 7. MVP Phasing

### Phase 1: Foundation (Weeks 1-4)
- Project scaffolding (FastAPI, Postgres, Redis, Celery, Docker Compose, CI)
- DB schema: orgs, workspaces, users, memberships, connected_accounts, token_vault
- Frodo user auth (JWT), multi-tenancy middleware, RBAC
- TikTok Shop client (HMAC signing) + OAuth connect flow
- Token refresh worker
- Next.js scaffolding: login, register, dashboard layout, Shop connection wizard

**Deliverable:** User registers, creates org/workspace, connects TikTok Shop, sees shops listed.

### Phase 2: Commerce Core (Weeks 5-8)
- Product/order sync (background jobs + webhook-driven)
- Shop webhook ingestion with signature verification
- Commerce dashboard (products, orders, fulfillment, returns)
- Real-time order updates via WebSocket
- Commerce analytics (revenue, order volume, top products)

**Deliverable:** Agency manages all Shop operations from Frodo.

### Phase 3: Advertising (Weeks 9-12)
- Marketing API client + OAuth flow
- Ad account sync (including Business Center)
- Campaign hierarchy (campaigns > ad groups > ads) with metrics
- Reporting engine (sync + async)
- Ads dashboard + Business Center integration
- Marketing webhooks

**Deliverable:** Agency monitors/manages all ad campaigns from Frodo.

### Phase 4: Content & Developer (Weeks 13-16)
- Developer API client + OAuth flow
- Video sync with metrics
- Content posting/upload
- Content calendar
- Developer webhooks
- Cross-platform identity linking UI

**Deliverable:** Agency manages content and sees all TikTok properties linked per brand.

### Phase 5: Creator Marketplace (Weeks 17-20)
- TikTok One/TTCM API integration
- Creator discovery + profiles
- Campaign management + creator invitations
- Spark Ads flow (request auth -> create ad)

**Deliverable:** Agency discovers creators and turns content into Spark Ads.

### Phase 6: Unified Analytics & Polish (Weeks 21-24)
- Cross-platform unified dashboard
- Export/reporting (CSV, PDF, scheduled emails)
- Notification system, team management UI
- Billing (Stripe), performance optimization, security hardening

### Deferred Post-MVP
- LIVE Events API (partner-only access required)
- Effect House (no REST API)
- CapCut (no official API)
- Pangle, Search Ads, MMM (niche features)
- Mobile app, white-labeling, i18n

---

## 8. Key Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| TikTok API changes | Abstract all calls behind client interfaces. Pin API versions. Monitor changelogs. |
| Token refresh failures at scale | Exponential backoff, dead letter queue, proactive alerting, user re-auth notification |
| Rate limit exhaustion (50 QPS Shop) | Redis token bucket per account, request queuing with backpressure, batching |
| Multi-tenant data leakage | PostgreSQL RLS, workspace_id on every query, integration tests for isolation |
| Webhook delivery gaps | Polling fallback (Celery periodic tasks), reconciliation jobs |
| Secret/token leakage | AES-256-GCM encryption, secrets in Vault, audit logging, no plaintext in logs |

---

## 9. Verification Plan

1. **Unit tests** (80%+ coverage): HMAC signing, Bearer auth, webhook verification, JWT, RBAC, encrypt/decrypt
2. **Integration tests**: Full OAuth connect flow (mocked TikTok), sync pipelines, webhook processing, tenant isolation
3. **E2E tests** (Playwright): Register -> connect Shop -> view products -> fulfill order
4. **Security**: Bandit static analysis, penetration testing, CSP headers
5. **Load testing**: Verify rate limiter behavior under concurrent requests

# Production Readiness Checklist — Frodo Unified TikTok Platform

> Engineering handover document for taking Frodo from pre-production to production.
>
> **Version**: 0.1.0 | **Status**: Pre-production, actively developing | **Date**: 2026-03-04

---

## Table of Contents

1. [Current State Assessment](#1-current-state-assessment)
2. [Environment Setup](#2-environment-setup)
3. [Infrastructure Requirements](#3-infrastructure-requirements)
4. [Deployment Guide](#4-deployment-guide)
5. [Security Checklist](#5-security-checklist)
6. [Monitoring & Observability](#6-monitoring--observability)
7. [Performance Considerations](#7-performance-considerations)
8. [Data Management](#8-data-management)
9. [Production Readiness Checklist](#9-production-readiness-checklist)
10. [Recommended Production Timeline](#10-recommended-production-timeline)

---

## 1. Current State Assessment

### What Is Built and Working

Frodo is a unified TikTok SaaS platform for agencies. The following components are implemented and tested:

| Component | Status | Details |
|-----------|--------|---------|
| FastAPI backend | Built | Python 3.12, async SQLAlchemy, Pydantic v2 |
| Auth system | Built | JWT (HS256), RBAC (5 roles), social login (TikTok + Google) |
| Multi-tenancy | Built | Organization → Workspace → Membership hierarchy, `workspace_id` FK on all tables |
| PostgreSQL schema | Built | 18 model files, 120+ entity classes, Alembic migrations |
| Redis integration | Built | Token cache, Celery broker, rate-limit counters, pub/sub |
| Celery workers | Built | 20 periodic beat schedules, 12 worker modules |
| TikTok platform clients | Built | Shop (HMAC), Developer (Bearer), Marketing (custom header), Research, LIVE |
| API gateway | Built | Rate limiter (token bucket), circuit breaker, retry with exponential backoff |
| Token vault | Built | AES-256-GCM encryption per connected account |
| Webhook ingestion | Built | Signature verification for Shop, Developer, Marketing |
| Commerce module | Built | Products, orders, fulfillment, returns, promotions, affiliate, finance |
| Advertising module | Built | Campaigns, ad groups, ads, reporting, audiences, pixels, catalogs, Spark Ads |
| Content module | Built | Videos, publishing, calendar |
| Creators module | Built | Discovery, profiles, campaigns, invitations |
| Analytics module | Built | Cross-platform KPIs, scheduled reports, notifications |
| Intelligence module | Built | Trends, competitor tracking, Research API |
| LIVE module | Built | Stream monitoring, sessions, analytics |
| Messaging module | Built | Conversations, auto-messages |
| Organic module | Built | Brand mentions, keywords, comments |
| Next.js frontend | Built | 74 dashboard pages, 14 sidebar sections, component library |
| Node.js SDK sidecar | Built | TikTok Shop HMAC signing proxy (Fastify, port 4000) |

### Test Coverage

| Category | Count | Notes |
|----------|-------|-------|
| Total tests | **879** | All passing |
| Unit tests | 842 | Business logic, services, models, workers |
| Integration tests | 37 | Route integration, sync pipelines, webhooks, WebSocket |
| E2E tests | 0 | **Not yet written — Playwright suite needed** |

**By module:**

| Module | Tests |
|--------|-------|
| Advertising | 136 |
| Content | 68 |
| Creators | 55 |
| Commerce | 54 |
| Analytics | 47 |
| Intelligence | 42 |
| DB Models | 39 |
| TikTok Clients | 38 |
| Workers | 31 |
| LIVE | 26 |
| Organic | 17 |
| Messaging | 16 |
| Integration | 37 |

### What Has Been Validated

- Unit test coverage across all 11 domain modules
- Celery beat schedule configuration (20 tasks)
- Token vault encryption/decryption
- JWT creation/validation
- Multi-tenant data scoping patterns
- TikTok API client signing mechanisms
- Webhook signature verification

### What Remains Untested / Unfinished

- **End-to-end Playwright tests** — no E2E suite exists
- **TikTok app registration** — no real app_key/app_secret provisioned on TikTok portals
- **Production OAuth redirect URIs** — hardcoded to localhost
- **Load testing** — Celery concurrency, rate limiter behavior under concurrent requests
- **Penetration testing** — multi-tenant data isolation under adversarial conditions
- **Production UX** — no onboarding flow, rough error boundaries, no skeleton states
- **SDK sidecar integration tests** — Node.js sidecar not covered by test suite
- **Frontend test coverage** — zero frontend tests
- **Phase 7 Intelligence platform** — listed as next work item

---

## 2. Environment Setup

### All Required Environment Variables

All variables are loaded from `.env` via `backend/config.py` (pydantic-settings BaseSettings).

#### Application Core

| Variable | Description | Example / Format | Required |
|----------|-------------|-----------------|----------|
| `APP_NAME` | Application display name | `frodo` | Yes |
| `APP_ENV` | Environment tag | `production` | Yes |
| `DEBUG` | Enable debug mode. Disables API docs when `false` | `false` | Yes |
| `SECRET_KEY` | App-level secret key (CSRF, misc signing) | Random 64-char hex string | Yes |
| `FRONTEND_URL` | Frontend origin for CORS | `https://app.yourdomain.com` | Yes |
| `BACKEND_URL` | Backend base URL | `https://api.yourdomain.com` | Yes |

#### Database

| Variable | Description | Format | Required |
|----------|-------------|--------|----------|
| `DATABASE_URL` | PostgreSQL async connection string | `postgresql+asyncpg://user:pass@host:5432/frodo` | Yes |

#### Redis

| Variable | Description | Format | Required |
|----------|-------------|--------|----------|
| `REDIS_URL` | Redis for token cache, rate limits, pub/sub | `redis://host:6379/0` | Yes |

#### JWT Authentication

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `JWT_SECRET_KEY` | JWT signing secret | `change-me` (MUST change) | Yes |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `15` | Yes |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` | Yes |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` | Yes |

#### Token Vault

| Variable | Description | Format | Required |
|----------|-------------|--------|----------|
| `TOKEN_VAULT_KEY` | AES-256-GCM key for encrypting TikTok tokens in the DB | Base64-encoded 32-byte key | Yes |

Generate with: `python -c "import os, base64; print(base64.b64encode(os.urandom(32)).decode())"`

#### TikTok Platform Credentials

| Variable | Description | Required For |
|----------|-------------|-------------|
| `TIKTOK_SHOP_APP_KEY` | TikTok Shop application key | Commerce (Shop) features |
| `TIKTOK_SHOP_APP_SECRET` | TikTok Shop application secret | Commerce (Shop) features |
| `TIKTOK_DEVELOPER_CLIENT_KEY` | TikTok Developer client key | Content, organic, social login |
| `TIKTOK_DEVELOPER_CLIENT_SECRET` | TikTok Developer client secret | Content, organic, social login |
| `TIKTOK_MARKETING_APP_ID` | TikTok Marketing API app ID | Advertising features |
| `TIKTOK_MARKETING_APP_SECRET` | TikTok Marketing API app secret | Advertising features |
| `TIKTOK_RESEARCH_CLIENT_KEY` | TikTok Research API client key | Intelligence features |
| `TIKTOK_RESEARCH_CLIENT_SECRET` | TikTok Research API client secret | Intelligence features |

#### SDK Sidecar

| Variable | Description | Required |
|----------|-------------|----------|
| `TIKTOK_SHOP_SDK_URL` | Internal URL to Node.js HMAC sidecar | Yes (Shop features) |
| `SIDECAR_AUTH_TOKEN` | Auth token the Python backend uses to call the sidecar | Yes (Shop features) |

#### Social Login

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | For Google login |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | For Google login |
| `GOOGLE_REDIRECT_URI` | Google OAuth callback URL | For Google login |
| `TIKTOK_LOGIN_REDIRECT_URI` | TikTok social login callback URL | For TikTok login |

#### Celery

| Variable | Description | Format | Required |
|----------|-------------|--------|----------|
| `CELERY_BROKER_URL` | Redis database for Celery message broker | `redis://host:6379/1` | Yes |
| `CELERY_RESULT_BACKEND` | Redis database for Celery result storage | `redis://host:6379/2` | Yes |

> Note: Use separate Redis DB indexes for cache (0), broker (1), and results (2) to avoid key collisions.

### Secrets That Need Provisioning

Before launch, the following must be provisioned through a secrets manager (not `.env` files):

| Secret | How to Generate | Rotation Impact |
|--------|----------------|-----------------|
| `SECRET_KEY` | `openssl rand -hex 64` | Low — misc signing |
| `JWT_SECRET_KEY` | `openssl rand -hex 64` | **High** — all users must re-login |
| `TOKEN_VAULT_KEY` | `python -c "import os,base64; print(base64.b64encode(os.urandom(32)).decode())"` | **Critical** — requires re-encryption of all stored tokens |
| TikTok App credentials | From TikTok developer portals | Platform reconnection required |
| Google OAuth credentials | From Google Cloud Console | Users must re-authorize |
| Database password | Generated by managed DB service | Update `DATABASE_URL` |
| Redis auth password | Generated by managed Redis service | Update `REDIS_URL`, `CELERY_*` URLs |

### Third-Party Service Accounts Needed

| Service | Purpose | Where to Register |
|---------|---------|-------------------|
| TikTok Shop Partner Center | Shop API app registration, `app_key`/`app_secret` | https://partner.tiktokshop.com |
| TikTok Developer Portal | Developer API, social login, content/video scopes | https://developers.tiktok.com |
| TikTok Marketing API | Ads API registration | https://business-api.tiktok.com |
| TikTok Research API | Intelligence/trend data (approval required) | https://developers.tiktok.com/products/research-api |
| Google Cloud Console | Google OAuth 2.0 credentials | https://console.cloud.google.com |
| AWS / GCP / Azure | Managed PostgreSQL, Redis, container orchestration | Cloud provider of choice |
| Docker/container registry | Store and deploy Docker images | Docker Hub, ECR, GCR, etc. |
| Error tracking (Sentry) | Runtime error capture and alerting | https://sentry.io |
| Log aggregation (optional) | Centralized logs | Datadog, Papertrail, CloudWatch |

---

## 3. Infrastructure Requirements

### Recommended Production Infrastructure

Docker Compose is development-only. Production must use managed services and container orchestration.

#### Backend API — FastAPI

- **Deployment**: Kubernetes Deployment or AWS ECS (stateless, horizontally scalable)
- **Replicas**: Start with 2, scale to N based on load
- **Resources**: 512MB–1GB RAM per instance, 0.5–1 vCPU
- **Load balancer**: AWS ALB / GCP GLB / nginx ingress
- **Health endpoint**: `GET /health` → `{"status": "healthy", "version": "0.1.0"}`

#### PostgreSQL

- **Recommended**: AWS RDS PostgreSQL 16, GCP Cloud SQL, or Supabase
- **Sizing**: Start with db.t3.medium (2 vCPU, 4GB RAM) — scale vertical first
- **Storage**: 100GB SSD, with auto-scaling enabled
- **Connection pooling**: PgBouncer in transaction mode (target: 100 DB connections, 10× app connections)
- **Read replicas**: Add after initial launch for analytics queries
- **Backup**: Daily automated snapshots, 30-day retention, point-in-time recovery enabled
- **Multi-AZ**: Required for production HA
- **RLS**: Row-Level Security is defined in schema — verify it is enforced in production

#### Redis

- **Recommended**: AWS ElastiCache Redis 7, GCP Memorystore, Upstash Redis
- **Sizing**: Start with 1GB instance — monitor `used_memory` and scale before 80%
- **Persistence**: Enable AOF (`appendonly yes`) to survive restarts
- **Multi-AZ**: Enable replication with at least 1 replica
- **Separate DB indexes**: `/0` = app cache, `/1` = Celery broker, `/2` = Celery results
- **Memory policy**: `allkeys-lru` — allows Redis to evict cache when under memory pressure

#### Celery Workers

- **Deployment**: Separate Kubernetes Deployment (not the API pods)
- **Concurrency**: `--concurrency=4` per worker container
- **Scaling**: Start with 2 worker pods; add more for high-volume accounts
- **Resources**: 512MB RAM, 1 vCPU per worker pod
- **Beat scheduler**: Exactly **one** Celery Beat instance — never run multiple (causes duplicate task execution)

#### Node.js SDK Sidecar

- **Deployment**: Separate Kubernetes Deployment
- **Port**: 4000 (internal only, not exposed externally)
- **Purpose**: TikTok Shop HMAC signing proxy
- **Resources**: 256MB RAM, 0.25 vCPU
- **Auth**: Secured with `SIDECAR_AUTH_TOKEN`

#### Frontend — Next.js

- **Option A (recommended)**: Vercel — zero-config Next.js hosting, edge CDN, preview deployments
- **Option B**: Self-hosted on Kubernetes with nginx, or AWS CloudFront + S3 for static export
- **Build**: `npm run build` produces optimized production bundle
- **CDN**: Required for static assets (images, fonts, JS bundles)

#### Object Storage (Deferred)

- **When needed**: Media uploads, async report exports (CSV/Excel)
- **Recommended**: AWS S3 or Cloudflare R2
- **Not yet integrated** — noted in ARCHITECTURE.md as planned

---

## 4. Deployment Guide

### Step-by-Step: Zero to Running in Production

#### Step 1: Provision Secrets

```bash
# Generate all secrets before anything else
python -c "import os, base64; print('SECRET_KEY:', os.urandom(64).hex())"
python -c "import os, base64; print('JWT_SECRET_KEY:', os.urandom(64).hex())"
python -c "import os, base64; print('TOKEN_VAULT_KEY:', base64.b64encode(os.urandom(32)).decode())"
```

Store in AWS Secrets Manager, GCP Secret Manager, or HashiCorp Vault. Never write to `.env` in production.

#### Step 2: Provision Managed Infrastructure

1. Create managed PostgreSQL 16 instance (Multi-AZ, daily backups enabled)
2. Create managed Redis 7 instance (AOF persistence, 1 replica)
3. Create container registry (ECR / GCR / Docker Hub)
4. Configure DNS: `api.yourdomain.com` → backend, `app.yourdomain.com` → frontend

#### Step 3: Register TikTok Applications

For each platform, register your app and configure OAuth redirect URIs pointing to production:

| Platform | Redirect URI to Register |
|----------|--------------------------|
| TikTok Shop | `https://api.yourdomain.com/api/connect/shop/callback` |
| TikTok Developer | `https://api.yourdomain.com/api/connect/developer/callback` |
| TikTok Marketing | `https://api.yourdomain.com/api/connect/marketing/callback` |
| TikTok Login (social) | `https://api.yourdomain.com/api/auth/tiktok/callback` |
| Google OAuth | `https://api.yourdomain.com/api/auth/google/callback` |

Request full production scopes on each platform (see ARCHITECTURE.md section 2 for scope details).

#### Step 4: Build Docker Images

```bash
# From the project root
GIT_SHA=$(git rev-parse --short HEAD)

# Build backend/worker image
docker build -t frodo-api:${GIT_SHA} .

# Build SDK sidecar image
docker build -t frodo-sdk:${GIT_SHA} ./tiktok-shop-sdk

# Tag and push to registry
docker tag frodo-api:${GIT_SHA} <registry>/frodo-api:${GIT_SHA}
docker tag frodo-sdk:${GIT_SHA} <registry>/frodo-sdk:${GIT_SHA}
docker push <registry>/frodo-api:${GIT_SHA}
docker push <registry>/frodo-sdk:${GIT_SHA}
```

#### Step 5: Run Database Migrations

Always run migrations before deploying the new API version:

```bash
# Run as a one-off container with production env
docker run --rm \
  --env DATABASE_URL="${DATABASE_URL}" \
  <registry>/frodo-api:${GIT_SHA} \
  alembic upgrade head

# Verify
docker run --rm \
  --env DATABASE_URL="${DATABASE_URL}" \
  <registry>/frodo-api:${GIT_SHA} \
  alembic current
```

#### Step 6: Deploy Services

Deploy in this order to avoid race conditions:

1. **PostgreSQL** — already running (managed service)
2. **Redis** — already running (managed service)
3. **SDK Sidecar** (`frodo-sdk`) — must be up before API (API health depends on it)
4. **API** (`frodo-api`) — `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
5. **Celery Worker** — `celery -A backend.workers.celery_app worker --loglevel=info --concurrency=4`
6. **Celery Beat** — `celery -A backend.workers.celery_app beat --loglevel=info` (**exactly one instance**)
7. **Frontend** — deploy to Vercel or serve via CDN

#### Step 7: Smoke Test

```bash
# Health check
curl https://api.yourdomain.com/health
# Expected: {"status": "healthy", "version": "0.1.0"}

# Verify API docs are disabled
curl https://api.yourdomain.com/docs
# Expected: 404 (DEBUG=false disables OpenAPI docs)

# Verify CORS header
curl -H "Origin: https://app.yourdomain.com" https://api.yourdomain.com/health
# Expected: Access-Control-Allow-Origin header present
```

### Zero-Downtime Deployment Strategy

The API is stateless (sessions stored in JWT cookies, no in-memory state). Zero-downtime is achievable with:

1. **Rolling deployments**: Kubernetes rolling update or ECS rolling deployment
2. **Migration safety**: Only run additive migrations (new columns nullable or with defaults) for zero-downtime. Destructive changes require a maintenance window.
3. **Health check**: Load balancer drains existing connections from old pods before terminating
4. **Readiness probe**: Configure Kubernetes readiness probe on `GET /health` before routing traffic

```yaml
# Kubernetes readiness probe example
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
```

### Rollback Procedure

#### Application Rollback

```bash
# Re-deploy previous image tag
docker pull <registry>/frodo-api:<previous-sha>
# Trigger rolling update to previous tag in Kubernetes/ECS

# Verify
curl https://api.yourdomain.com/health
```

#### Database Rollback

```bash
# Check current migration revision
alembic current

# Rollback one step
alembic downgrade -1

# Rollback to a specific revision
alembic downgrade <revision_id>
```

> **Warning**: Data-destructive migrations (DROP TABLE, DROP COLUMN) cannot be fully reversed. Always take a database snapshot before applying such migrations.

---

## 5. Security Checklist

### Authentication & Secrets

- [ ] **JWT_SECRET_KEY** is a cryptographically random 64-character hex string (not the default `change-me`)
- [ ] **SECRET_KEY** is a cryptographically random value (not the default)
- [ ] **TOKEN_VAULT_KEY** is a base64-encoded 32-byte random key (not the placeholder)
- [ ] All secrets are stored in a secrets manager (AWS Secrets Manager, GCP Secret Manager, or Vault), not in `.env` files on production servers
- [ ] `DEBUG=false` in production (disables OpenAPI docs, verbose tracebacks)
- [ ] `SIDECAR_AUTH_TOKEN` is set and validated on every request to the SDK sidecar

### Token Vault

- [ ] AES-256-GCM encryption key is backed up securely (loss = all stored TikTok tokens are unrecoverable)
- [ ] Token vault key rotation procedure is documented and tested before going live
- [ ] Re-encryption migration script exists before rotating `TOKEN_VAULT_KEY`
- [ ] `token_vault.refresh_failure_count` alerting is configured

### CORS

- [ ] `FRONTEND_URL` is set to the exact production frontend origin (e.g., `https://app.yourdomain.com`)
- [ ] Wildcard `*` CORS is not permitted in production
- [ ] CORS configuration verified against middleware in `backend/middleware/`

### Rate Limiting

- [ ] Frodo API rate limiting middleware is enabled for all authenticated endpoints
- [ ] TikTok API rate limits are enforced via Redis token bucket (Shop: 50 QPS, Developer: 600/min)
- [ ] Rate limit headers are returned to frontend for graceful UI handling

### HTTPS / TLS

- [ ] All traffic to API and frontend uses HTTPS (TLS 1.2+)
- [ ] HTTP → HTTPS redirect is configured at the load balancer
- [ ] TLS certificates are auto-renewed (ACM / Let's Encrypt)
- [ ] `Secure` and `HttpOnly` flags are set on JWT cookies

### Secrets Management (in code)

- [ ] No secrets or API keys hardcoded anywhere in the codebase
- [ ] `bandit -r backend/` runs clean (no high-severity findings)
- [ ] `pip audit` shows no known vulnerabilities in dependencies
- [ ] `.env` file is in `.gitignore` and never committed

### RBAC Verification

- [ ] 5-tier RBAC (owner > admin > manager > member > viewer) is enforced on all routes
- [ ] Role checks in `backend/auth/rbac.py` are tested by integration tests
- [ ] Viewer role cannot perform write operations — verified by test
- [ ] Organization-level isolation: users cannot access other organizations' workspaces

### Input Validation

- [ ] All API request bodies use Pydantic v2 schemas (automatic validation)
- [ ] Webhook payloads are validated with signature verification before processing
- [ ] No raw SQL string interpolation anywhere (SQLAlchemy ORM used throughout)
- [ ] File upload endpoints (when added) validate file type and size

### Multi-Tenant Data Isolation

- [ ] `workspace_id` is present on all tenant-scoped tables
- [ ] All queries in services include `workspace_id` filter
- [ ] PostgreSQL Row-Level Security policies are reviewed and enforced
- [ ] Integration tests verify cross-workspace data isolation (tenant A cannot read tenant B's data)

### Audit Logging

- [ ] `audit_log` table captures user actions with IP address
- [ ] Sensitive operations (token connect, account deletion, role changes) are logged
- [ ] Audit log is write-only to application — no delete endpoint exists

---

## 6. Monitoring & Observability

### Logging Strategy

All services log to stdout in structured JSON format. In production, pipe to a log aggregation service.

**Recommended stack**: AWS CloudWatch Logs, Datadog, or Papertrail.

```bash
# Log format configured in backend/middleware/logging.py
# Fields: timestamp, level, request_id, user_id, workspace_id, method, path, status_code, duration_ms
```

Key log queries for operators:

```bash
# API 5xx errors
grep '"level":"ERROR"' | grep '"status_code":5'

# Token refresh failures
grep 'token_refresh' | grep 'ERROR'

# Webhook signature failures
grep 'signature_valid.*false'

# Slow requests (> 2s)
grep '"duration_ms"' | awk -F'"duration_ms":' '{print $2}' | awk '{if($1>2000) print}'
```

### Key Metrics to Track

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| API p95 response time | API logs / APM | > 2s |
| API error rate (5xx) | API logs | > 1% |
| Celery task queue depth | Redis `llen celery` | > 1000 pending |
| Celery task failure rate | Celery events | > 5% |
| Token refresh failures | `token_vault.refresh_failure_count` | > 0 for any account |
| Connected account errors | `connected_accounts.status = 'error'` | Any |
| PostgreSQL connections | `pg_stat_activity` active count | > 80% of `max_connections` |
| Redis memory usage | `INFO memory` → `used_memory_rss` | > 80% of `maxmemory` |
| Webhook processing lag | `webhook_events` with `status='received'` older than 5 min | Any |
| Ad sync staleness | `campaigns.synced_at` older than 2h for active account | Any |
| Content sync staleness | `tiktok_videos.synced_at` older than 24h with active account | Any |
| Intelligence sync staleness | `trend_snapshots.collected_at` older than 8h | Any |
| Disk usage (DB) | Cloud provider metrics | > 85% |

### Health Check Endpoints

| Endpoint | Description | Expected Response |
|----------|-------------|-------------------|
| `GET /health` | Top-level health check | `{"status": "healthy", "version": "0.1.0"}` |

**Recommended additions** (not yet implemented):

```
GET /health/db     — Check PostgreSQL connectivity
GET /health/redis  — Check Redis connectivity
GET /health/celery — Check at least one worker is online
```

### Alerting Recommendations

| Alert | Trigger | Channel |
|-------|---------|---------|
| API down | `/health` returns non-200 for 1 min | PagerDuty / SMS |
| High error rate | 5xx rate > 1% over 5 min | Slack + email |
| Celery queue backlog | Queue depth > 1000 for > 10 min | Slack |
| Token refresh failure | Any `refresh_failure_count` increments | Slack |
| Connected account errored | Any `connected_accounts.status = 'error'` | Email to workspace owner |
| DB connection saturation | Active connections > 80% of max | PagerDuty |
| Redis memory high | > 80% used | PagerDuty |

### Error Tracking

- **Sentry** (recommended): Install `sentry-sdk[fastapi]`, configure DSN, capture unhandled exceptions with workspace/user context.

```python
# backend/main.py — add to app factory
import sentry_sdk
sentry_sdk.init(dsn="https://...", environment=settings.app_env, traces_sample_rate=0.1)
```

---

## 7. Performance Considerations

### Database Query Optimization

- All tenant-scoped tables have indexes on `workspace_id` (verified in schema)
- Additional performance indexes defined: `idx_orders_status`, `idx_campaigns_workspace`, `idx_webhook_events_platform`
- **Add before launch**: Composite indexes on high-frequency queries (e.g., `(workspace_id, synced_at)` for sync freshness queries)
- Use `EXPLAIN ANALYZE` to audit queries that take > 100ms in staging
- Consider read replicas for analytics aggregation queries (heavy JSONB operations on `metrics_snapshot`)

### Redis Memory Management

- Use separate DB indexes (0/1/2) to avoid cross-contamination
- Set `maxmemory-policy allkeys-lru` — evicts least-recently-used cache entries under pressure
- Token vault keys and rate-limit counters must not be evicted — store in a separate Redis instance or use `volatile-lru` with TTL-tagged keys
- Monitor `used_memory_rss` vs `used_memory` for fragmentation

### Celery Worker Concurrency

- Default config: `--concurrency=4` per worker container
- Shop sync tasks (HMAC-heavy) are CPU-bound — keep concurrency at 4 per container
- I/O-bound tasks (API calls to TikTok) benefit from higher concurrency
- Recommended: separate queues for high-priority tasks (token refresh) vs. data sync tasks
- Celery Beat: **single instance only** — duplicate schedulers cause duplicate task execution

### Frontend Bundle Optimization

- Next.js 15 App Router with React 19 — RSC reduces client-side JS
- Run `npm run build && npm run analyze` (add `@next/bundle-analyzer`) to check bundle sizes
- Ensure dynamic imports (`next/dynamic`) are used for heavy dashboard components
- Target: initial JS bundle < 200KB gzipped

### API Rate Limiting Tuning

TikTok platform rate limits (enforced by Redis token bucket in `backend/tiktok/rate_limiter.py`):

| Platform | Limit | Notes |
|----------|-------|-------|
| Shop | 50 QPS per app | Shared across all tenants |
| Developer | 600 requests/min | Per-token |
| Marketing | Varies by endpoint | Check Marketing API docs |

Under high load with many connected accounts, the shared 50 QPS Shop limit becomes a bottleneck. Mitigation:
- Queue sync tasks with backpressure
- Batch API calls where TikTok supports it (e.g., bulk product fetch)
- Separate registered TikTok apps by customer tier if needed (requires multiple `app_key`/`app_secret` pairs)

---

## 8. Data Management

### Backup Strategy

| Data Store | Method | Schedule | Retention |
|-----------|--------|----------|-----------|
| PostgreSQL | Managed DB automated snapshot | Daily | 30 days |
| PostgreSQL | Manual `pg_dump` before migrations | Before each migration | Keep until next successful migration |
| Redis | AOF (append-only file) persistence | Continuous | On-disk (managed service) |
| Redis | RDB snapshot | Every 15 min | Latest snapshot |

Manual backup command:

```bash
pg_dump -h <host> -U frodo -d frodo -F c -f backup_$(date +%Y%m%d_%H%M%S).dump
```

Restore:

```bash
pg_restore -h <host> -U frodo -d frodo --clean backup_YYYYMMDD_HHMMSS.dump
```

### Data Retention Policies

| Table | Retention | Rationale |
|-------|-----------|-----------|
| `audit_log` | 1 year minimum | Compliance, security investigations |
| `webhook_events` | 90 days | Debugging, idempotency verification |
| `orders`, `products` | Indefinite | Business data, customer history |
| `campaigns`, `ads` | Indefinite | Ad performance history |
| `tiktok_videos` | Indefinite | Content library |
| Celery task results | 24 hours | Set `result_expires` in Celery config |

### Migration Runbook

1. **Before any migration**: Take a manual database snapshot
2. **Test in staging first**: Run `alembic upgrade head` on a staging DB clone
3. **Check for destructive operations**: Review migration script for `DROP TABLE`, `DROP COLUMN`, data-loss operations
4. **Run migrations before deploying new API code**:
   ```bash
   alembic upgrade head
   alembic current  # Verify revision matches expected
   ```
5. **If migration fails**: Run `alembic downgrade -1` and investigate before retrying
6. **Never run `alembic downgrade` on production without a snapshot**

### Multi-Tenant Data Isolation Verification

Before launch, run this verification checklist:

```sql
-- 1. Verify workspace_id is on all tenant tables
SELECT table_name FROM information_schema.columns
WHERE column_name = 'workspace_id' AND table_schema = 'public'
ORDER BY table_name;

-- 2. Spot-check: products only return for correct workspace
SELECT COUNT(*) FROM products WHERE workspace_id != '<expected_workspace_id>';

-- 3. Check no cross-tenant data in orders
SELECT workspace_id, COUNT(*) FROM orders GROUP BY workspace_id;

-- 4. Verify RLS policies are active
SELECT tablename, policyname FROM pg_policies WHERE schemaname = 'public';
```

Integration tests cover tenant isolation — run `pytest tests/integration -v -k isolation` before production deployment.

---

## 9. Production Readiness Checklist

### CRITICAL — Must Have Before Any Production Traffic

| # | Item | Status | Estimated Effort |
|---|------|--------|------------------|
| C1 | `DEBUG=false` in production environment | TODO | < 1h |
| C2 | All default secret values replaced (`SECRET_KEY`, `JWT_SECRET_KEY`, `TOKEN_VAULT_KEY`) | TODO | < 1h |
| C3 | Secrets stored in secrets manager (not `.env` files on servers) | TODO | 2–4h |
| C4 | TikTok app credentials provisioned for all platforms (Shop, Developer, Marketing) | TODO | 2–5 days (TikTok review) |
| C5 | Production OAuth redirect URIs registered with all TikTok platforms and Google | TODO | 2h (after apps registered) |
| C6 | Production PostgreSQL with automated backups and Multi-AZ | TODO | 2–4h |
| C7 | Production Redis with AOF persistence | TODO | 1–2h |
| C8 | HTTPS / TLS enabled on all public endpoints | TODO | 1–2h |
| C9 | `FRONTEND_URL` set to exact production origin (CORS) | TODO | < 30min |
| C10 | Database migrations applied to production DB | TODO | < 30min |
| C11 | Celery Beat running as a single instance (not duplicated) | TODO | < 1h |
| C12 | Health endpoint responding correctly | TODO | < 30min |
| C13 | `bandit -r backend/` passes with no HIGH severity findings | TODO | 2–4h to fix if issues found |
| C14 | `pip audit` shows no critical vulnerabilities | TODO | 1–2h to resolve |
| C15 | Multi-tenant data isolation integration tests pass | DONE | — |
| C16 | Token vault encryption is active and keys are backed up | TODO | 1h |

### HIGH — Should Have Before Launch

| # | Item | Status | Estimated Effort |
|---|------|--------|------------------|
| H1 | Error tracking (Sentry) integrated with `app_env` context | TODO | 2–4h |
| H2 | Structured logging shipped to centralized log aggregation | TODO | 2–4h |
| H3 | Alerting configured for API downtime, error rate, queue depth | TODO | 4–8h |
| H4 | Database connection pooling (PgBouncer) configured | TODO | 2–4h |
| H5 | Redis `maxmemory-policy` set to `allkeys-lru` | TODO | < 1h |
| H6 | Celery task queues separated by priority | TODO | 2–4h |
| H7 | Token refresh failure alerting (notify workspace owners) | TODO | 4–8h |
| H8 | Frontend deployed to CDN (Vercel or CloudFront) | TODO | 2–4h |
| H9 | Load testing completed — simulate 50 concurrent active workspaces | TODO | 1–2 days |
| H10 | Zero-downtime deployment strategy tested in staging | TODO | 1 day |
| H11 | Rollback procedure tested in staging | TODO | 2–4h |
| H12 | E2E test suite (Playwright) covering core flows: register → connect Shop → view orders | TODO | 3–5 days |
| H13 | Rate limit configuration tuned for production load | TODO | 1 day |
| H14 | `JWT_SECRET_KEY` rotation procedure documented | TODO | 2h |
| H15 | `TOKEN_VAULT_KEY` re-encryption script implemented and tested | TODO | 1–2 days |
| H16 | All 20 Celery beat tasks verified running in production | TODO | 2–4h |
| H17 | Webhook signature verification tested with real TikTok payloads | TODO | 4–8h |

### MEDIUM — Nice to Have for Launch

| # | Item | Status | Estimated Effort |
|---|------|--------|------------------|
| M1 | User onboarding flow (welcome, connect wizard, guided tour) | TODO | 3–5 days |
| M2 | Error boundary components on all frontend pages | TODO | 2–3 days |
| M3 | Skeleton/loading states on all data-fetching views | TODO | 2–3 days |
| M4 | Empty state UI with call-to-action for new workspaces | TODO | 1–2 days |
| M5 | Read replicas for analytics queries | TODO | 4–8h |
| M6 | Scheduled reports email delivery | TODO | 1–2 days |
| M7 | Frontend bundle analysis and optimization | TODO | 1 day |
| M8 | API response caching headers for read-heavy endpoints | TODO | 1 day |
| M9 | Billing integration (Stripe) | TODO | 1–2 weeks |
| M10 | SDK sidecar integration tests | TODO | 2–3 days |
| M11 | Frontend component tests (Vitest / Testing Library) | TODO | 1–2 weeks |
| M12 | Penetration testing / security audit | TODO | Engage external firm |
| M13 | Data retention automated cleanup jobs | TODO | 1–2 days |
| M14 | API key management UI (workspace API keys for `analytics` module) | TODO | 1–2 days |
| M15 | Phase 7 Intelligence platform deep-dive | TODO | 2–3 weeks |

---

## 10. Recommended Production Timeline

### Phase A: Infrastructure & Secrets (Week 1)

**Goal**: Production infrastructure running, secrets provisioned.

| Task | Owner | Duration |
|------|-------|----------|
| Provision managed PostgreSQL (Multi-AZ, backups on) | DevOps | 1 day |
| Provision managed Redis (AOF persistence, 1 replica) | DevOps | 0.5 day |
| Set up container registry and CI/CD pipeline | DevOps | 1 day |
| Generate and store all secrets in secrets manager | DevOps | 0.5 day |
| Configure DNS and TLS certificates | DevOps | 0.5 day |
| Deploy backend API + Celery to staging | DevOps | 1 day |
| Deploy frontend to Vercel (staging) | DevOps | 0.5 day |

**Exit criteria**: Staging environment mirrors production architecture. Health endpoint returns 200.

### Phase B: TikTok App Registration (Weeks 1–3, parallel)

**Goal**: All TikTok platform apps registered with full production scopes.

> This is the longest-lead-time item — TikTok app review can take 5–15 business days.

| Task | Owner | Duration |
|------|-------|----------|
| Submit TikTok Shop Partner Center app (all 13 API domains) | Product | 1 day submit + 5–15 days review |
| Submit TikTok Developer Portal app (full content + user scopes) | Product | 1 day submit + 5–15 days review |
| Submit TikTok Marketing API app (full Marketing API access) | Product | 1 day submit + 5–15 days review |
| Set up Google Cloud OAuth credentials | Product | 0.5 day |
| Configure production redirect URIs after approval | Engineer | 2h |

**Exit criteria**: All TikTok platforms return valid tokens for test accounts.

### Phase C: Security Hardening (Week 2)

**Goal**: Security checklist CRITICAL items complete.

| Task | Owner | Duration |
|------|-------|----------|
| Run `bandit -r backend/` and resolve HIGH findings | Engineer | 1–2 days |
| Run `pip audit` and update vulnerable dependencies | Engineer | 0.5 day |
| Verify CORS, HTTPS, cookie flags in staging | Engineer | 0.5 day |
| Write `TOKEN_VAULT_KEY` re-encryption migration | Engineer | 1–2 days |
| Document JWT secret rotation procedure | Engineer | 2h |
| Integration test: multi-tenant isolation audit | Engineer | 0.5 day |

**Exit criteria**: All CRITICAL security checklist items are complete.

### Phase D: Observability (Week 2–3)

**Goal**: Operators can see what the system is doing.

| Task | Owner | Duration |
|------|-------|----------|
| Integrate Sentry for error tracking (backend + frontend) | Engineer | 0.5 day |
| Ship structured logs to aggregation service | DevOps | 0.5 day |
| Set up dashboards for key metrics (API latency, error rate, queue depth) | DevOps | 1 day |
| Configure alerts (API down, high error rate, token refresh failures) | DevOps | 1 day |

**Exit criteria**: On-call team can detect and diagnose incidents from dashboards and alerts.

### Phase E: E2E Testing & Load Testing (Week 3)

**Goal**: Validated under realistic conditions.

| Task | Owner | Duration |
|------|-------|----------|
| Write Playwright E2E suite: register → connect Shop → view orders | Engineer | 3–5 days |
| Run load test: 50 concurrent active workspaces | Engineer | 1–2 days |
| Tune Celery worker concurrency based on load results | Engineer | 0.5 day |
| Test zero-downtime rolling deployment in staging | DevOps | 1 day |
| Test rollback procedure in staging | DevOps | 0.5 day |

**Exit criteria**: E2E suite passes, system stable under 50-workspace load test, rollback verified.

### Phase F: Soft Launch (Week 4)

**Goal**: First real paying customer onboarded.

| Task | Owner | Duration |
|------|-------|----------|
| Deploy to production with all CRITICAL checklist items complete | DevOps | 1 day |
| Onboard 1–3 internal / beta customers | Product | ongoing |
| Monitor dashboards closely for 72h post-launch | DevOps | 3 days |
| Resolve any HIGH checklist items surfaced by live traffic | Engineer | ongoing |

**Exit criteria**: Platform serving real users without critical incidents for 72h.

### Phase G: Hardening & Growth (Weeks 5–8)

Complete HIGH checklist items, implement onboarding UX, billing, performance optimization, and begin Phase 7 Intelligence platform work.

---

## Dependencies Between Phases

```
Phase A (Infrastructure)
  └──> Phase C (Security hardening requires staging env)
  └──> Phase D (Observability requires staging env)
  └──> Phase E (E2E/load testing requires staging env)

Phase B (TikTok app registration)
  └──> Phase E (E2E tests require real TikTok credentials)
  └──> Phase F (Production launch requires real credentials)

Phase C (Security) ──> Phase F (Launch requires security sign-off)
Phase D (Observability) ──> Phase F (Launch requires monitoring in place)
Phase E (Testing) ──> Phase F (Launch requires E2E + load test sign-off)
```

**Critical path**: TikTok app registration (Phase B) is the longest-lead-time item and should begin on Day 1.

---

*Document maintained by engineering team. Update checklist item statuses as work completes.*
*Related docs: [ARCHITECTURE.md](../ARCHITECTURE.md) | [RUNBOOK.md](RUNBOOK.md) | [CONTRIB.md](CONTRIB.md)*

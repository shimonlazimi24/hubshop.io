# Frodo Backend Codemap

> Freshness: 2026-02-24 | Auto-generated

## Directory Structure

```
backend/
  main.py                     # FastAPI app factory, router mounting
  config.py                   # Pydantic BaseSettings (23 fields)
  dependencies.py             # DI: get_db, get_current_user, get_org_membership
  auth/
    jwt.py                    # create_access_token, create_refresh_token, decode_token
    rbac.py                   # Role enum (5 levels), has_permission, require_role
    passwords.py              # hash_password (bcrypt), verify_password
    social.py                 # SocialAuthService (TikTok/Google OAuth)
    routes.py                 # /login, /register, /refresh, /me, /social
  db/
    models/                   # 18 model files, 120+ entity classes
    migrations/               # Alembic migration files
    session.py                # Async session factory
  tiktok/
    gateway.py                # PlatformGateway (rate limiter + circuit breaker + retry)
    rate_limiter.py           # TokenBucketRateLimiter (Redis-backed)
    circuit_breaker.py        # CircuitBreaker (CLOSED/OPEN/HALF_OPEN)
    retry.py                  # with_retry() decorator (exponential backoff)
    shop/client.py            # TikTokShopClient (HMAC-SHA256)
    developer/client.py       # TikTokDeveloperClient (OAuth Bearer)
    marketing/client.py       # TikTokMarketingClient (OAuth + SDK)
    research/client.py        # TikTokResearchClient (client credentials)
    live/client.py            # TikTokLiveClientWrapper (WebSocket)
  modules/
    connect/                  # 1 route file
    commerce/                 # services/ (+ unified_service.py) + routes/ + schemas.py
    advertising/              # services/ (+ unified_service.py) + routes/ + schemas.py
    content/                  # services/ (+ content_creator_bridge.py) + routes/ (+ bridge.py) + schemas.py
    creators/                 # 5 route files + services/ + schemas.py
    analytics/                # services/ + routes/ + schemas.py
    intelligence/             # services/ + routes/
    live/                     # services/ + routes/ + schemas.py
    messaging/                # services/ + routes/
    organic/                  # services/ + routes/
    webhooks/                 # 1 route file
  workers/
    celery_app.py             # Celery config + beat schedule (24 tasks)
    token_refresh.py          # Developer/Shop/Marketing token management
    webhook_processor.py      # Async webhook event routing
    data_sync.py              # Commerce data sync (orders, products)
    ad_sync.py                # Advertising sync (accounts, campaigns, ad groups, ads)
    content_sync.py           # Video + metrics ingestion
    creator_sync.py           # Creator profile updates
    analytics_sync.py         # KPI aggregation + report generation
    intelligence_sync.py      # Trend + competitor tracking
    live_sync.py              # Session monitoring + cleanup
    messaging_sync.py         # Conversation + mention sync
  middleware/
    logging_mw.py             # RequestLoggingMiddleware (request_id, timing)
    tenant.py                 # TenantMiddleware (X-Workspace-Id)
  utils/
    crypto.py                 # AES-256-GCM encrypt/decrypt
    pagination.py             # Paginate helper
```

## Config Fields (backend/config.py)

| Category | Fields |
|----------|--------|
| App | app_name, app_env, debug, secret_key, frontend_url, backend_url |
| Database | database_url |
| Redis | redis_url |
| JWT | jwt_secret_key, jwt_access_token_expire_minutes, jwt_refresh_token_expire_days, jwt_algorithm |
| Token Vault | token_vault_key (AES-256 base64) |
| TikTok Shop | tiktok_shop_app_key, tiktok_shop_app_secret |
| TikTok Developer | tiktok_developer_client_key, tiktok_developer_client_secret |
| TikTok Marketing | tiktok_marketing_app_id, tiktok_marketing_app_secret |
| TikTok Research | tiktok_research_client_key, tiktok_research_client_secret |
| Google OAuth | google_client_id, google_client_secret, google_redirect_uri |
| TikTok Login | tiktok_login_redirect_uri |
| Celery | celery_broker_url, celery_result_backend |

## Dependency Injection

| Dependency | Type | Purpose |
|-----------|------|---------|
| `get_db()` | `AsyncSession` | Async DB session (yield + close) |
| `get_current_user()` | `User` | JWT Bearer extraction + user lookup |
| `get_org_membership()` | `Membership` | Workspace membership validation |

## Module Pattern

Each module follows: `services/` (business logic) + `routes/` or `routes.py` (API endpoints) + optional `schemas.py` (Pydantic DTOs).

Schema files exist in: analytics, advertising, commerce, content, creators, live.

## Test Coverage (879 total)

| Module | Tests |
|--------|-------|
| advertising | 136 |
| content | 69 |
| creators | 55 |
| commerce | 54 |
| analytics | 47 |
| intelligence | 42 |
| models | 39 |
| tiktok clients | 38 |
| workers | 31 |
| live | 26 |
| organic | 17 |
| messaging | 16 |
| integration | 37 |

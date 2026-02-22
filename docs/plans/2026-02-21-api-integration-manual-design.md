# API Integration Manual — Design Document

**Date**: 2026-02-21
**Type**: Ops/Deployment Guide
**Audience**: Backend developer with zero TikTok platform knowledge
**Goal**: Step-by-step instructions to register all TikTok platform apps, configure credentials, and verify connectivity to make Frodo operational

---

## Approach

**Platform-First structure**: One self-contained chapter per TikTok platform. Each chapter covers what the platform is, how to register, where credentials go, the auth flow, gotchas, and a verification script. Developer can tackle one platform at a time and verify independently.

## Manual Structure

### Section 1: Overview & Architecture

- **What is Frodo**: One-paragraph explanation — unified TikTok management platform for brands
- **The 5 TikTok Platforms**: Table explaining each platform, what it does, and what Frodo uses it for:

| Platform | What It Is | Frodo Uses It For |
|----------|-----------|-------------------|
| TikTok Shop | E-commerce marketplace | Orders, products, shops, fulfillment |
| TikTok Developer | Content & user data APIs | Video publishing, display, user info |
| TikTok Marketing | Ads management | Campaigns, ad groups, ads, reporting |
| TikTok Research | Public data queries | Trend analysis, competitor research |
| TikTok LIVE | Live streaming | Real-time commerce, stream monitoring |

- **Architecture Diagram** (text-based):
  ```
  Frontend → FastAPI → Service → PlatformGateway → [RateLimiter → CircuitBreaker → Retry] → TikTok API
                                      ↑
                              TokenVault (encrypted credentials)
  ```
- **Key Concepts**: Brief explanations of TokenVault, PlatformGateway, ConnectedAccount, rate limiting, circuit breaker

### Section 2: Prerequisites & Infrastructure

- **System Requirements**: Python 3.12+, Docker & Docker Compose, Node.js 18+ (frontend)
- **Start Infrastructure**: `docker compose up -d postgres redis`
- **Run Database Migrations**: `alembic upgrade head`
- **Environment File Setup**: Create `.env` from template with all credential placeholders:
  ```
  DATABASE_URL=postgresql+asyncpg://frodo:frodo@localhost:5432/frodo
  REDIS_URL=redis://localhost:6379/0
  TOKEN_VAULT_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">
  TIKTOK_SHOP_APP_KEY=
  TIKTOK_SHOP_APP_SECRET=
  TIKTOK_DEVELOPER_CLIENT_KEY=
  TIKTOK_DEVELOPER_CLIENT_SECRET=
  TIKTOK_MARKETING_APP_ID=
  TIKTOK_MARKETING_APP_SECRET=
  TIKTOK_RESEARCH_CLIENT_KEY=
  TIKTOK_RESEARCH_CLIENT_SECRET=
  ```
- **Start Services**: `docker compose up -d`
- **Gotchas**: TOKEN_VAULT_KEY must be generated once and never changed. Redis must be accessible from both API and Celery containers.

### Section 3: TikTok Shop Setup

- **What it is**: E-commerce platform for selling via TikTok
- **Registration**: TikTok Shop Partner Center → create partner app → note App Key + App Secret → configure redirect URI
- **Credential mapping**: `TIKTOK_SHOP_APP_KEY`, `TIKTOK_SHOP_APP_SECRET`
- **Auth flow**: Seller OAuth → auth code → exchange for access token (7d) → HMAC-SHA256 signed requests → Celery auto-refresh
- **Gotchas**:
  - HMAC-SHA256 signing (not Bearer tokens) — `app_secret + path + sorted_params + body + app_secret`
  - Each seller has its own token (multi-tenant)
  - `shop_cipher` required for some endpoints
  - Rate limit: 50 QPS per shop
- **Verification**: Script that signs a request to `/authorization/202309/shops` and confirms shop data

### Section 4: TikTok Developer Setup

- **What it is**: Content, user, and display APIs
- **Registration**: TikTok for Developers → create app → select scopes → note Client Key + Client Secret → configure redirect URI → submit for review
- **Credential mapping**: `TIKTOK_DEVELOPER_CLIENT_KEY`, `TIKTOK_DEVELOPER_CLIENT_SECRET`
- **Auth flow**: User OAuth → auth code → exchange for access token (24h) + refresh token (365d) → Celery auto-refresh
- **Gotchas**:
  - Apps start in sandbox (test users only until approved)
  - Some scopes require business verification
  - Access token expires in 24h — Celery refresh worker must be running
  - Refresh token expires in 365d — needs manual re-auth annually
  - Rate limit: 10 QPS
  - Some endpoints require `fields` parameter
- **Verification**: Script that exchanges auth code for tokens and calls `/v2/user/info/`

### Section 5: TikTok Marketing Setup

- **What it is**: Ads management (campaigns, ad groups, ads, audiences, pixels, reporting, Spark Ads)
- **Registration**: TikTok for Business Marketing API portal → create app → select API products → note App ID + App Secret → configure redirect URI
- **Credential mapping**: `TIKTOK_MARKETING_APP_ID`, `TIKTOK_MARKETING_APP_SECRET`
- **Auth flow**: Advertiser OAuth → auth code → exchange for long-term access token (no expiry) → `Access-Token` header + `advertiser_id` param
- **Optional Business SDK**:
  - Install: `pip install business-api-client`
  - If installed, `TikTokMarketingClient.sdk` exposes typed API methods
  - Falls back to raw HTTP if not installed
  - Use SDK for complex operations (campaign creation, batch ops); raw HTTP for simple reads
  - Pin SDK version in requirements.txt — must match API version (v1.3)
- **Gotchas**:
  - Requires TikTok Ads Manager account with active ad account
  - App must be linked to a Business Center
  - Long-term token — no auto-refresh, but if revoked needs full re-auth
  - Every request requires `advertiser_id`
  - `metadata_json` stores list of accessible advertiser_ids
  - Rate limit: 10 QPS
  - Sandbox ad accounts have fake data
- **Verification**: Script that calls `/advertiser/info/` and confirms account data

### Section 6: TikTok Research Setup

- **What it is**: Public data queries for research — video search, user info, comments, followers
- **Registration**: TikTok for Developers → Research API section → apply with use-case justification → once approved, note Client Key + Client Secret
- **Credential mapping**: `TIKTOK_RESEARCH_CLIENT_KEY`, `TIKTOK_RESEARCH_CLIENT_SECRET`
- **Auth flow**: Client credentials (server-to-server) — POST client_key + client_secret → short-lived access token → Bearer auth → auto-refreshed per batch
- **Gotchas**:
  - NOT user-authorized OAuth — no user redirect
  - Requires TikTok approval (not instant)
  - Rate limit: 5 QPS (strictest platform)
  - Public data only
  - Cursor-based pagination
  - Methods: `query_videos()`, `query_user_info()`, `query_video_comments()`, `query_user_followers()`
- **Verification**: Script that obtains client credentials token and calls `/v2/research/video/query/`

### Section 7: TikTok LIVE Setup

- **What it is**: Real-time live stream monitoring via WebSocket
- **Setup**: Install `pip install TikTokLive` — no app registration, no credentials, no env vars
- **How it works**: Connect to live stream by username → WebSocket events (Comment, Gift, Like, Follow, Share, Join, LiveEnd) → `LiveEventData` objects
- **Gotchas**:
  - Third-party library, not official TikTok API
  - `TikTokLiveClientWrapper` raises NotImplementedError if package not installed
  - Connection can be unstable — depends on stream availability
  - LIVE is **partially implemented** — wrapper exists but full production flow needs work
  - Pin the library version to avoid breaking changes
  - No rate limit from TikTok (Frodo configures 100 QPS in gateway)
- **Current status**: Least mature integration. Dev should expect to build out connection management, reconnection logic, and event processing.
- **Verification**: Script that imports TikTokLive, instantiates wrapper, confirms library loads

### Section 8: Verification & Smoke Tests

- **Pre-flight checks**: Docker services running, DB migrated, `.env` populated, Redis accessible
- **Per-platform verification scripts**: Each loads creds, authenticates, makes a basic API call, prints success/failure
- **System-level checks**:
  - Token vault: tokens encrypted in DB (not plaintext)
  - Celery workers: `celery inspect registered` shows token refresh task
  - Rate limiter: Redis keys exist after first API call
  - Circuit breaker: all platforms in CLOSED state
- **Troubleshooting table**:

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| 401 on Shop API | Invalid HMAC signature | Check app_secret, verify signing order |
| 401 on Developer API | Expired access token | Check Celery beat is running refresh task |
| Empty Developer response | Missing `fields` param | Add required fields to request |
| 429 on any platform | Rate limit exceeded | Check rate limiter config, reduce QPS |
| Circuit breaker OPEN | 5+ consecutive failures | Check credentials, wait 30s for reset |
| Token vault decrypt error | Wrong TOKEN_VAULT_KEY | Key must match what was used to encrypt |

## Deliverables

1. **Markdown manual** at `docs/api-integration-manual.md`
2. **Verification scripts** at `scripts/verify/` (one per platform + one combined)
3. **`.env.example`** file updated with all required variables and comments

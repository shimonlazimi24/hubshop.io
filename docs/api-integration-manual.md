# Frodo API Integration Manual

> **Audience**: Backend developer with zero TikTok API knowledge.
> **Purpose**: Step-by-step ops and deployment guide for connecting Frodo to all five TikTok platforms.
> **Last updated**: 2026-02-21

---

## Table of Contents

1. [Overview & Architecture](#1-overview--architecture)
2. [Prerequisites & Infrastructure](#2-prerequisites--infrastructure)
3. [TikTok Shop Setup](#3-tiktok-shop-setup)
4. [TikTok Developer Setup](#4-tiktok-developer-setup)
5. [TikTok Marketing Setup](#5-tiktok-marketing-setup)
6. [TikTok Research Setup](#6-tiktok-research-setup)
7. [TikTok LIVE Setup](#7-tiktok-live-setup)
8. [Verification & Troubleshooting](#8-verification--troubleshooting)

---

## 1. Overview & Architecture

### What Is Frodo

Frodo ("One platform to rule them all") is a unified SaaS platform that connects to **five separate TikTok APIs**, giving brands a single dashboard to manage their TikTok commerce, content, advertising, analytics, and live streaming. Each TikTok API was built by a different team at TikTok, uses a different authentication model, and has its own developer portal. Frodo abstracts all of this behind a unified service layer so that end users never have to deal with the complexity.

### The 5 TikTok Platforms

| Platform | What It Is | Frodo Uses It For | Auth Model |
|----------|-----------|-------------------|------------|
| **TikTok Shop** | E-commerce marketplace | Orders, products, shops, fulfillment, returns | HMAC-SHA256 request signing |
| **TikTok Developer** | Content & user data APIs | Video publishing, display, user info, metrics | OAuth 2.0 Bearer (24h access token, 365d refresh token) |
| **TikTok Marketing** | Ads management (largest API surface) | Campaigns, ad groups, ads, audiences, reporting | OAuth 2.0 long-term token (no scheduled expiry) |
| **TikTok Research** | Public data query API | Trend analysis, competitor intelligence | Client credentials (server-to-server, no user interaction) |
| **TikTok LIVE** | Live streaming events | Real-time commerce, stream monitoring | None (public WebSocket via third-party TikTokLive library) |

> **Key insight**: These five platforms have **no cross-authentication**. A Shop token cannot call the Marketing API, and a Developer token cannot call the Shop API. Frodo stores and manages credentials for each platform independently.

### Architecture Diagram

```
Browser / Frontend (Next.js 15)
         |
         v
    FastAPI Server (backend/)
         |
         v
    Service Layer (backend/modules/*)
         |
         v
    PlatformGateway (backend/tiktok/gateway.py)
         |
    +----+---------------------------+
    |    |                           |
    v    v                           v
RateLimiter  CircuitBreaker       Retry
(Redis)      (per-platform)       (exp. backoff)
    |    |                           |
    +----+---------------------------+
         |
         v
    Platform Client
    (shop/ | developer/ | marketing/ | research/ | live/)
         |
         v
    TikTok API  <-- TokenVault (AES-256-GCM encrypted credentials)
```

Every outgoing API call follows the same path: Service Layer -> PlatformGateway -> rate limit check -> circuit breaker check -> retry wrapper -> platform-specific HTTP client -> TikTok API.

### Key Concepts

#### TokenVault

**File**: `backend/db/models/platform.py` (class `TokenVault`)

Stores encrypted access tokens and refresh tokens for each connected account. Encryption uses **AES-256-GCM** with a 96-bit random nonce. The encryption key is derived from the `TOKEN_VAULT_KEY` environment variable. Each vault entry is linked 1:1 to a `ConnectedAccount` via `connected_account_id`. Fields include `encrypted_access_token`, `encrypted_refresh_token`, `access_token_expires_at`, `refresh_token_expires_at`, and `scopes`.

The actual encryption/decryption logic lives in `backend/utils/crypto.py` and uses the `cryptography` library's `AESGCM` primitive.

#### ConnectedAccount

**File**: `backend/db/models/platform.py` (class `ConnectedAccount`)

Represents one workspace's connection to one TikTok platform. A workspace can have multiple connected accounts (e.g., one Shop seller + one Developer user + one Marketing advertiser). Each account tracks:

- `platform`: One of `SHOP`, `DEVELOPER`, `MARKETING`, `LIVE`, `RESEARCH`
- `status`: One of `ACTIVE`, `ERROR`, `DISCONNECTED`, `REFRESHING`
- `platform_account_id`: The ID on TikTok's side (seller_id, open_id, advertiser_id)
- `metadata_json`: Platform-specific data (e.g., `shop_ciphers` for Shop, `advertiser_ids` for Marketing, `scope` for Developer)

#### PlatformGateway

**File**: `backend/tiktok/gateway.py` (class `PlatformGateway`)

The single entry point for all outbound TikTok API calls. Wraps every request with three layers of protection:

1. **Circuit breaker** check (fail-fast if platform is down)
2. **Rate limiter** check (token bucket, Redis-backed)
3. **Retry** with exponential backoff (on 429/5xx)

Each gateway instance is initialized with a specific `Platform`, `account_id`, and platform `client`.

#### RateLimiter

**File**: `backend/tiktok/rate_limiter.py` (class `TokenBucketRateLimiter`)

Redis-backed token bucket algorithm. Each platform + account combination gets its own bucket. Pre-configured limits:

| Platform | Max QPS | Refill Rate | Redis Key Prefix |
|----------|---------|-------------|------------------|
| Shop | 50 | 50/s | `rate_limit:shop:{account_id}` |
| Developer | 10 | 10/s | `rate_limit:developer:{account_id}` |
| Marketing | 10 | 10/s | `rate_limit:marketing:{account_id}` |
| Research | 5 | 5/s | `rate_limit:research:{account_id}` |
| LIVE | 100 | 100/s | `rate_limit:live:{account_id}` |

Buckets auto-expire after 120 seconds of idle time.

#### CircuitBreaker

**File**: `backend/tiktok/circuit_breaker.py` (class `CircuitBreaker`)

Per-platform failure tracking with three states:

- **CLOSED** (normal): Counts failures within a 60-second sliding window. All requests pass through.
- **OPEN** (fail-fast): Activated after 5 failures within the window. All requests immediately raise `CircuitBreakerOpen`. Transitions to HALF_OPEN after 30 seconds.
- **HALF_OPEN** (probe): Allows one probe request. Success returns to CLOSED; failure returns to OPEN.

#### Retry

**File**: `backend/tiktok/retry.py` (function `with_retry`)

Exponential backoff on retryable errors. Default configuration: max 3 retries with delays of 1s, 2s, 4s (base * 2^attempt).

- **Retryable**: HTTP 429, 500, 502, 503, 504, and transport errors (connection reset, timeout)
- **Non-retryable**: HTTP 400, 401, 403, 404 (client errors are never retried)

---

## 2. Prerequisites & Infrastructure

### System Requirements

| Component | Minimum Version | Purpose |
|-----------|----------------|---------|
| Python | 3.12+ | Backend runtime |
| Docker & Docker Compose | Latest stable | Container orchestration |
| Node.js | 18+ | Frontend build (Next.js) |
| PostgreSQL | 16 | Primary database (runs in Docker) |
| Redis | 7 | Rate limiting, Celery broker, caching (runs in Docker) |

### Step-by-Step Setup

**1. Clone and install dependencies**

```bash
git clone <repository-url> && cd frodo
pip install -r requirements.txt
```

**2. Start infrastructure services**

```bash
docker compose up -d postgres redis
```

Wait for both to be healthy:

```bash
docker compose ps  # Both should show "healthy"
```

**3. Run database migrations**

```bash
alembic upgrade head
```

**4. Configure environment**

```bash
cp .env.example .env
```

**5. Generate the Token Vault encryption key**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste it as the value of `TOKEN_VAULT_KEY` in `.env`.

**6. Fill in platform credentials**

Open `.env` and fill in the platform-specific credentials as you complete Sections 3-7 of this manual. You do not need all platforms configured to start the server -- only the ones you plan to use.

**7. Start all services**

```bash
docker compose up -d
```

This starts 5 containers: `api`, `celery-worker`, `celery-beat`, `postgres`, `redis`.

**8. Verify the API is running**

```bash
curl http://localhost:8000/health
```

### Environment Variables Reference

The complete `.env.example` is at the project root. Key variables:

```bash
# Core
APP_ENV=development
SECRET_KEY=change-me-to-a-random-secret-key
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Database & Redis
DATABASE_URL=postgresql+asyncpg://frodo:frodo@localhost:5432/frodo
REDIS_URL=redis://localhost:6379/0

# Token Vault
TOKEN_VAULT_KEY=<output of secrets.token_urlsafe(32)>

# TikTok Shop (Section 3)
TIKTOK_SHOP_APP_KEY=
TIKTOK_SHOP_APP_SECRET=

# TikTok Developer (Section 4)
TIKTOK_DEVELOPER_CLIENT_KEY=
TIKTOK_DEVELOPER_CLIENT_SECRET=

# TikTok Marketing (Section 5)
TIKTOK_MARKETING_APP_ID=
TIKTOK_MARKETING_APP_SECRET=

# TikTok Research (Section 6)
TIKTOK_RESEARCH_CLIENT_KEY=
TIKTOK_RESEARCH_CLIENT_SECRET=

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

> **Warning: TOKEN_VAULT_KEY**
>
> Generate `TOKEN_VAULT_KEY` **once** and **never change it**. This key encrypts every access token and refresh token stored in the database. Changing or losing this key means all existing encrypted tokens become permanently unreadable, and every connected account will need to be re-authorized by the end user.

> **Warning: Redis Accessibility**
>
> Redis must be accessible from both the API container and the Celery containers. They share the same Docker network by default. If you split Redis into a separate host or cluster, update `REDIS_URL` and `CELERY_BROKER_URL` accordingly in all service configurations.

> **Warning: Docker Health Checks**
>
> All 5 Docker services (`api`, `celery-worker`, `celery-beat`, `postgres`, `redis`) must be running and healthy before proceeding to platform setup. The `api` service depends on both `postgres` and `redis` via `condition: service_healthy` in `docker-compose.yml`. If either dependency is unhealthy, the API will not start.

### Reference Files

| File | Purpose |
|------|---------|
| `backend/config.py` | All settings with defaults and env var mappings |
| `docker-compose.yml` | Container definitions for all 5 services |
| `.env.example` | Template for environment variables |
| `backend/db/models/platform.py` | ConnectedAccount, TokenVault, Platform enum |
| `backend/utils/crypto.py` | AES-256-GCM encrypt/decrypt functions |

---

## 3. TikTok Shop Setup

### What It Is

TikTok Shop is TikTok's e-commerce marketplace. Sellers list products, process orders, and manage fulfillment directly through TikTok. The Shop API lets Frodo pull order data, manage products, query shops, and handle returns and fulfillment on behalf of a seller.

**This is a completely separate platform from TikTok for Developers.** It has its own developer portal, its own app registration, and its own authentication model (HMAC-SHA256 signing instead of Bearer tokens).

### Registration Steps

1. Go to **https://partner.tiktokshop.com** (not developers.tiktok.com)
2. Register as a **Partner Developer** (you need a business entity)
3. Create a new App in the Partner Center
4. Note down your **App Key** and **App Secret**
5. Under "Configuration", add the redirect URI: `{BACKEND_URL}/api/connect/shop/callback`
   - For local development: `http://localhost:8000/api/connect/shop/callback`
6. Request the scopes you need (orders, products, fulfillment, etc.)
7. Submit the app for review (TikTok reviews Shop apps before they can access production data)

### Environment Variables

```bash
TIKTOK_SHOP_APP_KEY=your_app_key_here
TIKTOK_SHOP_APP_SECRET=your_app_secret_here
```

### Authentication Flow

TikTok Shop uses a unique authentication model that differs from standard OAuth 2.0:

```
1. User clicks "Connect Shop" in Frodo
         |
         v
2. Frodo redirects to TikTok Shop OAuth:
   https://services.tiktokshops.us/open/authorize?service_id={app_key}&state={state}
         |
         v
3. Seller approves access on TikTok
         |
         v
4. TikTok redirects to: {BACKEND_URL}/api/connect/shop/callback?code={auth_code}&state={state}
         |
         v
5. Frodo exchanges code for tokens:
   GET https://auth.tiktok-shops.com/api/v2/token/get
   Params: app_key, app_secret, auth_code, grant_type=authorized_code
         |
         v
6. Response includes: access_token (7-day), refresh_token, seller_id, shop_cipher_list
         |
         v
7. Tokens are AES-256-GCM encrypted and stored in TokenVault
```

**After the initial exchange**, every API request to TikTok Shop must be **HMAC-SHA256 signed**. This is NOT a Bearer token -- the signature is computed from the request path, parameters, and body.

### Request Signing

**File**: `backend/tiktok/shop/client.py` -> `_generate_signature()`

The signing formula is:

```
sign_string = app_secret + path + sorted(param_key + param_value) + body + app_secret
signature   = HMAC-SHA256(app_secret, sign_string)
```

Parameters named `sign` and `access_token` are excluded from the signature base. The `access_token` is sent in both a query parameter and the `x-tts-access-token` header.

Example of how a signed request is built:

```python
# Common params added to every request
params = {
    "app_key": app_key,
    "timestamp": str(int(time.time())),
    "shop_cipher": shop_cipher,  # if applicable
}

# Generate signature from path + sorted params + body
params["sign"] = generate_signature(app_secret, path, params, body_str)
params["access_token"] = access_token

# Headers
headers = {
    "Content-Type": "application/json",
    "x-tts-access-token": access_token,
}
```

### Token Refresh

Shop access tokens expire after **7 days**. Frodo automatically refreshes them via Celery Beat.

**Task**: `backend.workers.token_refresh.refresh_shop_tokens`
**Schedule**: Daily at midnight UTC (`crontab(minute=0, hour=0)`)
**Logic** (`_refresh_shop_token()`):

```
GET https://auth.tiktok-shops.com/api/v2/token/refresh
Params: app_key, app_secret, refresh_token, grant_type=refresh_token
```

If refresh fails, the account status is set to `ERROR`.

### Gotchas and Common Mistakes

| Gotcha | Detail |
|--------|--------|
| **HMAC, not Bearer** | Shop API uses request signing, not Bearer tokens. Sending `Authorization: Bearer <token>` will not work. The token goes in `x-tts-access-token` header and `access_token` query param. |
| **Multi-tenant tokens** | Each seller has their own token. A single Frodo workspace may connect multiple sellers. Tokens are stored per-ConnectedAccount. |
| **shop_cipher** | Some endpoints require a `shop_cipher` parameter to identify which shop under a seller. The list of ciphers is stored in `metadata_json.shop_ciphers` on the ConnectedAccount. |
| **50 QPS limit** | Shop API allows 50 queries per second per app. Exceeding this returns HTTP 429. The rate limiter handles this automatically. |
| **Different refresh URL** | Token exchange uses `auth.tiktok-shops.com/api/v2/token/get`. Token refresh uses `auth.tiktok-shops.com/api/v2/token/refresh`. These are different endpoints. |
| **Separate portal** | Registration is at partner.tiktokshop.com, not developers.tiktok.com. Credentials from the Developer platform do not work here. |

### Verification

```bash
python -m scripts.verify.verify_shop
```

This script tests HMAC-SHA256 signature generation and makes an HTTP round-trip to the Shop API. It will report success if credentials are valid, even if no seller has authorized yet.

---

## 4. TikTok Developer Setup

### What It Is

TikTok Developer (also called "TikTok for Developers" or "Login Kit / Content Posting API") provides access to user profiles, video data, video publishing, and comment management. This is the API you use to read a user's TikTok videos, publish new content, and retrieve engagement metrics.

**This is a separate platform from TikTok Shop and TikTok Marketing.** The Developer API is user-centric (OAuth on behalf of a TikTok user), while Marketing is advertiser-centric and Shop is seller-centric.

### Registration Steps

1. Go to **https://developers.tiktok.com**
2. Create a developer account (requires a TikTok account)
3. Click "Manage apps" and create a new app
4. Request the following scopes:
   - `user.info.basic` -- Basic user profile
   - `user.info.profile` -- Extended profile info
   - `user.info.stats` -- Follower/following counts
   - `video.list` -- List user's videos
   - `video.publish` -- Publish videos
   - `video.upload` -- Upload video files
   - `comment.list` -- Read comments
   - `comment.list.manage` -- Manage comments
5. Set the redirect URI to: `{BACKEND_URL}/api/connect/developer/callback`
   - For local development: `http://localhost:8000/api/connect/developer/callback`
6. Note down your **Client Key** and **Client Secret**
7. Submit for review (new apps start in sandbox mode)

### Environment Variables

```bash
TIKTOK_DEVELOPER_CLIENT_KEY=your_client_key_here
TIKTOK_DEVELOPER_CLIENT_SECRET=your_client_secret_here
```

### Authentication Flow

Standard OAuth 2.0 Authorization Code flow:

```
1. User clicks "Connect TikTok Account" in Frodo
         |
         v
2. Frodo redirects to TikTok OAuth:
   https://www.tiktok.com/v2/auth/authorize/
   ?client_key={client_key}
   &response_type=code
   &scope=user.info.basic,video.list
   &redirect_uri={BACKEND_URL}/api/connect/developer/callback
   &state={workspace_id}:{user_id}
         |
         v
3. User approves on TikTok
         |
         v
4. TikTok redirects to: {BACKEND_URL}/api/connect/developer/callback?code={code}&state={state}
         |
         v
5. Frodo exchanges code for tokens:
   POST https://open.tiktokapis.com/v2/oauth/token/
   Body: client_key, client_secret, code, grant_type=authorization_code, redirect_uri
         |
         v
6. Response includes: access_token (24h), refresh_token (365d), open_id, scope
         |
         v
7. Tokens encrypted and stored in TokenVault
```

After authorization, API calls use standard Bearer token authentication:

```
Authorization: Bearer {access_token}
```

**Base URL**: `https://open.tiktokapis.com/v2`

**File**: `backend/tiktok/developer/client.py`

### Token Refresh

Developer access tokens expire after **24 hours**. Refresh tokens last **365 days**.

**Task**: `backend.workers.token_refresh.refresh_developer_tokens`
**Schedule**: Every 12 hours (`crontab(minute=0, hour="*/12")`)
**Logic** (`_refresh_developer_token()`):

```
POST https://open.tiktokapis.com/v2/oauth/token/
Body: client_key, client_secret, grant_type=refresh_token, refresh_token={refresh_token}
```

If refresh fails, the account status is set to `ERROR`.

> **Warning: Celery Must Be Running**
>
> If Celery Beat is not running, developer tokens will expire after 24 hours and all Developer API calls will start returning 401. This is the most time-sensitive token of all five platforms. Always verify Celery Beat is running: `docker compose ps celery-beat`.

### Gotchas and Common Mistakes

| Gotcha | Detail |
|--------|--------|
| **Sandbox mode** | New apps start in sandbox mode. You can only access your own TikTok account's data. Production access requires app review and may require business verification. |
| **Business verification** | For publishing scopes (`video.publish`, `video.upload`), TikTok may require business verification before approving your app for production. |
| **24-hour access token** | The shortest-lived token of all five platforms. Celery Beat must be running to auto-refresh. |
| **365-day refresh token** | Refresh tokens expire after one year. Users will need to re-authorize annually. There is no way to extend this programmatically. |
| **`fields` parameter** | Many Developer API endpoints require a `fields` query parameter to specify which data fields to return. Omitting it returns empty data, not an error. |
| **10 QPS** | Developer API allows 10 queries per second (600/minute). Lower than Shop's 50 QPS. |
| **Separate from Marketing** | A Developer app cannot call Marketing API endpoints. They are completely separate platforms with separate credentials, even though both use OAuth 2.0. |

### Verification

```bash
python -m scripts.verify.verify_developer
```

This script tests credential validity by calling the token endpoint. It reports whether the client key and secret are accepted.

---

## 5. TikTok Marketing Setup

### What It Is

TikTok Marketing API (also called "TikTok for Business API" or "TikTok Ads API") is the largest API surface of all five platforms. It provides full programmatic control over TikTok advertising: creating campaigns, managing ad groups and ads, defining audiences, uploading creatives, pulling performance reports, and more.

**This platform has its own developer portal** separate from both developers.tiktok.com and partner.tiktokshop.com.

### Registration Steps

1. Go to **https://business-api.tiktok.com/portal/docs** and click "Apply for access"
2. You need:
   - A TikTok Ads Manager account (create one at https://ads.tiktok.com)
   - A TikTok Business Center account
3. Register your developer app in the Marketing API portal
4. Set the redirect URI to: `{BACKEND_URL}/api/connect/marketing/callback`
   - For local development: `http://localhost:8000/api/connect/marketing/callback`
5. Note down your **App ID** and **App Secret**
6. Submit for review

### Environment Variables

```bash
TIKTOK_MARKETING_APP_ID=your_app_id_here
TIKTOK_MARKETING_APP_SECRET=your_app_secret_here
```

### Authentication Flow

```
1. User clicks "Connect Ad Account" in Frodo
         |
         v
2. Frodo redirects to Marketing OAuth:
   https://business-api.tiktok.com/portal/auth
   ?app_id={app_id}
   &redirect_uri={BACKEND_URL}/api/connect/marketing/callback
   &state={workspace_id}:{user_id}
         |
         v
3. Advertiser approves access on TikTok Business Center
         |
         v
4. TikTok redirects to: {BACKEND_URL}/api/connect/marketing/callback?auth_code={code}&state={state}
         |
         v
5. Frodo exchanges code for token:
   POST https://business-api.tiktok.com/open_api/v1.3/oauth2/access_token/
   Body: { "app_id": ..., "secret": ..., "auth_code": ... }
         |
         v
6. Response includes: access_token (long-term, no scheduled expiry), advertiser_ids[]
         |
         v
7. Token encrypted and stored in TokenVault; advertiser_ids stored in metadata_json
```

After authorization, API calls use a custom `Access-Token` header (not `Authorization: Bearer`):

```
Access-Token: {access_token}
```

Every request also requires an `advertiser_id` parameter to identify which ad account to operate on. The list of advertiser IDs is returned during token exchange and stored in `metadata_json.advertiser_ids`.

**Base URL**: `https://business-api.tiktok.com/open_api/v1.3`

**File**: `backend/tiktok/marketing/client.py`

### Official SDK (Optional)

TikTok provides an official Python SDK for the Marketing API:

```bash
pip install business-api-client
```

The `TikTokMarketingClient` auto-detects the SDK at initialization. If installed, the SDK is available via `client.sdk` for typed API access:

```python
from business_api_client import CampaignApi

# Raw HTTP (always available)
result = await gateway.get("/campaign/get/", params={"advertiser_id": "123"})

# SDK (available when business-api-client is installed)
if marketing_client.sdk:
    campaign_api = CampaignApi(marketing_client.sdk)
    # Use typed SDK methods
```

If the SDK is not installed, all calls fall back to raw HTTP. The SDK is optional and not required for Frodo to function.

> **Tip**: Pin the SDK version in requirements.txt. The SDK occasionally introduces breaking changes.

### Token Validation

Marketing tokens are **long-term** -- they have no scheduled expiry. However, they can be revoked by the advertiser at any time. Frodo periodically validates tokens:

**Task**: `backend.workers.token_refresh.check_marketing_tokens`
**Schedule**: Daily at 6 AM UTC (`crontab(minute=0, hour=6)`)
**Logic** (`_do_check_marketing_tokens()`):

```
GET https://business-api.tiktok.com/open_api/v1.3/user/info/
Headers: Access-Token: {token}
```

If the validation call returns a non-200 status or error code, the account status is set to `ERROR`.

### Gotchas and Common Mistakes

| Gotcha | Detail |
|--------|--------|
| **Needs Ads Manager + Business Center** | You must have both a TikTok Ads Manager account AND a Business Center. The Marketing API is specifically for managing ad campaigns; you cannot use Developer credentials here. |
| **Long-term token can be revoked** | The token does not expire on a schedule, but advertisers can revoke it at any time via their Business Center. The `check_marketing_tokens` Celery task catches this. |
| **`advertiser_id` required** | Almost every Marketing API endpoint requires an `advertiser_id` parameter. This is stored in `metadata_json.advertiser_ids` on the ConnectedAccount. A single token can access multiple advertiser accounts. |
| **`Access-Token` header** | The Marketing API uses `Access-Token` (not `Authorization: Bearer`). This is a custom TikTok header. |
| **10 QPS** | Conservative rate limit. Marketing API rate limits vary by endpoint, but Frodo defaults to 10 QPS as a safe baseline. |
| **Sandbox data is fake** | Sandbox mode returns synthetic data. Campaign IDs, metrics, and advertiser data in sandbox do not correspond to real accounts. |

### Verification

```bash
python -m scripts.verify.verify_marketing
```

This script verifies that the App ID and App Secret are accepted by the Marketing API OAuth endpoint. It also checks whether the optional `business-api-client` SDK is installed.

---

## 6. TikTok Research Setup

### What It Is

TikTok Research API provides access to **public** TikTok data for academic and business research purposes. Unlike the other four platforms, this API uses server-to-server authentication (client credentials) -- no end-user authorization is needed. It is designed for querying public videos, user profiles, comments, and follower data at scale.

**This API requires a separate application and approval from TikTok**, which can take days to weeks.

### Registration Steps

1. Go to **https://developers.tiktok.com** (same portal as Developer, but separate application)
2. Navigate to the "Research API" section
3. Submit an application describing your research use case
4. TikTok reviews the application (this process can take days to weeks)
5. Once approved, note down your **Client Key** and **Client Secret** for the Research API
   - These are different credentials from your Developer API client key/secret

### Environment Variables

```bash
TIKTOK_RESEARCH_CLIENT_KEY=your_research_client_key_here
TIKTOK_RESEARCH_CLIENT_SECRET=your_research_client_secret_here
```

### Authentication Flow

Server-to-server client credentials grant -- no user interaction required:

```
1. Frodo needs to call the Research API
         |
         v
2. Auto-request token (first call or when token expires):
   POST https://open.tiktokapis.com/v2/oauth/token/
   Body: { "client_key": ..., "client_secret": ..., "grant_type": "client_credentials" }
         |
         v
3. Response includes: access_token (short-lived)
         |
         v
4. Use token for API calls:
   Authorization: Bearer {access_token}
         |
         v
5. Token is cached in-memory on the client instance.
   When expired, step 2 runs again automatically.
```

**Base URL**: `https://open.tiktokapis.com/v2/research`

**File**: `backend/tiktok/research/client.py`

The `TikTokResearchClient` handles token acquisition transparently via `_ensure_token()`. You do not need to manually manage tokens for this platform.

### Available Methods

The Research client (`backend/tiktok/research/client.py`) provides four high-level methods:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `query_videos()` | `/video/query/` | Search public videos by hashtag, keyword, username, or region. Returns view/like/comment/share counts. |
| `query_user_info()` | `/user/info/` | Get public profile info: display name, follower/following counts, likes, video count, bio, avatar. |
| `query_video_comments()` | `/video/comment/list/` | List comments on a public video by video ID. |
| `query_user_followers()` | `/user/followers/` | List followers of a public user by username. |

All methods use POST requests with JSON bodies.

### Gotchas and Common Mistakes

| Gotcha | Detail |
|--------|--------|
| **Requires TikTok approval** | Unlike the other platforms, you cannot just register and start using the Research API. TikTok must explicitly approve your application, which can take days or weeks. |
| **Strictest rate limit: 5 QPS** | This is the lowest rate limit of all five platforms. Heavy batch queries will be throttled quickly. |
| **Public data only** | The Research API only returns publicly available data. Private accounts, deleted videos, and restricted content are not accessible. |
| **Cursor-based pagination** | Large result sets use cursor pagination. Pass the cursor from the previous response to get the next page. |
| **No ConnectedAccount needed** | Unlike Shop, Developer, and Marketing, the Research API uses app-level credentials (not per-user tokens). There is no ConnectedAccount or TokenVault entry. The client key and secret are read directly from environment variables. |
| **Date format** | Video queries require `start_date` and `end_date` in `YYYYMMDD` format (e.g., `"20240101"`), not ISO 8601. |

### Verification

```bash
python -m scripts.verify.verify_research
```

This script obtains a client credentials token and makes a test video query. If the token is obtained but the query fails with a 429, the script reports success (credentials work, just rate limited).

---

## 7. TikTok LIVE Setup

### What It Is

TikTok LIVE is TikTok's live streaming feature. Unlike the other four platforms, Frodo does **not** connect to an official TikTok API. Instead, it uses the **TikTokLive** third-party open-source Python library, which connects to public LIVE streams via WebSocket and receives real-time events (comments, gifts, likes, follows, shares, joins, and stream endings).

**No registration, no credentials, no environment variables required.**

### Setup

The only requirement is installing the TikTokLive package:

```bash
pip install TikTokLive
```

That is it. No TikTok developer account, no app registration, no API keys.

### How It Works

**File**: `backend/tiktok/live/client.py` (class `TikTokLiveClientWrapper`)

The wrapper accepts a TikTok `unique_id` (username) and connects to their live stream:

```python
from backend.tiktok.live.client import TikTokLiveClientWrapper, LiveEventType

wrapper = TikTokLiveClientWrapper(unique_id="@username")

# Register callbacks
wrapper.on_event(LiveEventType.COMMENT, my_comment_handler)
wrapper.on_event(LiveEventType.GIFT, my_gift_handler)

# Connect (blocks until stream ends or disconnect)
await wrapper.connect()
```

### Event Types

The wrapper dispatches 7 event types as frozen `LiveEventData` dataclass instances:

| Event Type | Trigger | Payload |
|-----------|---------|---------|
| `COMMENT` | Viewer posts a chat message | `{"comment": "text"}` |
| `GIFT` | Viewer sends a gift | `{"gift_name": "...", "repeat_count": N}` |
| `LIKE` | Viewer likes the stream | `{}` |
| `FOLLOW` | Viewer follows the streamer | `{}` |
| `SHARE` | Viewer shares the stream | `{}` |
| `JOIN` | Viewer joins the stream | `{}` |
| `LIVE_END` | Stream ends | `{}` |

Each event includes `event_type`, `user_id`, `username`, `payload`, and `timestamp` (UTC).

### Gotchas and Common Mistakes

| Gotcha | Detail |
|--------|--------|
| **Third-party library** | TikTokLive is not an official TikTok product. It reverse-engineers the public WebSocket protocol. TikTok may change the protocol without notice, breaking the library. |
| **Unstable connections** | WebSocket connections to LIVE streams can drop due to network issues, TikTok server changes, or stream configuration. The wrapper does not currently implement automatic reconnection. |
| **Pin the version** | Add `TikTokLive==X.Y.Z` to your requirements.txt with a specific version. Upgrades may introduce breaking changes. |
| **100 QPS safety net** | The PlatformGateway applies a 100 QPS rate limit to LIVE, even though there is no formal TikTok-imposed limit. This prevents accidental resource exhaustion. |
| **Partially implemented** | LIVE is the least mature integration in Frodo. Connection management, automatic reconnection, and event processing/storage still need additional work. |
| **NotImplementedError** | If the TikTokLive package is not installed, calling `wrapper.connect()` raises `NotImplementedError` with a helpful message. The wrapper can still be instantiated for testing. |

### Current Status

LIVE is the least mature of the five platform integrations. The following areas need additional development:

- Automatic reconnection on disconnect
- Persistent event storage (currently events are dispatched to callbacks but not persisted to the database)
- Stream health monitoring
- Multi-stream management (connecting to multiple LIVE streams simultaneously)

### Verification

```bash
python -m scripts.verify.verify_live
```

This script checks that the TikTokLive package is installed and that the Frodo wrapper can be instantiated with all 7 event types. No network calls are made.

---

## 8. Verification & Troubleshooting

### Pre-Flight Checklist

Before running any verification scripts, confirm the following:

| Check | Command | Expected Result |
|-------|---------|-----------------|
| Docker services running | `docker compose ps` | All 5 services show "Up" (api, celery-worker, celery-beat, postgres, redis) |
| PostgreSQL healthy | `docker compose exec postgres pg_isready -U frodo` | "accepting connections" |
| Redis healthy | `docker compose exec redis redis-cli ping` | "PONG" |
| Migrations applied | `alembic current` | Shows latest migration revision |
| .env exists | `test -f .env && echo OK` | "OK" |
| API health check | `curl http://localhost:8000/health` | 200 OK |

### Run All Verification Scripts

```bash
python -m scripts.verify.verify_all
```

This runs all 5 platform verification scripts in sequence and prints a summary:

```
============================================================
Frodo Platform Verification Suite
============================================================

--- Shop ---
[OK] TikTok Shop: Credentials valid (signature accepted). ...

--- Developer ---
[OK] TikTok Developer: Credentials accepted by TikTok. ...

--- Marketing ---
[OK] TikTok Marketing: Credentials valid (app_id + secret accepted). ...

--- Research ---
[OK] TikTok Research: Client credentials token obtained
[OK] TikTok Research: Video query returned N result(s)

--- Live ---
[OK] TikTok LIVE: TikTokLive package installed
[OK] TikTok LIVE: Frodo wrapper instantiated - 7 event types registered

============================================================
Summary
============================================================
  [OK] Shop
  [OK] Developer
  [OK] Marketing
  [OK] Research
  [OK] Live

All 5 platforms verified successfully.
```

### Per-Platform Verification Commands

| Platform | Command | What It Tests |
|----------|---------|---------------|
| Shop | `python -m scripts.verify.verify_shop` | HMAC-SHA256 signature generation, API connectivity |
| Developer | `python -m scripts.verify.verify_developer` | Client key/secret validity via token endpoint |
| Marketing | `python -m scripts.verify.verify_marketing` | App ID/secret validity, optional SDK detection |
| Research | `python -m scripts.verify.verify_research` | Client credentials token exchange, test video query |
| LIVE | `python -m scripts.verify.verify_live` | TikTokLive package installation, wrapper instantiation |

### System-Level Checks

Beyond per-platform verification, you should also check these system components:

**Token Vault Encryption**

Verify that token encryption/decryption works with your `TOKEN_VAULT_KEY`:

```python
python -c "
from backend.utils.crypto import encrypt_token, decrypt_token
test = 'hello_world_test_token'
encrypted = encrypt_token(test)
decrypted = decrypt_token(encrypted)
assert decrypted == test
print('[OK] Token vault encryption/decryption working')
"
```

**Celery Registered Tasks**

Verify that Celery has discovered all worker tasks:

```bash
docker compose exec celery-worker celery -A backend.workers.celery_app inspect registered
```

Look for these token-related tasks:
- `backend.workers.token_refresh.refresh_developer_tokens`
- `backend.workers.token_refresh.refresh_shop_tokens`
- `backend.workers.token_refresh.check_marketing_tokens`

**Redis Rate Limiter Keys**

After making some API calls, check that rate limiter keys are being created:

```bash
docker compose exec redis redis-cli KEYS "rate_limit:*"
```

Expected format: `rate_limit:{platform}:{account_id}`

**Circuit Breaker State**

Circuit breakers are in-memory (not persisted to Redis). They reset when the API process restarts. To check current state during runtime, query the health endpoint or add logging to `backend/tiktok/gateway.py`.

### Troubleshooting

| # | Symptom | Likely Cause | Fix |
|---|---------|--------------|-----|
| 1 | **Shop API returns 401** | Access token expired (>7 days without Celery refresh) | Check Celery Beat is running. Verify `refresh_shop_tokens` task is in the beat schedule. If token is beyond repair, have the seller re-authorize via `/connect/shop/authorize`. |
| 2 | **Developer API returns 401** | Access token expired (>24 hours without Celery refresh) | This is the most time-sensitive token. Check Celery Beat status: `docker compose ps celery-beat`. Check task logs: `docker compose logs celery-worker`. If refresh token is also expired (>365 days), user must re-authorize. |
| 3 | **Developer API returns empty data** | Missing `fields` parameter in the API request | Many Developer API endpoints return empty results if the `fields` query parameter is not specified. Check the request in the service layer and ensure `fields` is included. |
| 4 | **Marketing API returns 401** | Token revoked by advertiser in Business Center | Re-connect the advertiser via `/connect/marketing/authorize`. Marketing tokens do not expire on a schedule but can be revoked at any time. |
| 5 | **Any platform returns 429** | Rate limit exceeded | The rate limiter should prevent this, but if it happens: (a) check Redis is accessible, (b) verify rate limiter keys exist (`redis-cli KEYS "rate_limit:*"`), (c) check if multiple instances are sharing the same Redis. |
| 6 | **Requests fail immediately with CircuitBreakerOpen** | Platform had 5+ failures in 60 seconds, circuit is OPEN | Wait 30 seconds for the circuit breaker to transition to HALF_OPEN and allow a probe request. If the underlying issue is resolved, the circuit will close automatically. To force reset, restart the API container. |
| 7 | **Token vault decrypt fails with InvalidTag** | `TOKEN_VAULT_KEY` was changed or corrupted | If you changed the key, all existing encrypted tokens are permanently unreadable. You must have users re-authorize all connected accounts. Restore the original key from backups if possible. |
| 8 | **Celery tasks not running on schedule** | Celery Beat not started or not discovering tasks | Verify Celery Beat is running: `docker compose ps celery-beat`. Check logs: `docker compose logs celery-beat`. Ensure `backend.workers` is in the autodiscover path. Run `celery -A backend.workers.celery_app inspect active` to check worker status. |
| 9 | **Research API returns 403** | Application not approved by TikTok, or credentials are for a different API | Research API requires explicit approval from TikTok. Verify your application status at developers.tiktok.com. Ensure you are using the Research API client key/secret, not the Developer API credentials (they are separate). |
| 10 | **LIVE raises NotImplementedError** | TikTokLive package not installed | Run `pip install TikTokLive`. The wrapper gracefully degrades -- it can be instantiated without the package, but `connect()` will raise NotImplementedError. Check installation: `python -c "import TikTokLive; print(TikTokLive.__version__)"`. |

### Celery Beat Schedule Reference

For completeness, here are all token-related scheduled tasks:

| Task | Schedule | Purpose |
|------|----------|---------|
| `refresh_developer_tokens` | Every 12 hours | Refresh 24h Developer access tokens |
| `refresh_shop_tokens` | Daily at midnight UTC | Refresh 7-day Shop access tokens |
| `check_marketing_tokens` | Daily at 6 AM UTC | Validate long-term Marketing tokens |

All tasks have `max_retries=3` with a 60-second retry delay.

---

## Appendix: Quick Reference Card

### Platform Credentials Summary

| Platform | Env Var 1 | Env Var 2 | Portal |
|----------|-----------|-----------|--------|
| Shop | `TIKTOK_SHOP_APP_KEY` | `TIKTOK_SHOP_APP_SECRET` | partner.tiktokshop.com |
| Developer | `TIKTOK_DEVELOPER_CLIENT_KEY` | `TIKTOK_DEVELOPER_CLIENT_SECRET` | developers.tiktok.com |
| Marketing | `TIKTOK_MARKETING_APP_ID` | `TIKTOK_MARKETING_APP_SECRET` | business-api.tiktok.com |
| Research | `TIKTOK_RESEARCH_CLIENT_KEY` | `TIKTOK_RESEARCH_CLIENT_SECRET` | developers.tiktok.com (Research section) |
| LIVE | None | None | No registration needed |

### OAuth Callback URLs

| Platform | Callback URL |
|----------|-------------|
| Shop | `{BACKEND_URL}/api/connect/shop/callback` |
| Developer | `{BACKEND_URL}/api/connect/developer/callback` |
| Marketing | `{BACKEND_URL}/api/connect/marketing/callback` |
| Research | N/A (server-to-server) |
| LIVE | N/A (WebSocket) |

### Token Lifetimes

| Platform | Access Token | Refresh Token | Auto-Refresh |
|----------|-------------|---------------|--------------|
| Shop | 7 days | Included in refresh response | Daily (Celery) |
| Developer | 24 hours | 365 days | Every 12h (Celery) |
| Marketing | No expiry (long-term) | N/A | Validated daily (Celery) |
| Research | Short-lived | N/A | Per-request (in-memory) |
| LIVE | N/A | N/A | N/A |

### Key Source Files

| File | Purpose |
|------|---------|
| `backend/config.py` | All settings and environment variable mappings |
| `backend/db/models/platform.py` | Platform, AccountStatus, ConnectedAccount, TokenVault models |
| `backend/utils/crypto.py` | AES-256-GCM encrypt/decrypt for TokenVault |
| `backend/tiktok/gateway.py` | PlatformGateway (rate limit + circuit breaker + retry) |
| `backend/tiktok/rate_limiter.py` | Redis-backed token bucket rate limiters |
| `backend/tiktok/circuit_breaker.py` | Per-platform circuit breaker |
| `backend/tiktok/retry.py` | Exponential backoff retry wrapper |
| `backend/tiktok/shop/client.py` | Shop API client with HMAC-SHA256 signing |
| `backend/tiktok/developer/client.py` | Developer API client with Bearer auth |
| `backend/tiktok/marketing/client.py` | Marketing API client with SDK adapter |
| `backend/tiktok/research/client.py` | Research API client with client credentials |
| `backend/tiktok/live/client.py` | LIVE WebSocket wrapper |
| `backend/modules/connect/routes.py` | OAuth callback handlers for Shop, Developer, Marketing |
| `backend/workers/token_refresh.py` | Celery tasks for token refresh and validation |
| `backend/workers/celery_app.py` | Celery configuration and beat schedule |
| `scripts/verify/verify_all.py` | Run all verification scripts |
| `docker-compose.yml` | Container definitions |
| `.env.example` | Environment variable template |

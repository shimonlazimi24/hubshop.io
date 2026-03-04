# Process Flow Guide

Detailed sequence diagrams and step-by-step explanations for every major process in the Frodo platform. Each flow includes the key files involved and error handling behavior.

---

## Table of Contents

1. [User Authentication Flow](#1-user-authentication-flow)
2. [Organization & Workspace Setup Flow](#2-organization--workspace-setup-flow)
3. [TikTok Platform Connection Flow](#3-tiktok-platform-connection-flow)
4. [API Request Flow (Through Gateway)](#4-api-request-flow-through-gateway)
5. [Data Sync Pipeline](#5-data-sync-pipeline)
6. [Webhook Processing Flow](#6-webhook-processing-flow)
7. [Real-Time Events Flow](#7-real-time-events-flow)
8. [SDK Sidecar Flow](#8-sdk-sidecar-flow)

---

## 1. User Authentication Flow

### 1a. Email/Password Registration

```
Browser                    FastAPI Backend                  PostgreSQL
  |                            |                               |
  |  POST /api/auth/register   |                               |
  |  {email, password,         |                               |
  |   full_name, org_name}     |                               |
  |--------------------------->|                               |
  |                            |  SELECT user WHERE email=X    |
  |                            |------------------------------>|
  |                            |  (check no duplicate)         |
  |                            |<------------------------------|
  |                            |                               |
  |                            |  INSERT INTO users            |
  |                            |  (email, hashed_password,     |
  |                            |   full_name)                  |
  |                            |------------------------------>|
  |                            |  user.id                      |
  |                            |<------------------------------|
  |                            |                               |
  |                            |  INSERT INTO organizations    |
  |                            |  (name, slug)                 |
  |                            |------------------------------>|
  |                            |  org.id                       |
  |                            |<------------------------------|
  |                            |                               |
  |                            |  INSERT INTO workspaces       |
  |                            |  (name="Default", org_id)     |
  |                            |------------------------------>|
  |                            |  workspace.id                 |
  |                            |<------------------------------|
  |                            |                               |
  |                            |  INSERT INTO memberships      |
  |                            |  (user_id, org_id,            |
  |                            |   workspace_id, role=OWNER)   |
  |                            |------------------------------>|
  |                            |<------------------------------|
  |                            |                               |
  |                            |  create_access_token()        |
  |                            |  create_refresh_token()       |
  |                            |  (HS256, 15min / 7d)          |
  |                            |                               |
  |  {access_token,            |                               |
  |   refresh_token}           |                               |
  |<---------------------------|                               |
```

**Step-by-step:**

1. Client sends email, password, full_name, and organization_name to `POST /api/auth/register`.
2. Backend checks for duplicate email (409 Conflict if found).
3. Password is hashed with bcrypt via `hash_password()`.
4. A new `User` row is inserted.
5. An `Organization` row is created from the provided name (slug is auto-generated).
6. A default `Workspace` named "Default" is created under the org.
7. A `Membership` row links the user to org+workspace with `OWNER` role.
8. JWT access token (15min, HS256) and refresh token (7 days) are returned.

**Key files:**
- `backend/auth/routes.py` -- `register()` endpoint (line 50)
- `backend/auth/jwt.py` -- `create_access_token()`, `create_refresh_token()`
- `backend/auth/passwords.py` -- `hash_password()`, `verify_password()`
- `backend/db/models/user.py` -- User model
- `backend/db/models/organization.py` -- Organization, Workspace, Membership, Role

**Error handling:**
- Duplicate email: 409 Conflict
- Invalid input: 422 Validation Error (Pydantic)

---

### 1b. Email/Password Login

```
Browser                    FastAPI Backend                  PostgreSQL
  |                            |                               |
  |  POST /api/auth/login      |                               |
  |  {email, password}         |                               |
  |--------------------------->|                               |
  |                            |  SELECT user WHERE email=X    |
  |                            |------------------------------>|
  |                            |<------------------------------|
  |                            |                               |
  |                            |  verify_password(password,    |
  |                            |    user.hashed_password)      |
  |                            |                               |
  |                            |  check user.is_active         |
  |                            |                               |
  |                            |  SELECT membership            |
  |                            |  WHERE user_id = user.id      |
  |                            |  LIMIT 1                      |
  |                            |------------------------------>|
  |                            |<------------------------------|
  |                            |                               |
  |                            |  create_access_token(         |
  |                            |    user_id, org_id, role)     |
  |                            |  create_refresh_token(        |
  |                            |    user_id)                   |
  |                            |                               |
  |  {access_token,            |                               |
  |   refresh_token}           |                               |
  |<---------------------------|                               |
```

**Step-by-step:**

1. Client sends email + password to `POST /api/auth/login`.
2. Backend looks up the user by email.
3. Password is verified against stored bcrypt hash.
4. User `is_active` flag is checked (403 if disabled).
5. First membership is loaded to embed `org_id` and `role` in the JWT claims.
6. Access token (15min) and refresh token (7 days) are returned.

**Error handling:**
- Wrong email or password: 401 Unauthorized ("Invalid email or password")
- Disabled account: 403 Forbidden ("Account is disabled")

---

### 1c. TikTok OAuth Social Login

```
Browser                    FastAPI Backend          TikTok OAuth        PostgreSQL
  |                            |                       |                    |
  |  GET /api/auth/            |                       |                    |
  |      tiktok/login          |                       |                    |
  |--------------------------->|                       |                    |
  |                            |                       |                    |
  |  {authorize_url}           |                       |                    |
  |<---------------------------|                       |                    |
  |                            |                       |                    |
  |  User clicks               |                       |                    |
  |  authorize_url             |                       |                    |
  |--------------------------------------->|           |                    |
  |                            |           |           |                    |
  |  TikTok login page         |           |           |                    |
  |<---------------------------------------|           |                    |
  |                            |           |           |                    |
  |  User authorizes           |           |           |                    |
  |  Redirect to callback      |           |           |                    |
  |  with ?code=X&state=Y      |           |           |                    |
  |                            |           |           |                    |
  |  GET /api/auth/            |                       |                    |
  |      tiktok/callback       |                       |                    |
  |      ?code=X&state=Y       |                       |                    |
  |--------------------------->|                       |                    |
  |                            |  POST token exchange  |                    |
  |                            |  (code, client_key,   |                    |
  |                            |   client_secret)      |                    |
  |                            |---------------------->|                    |
  |                            |  {access_token,       |                    |
  |                            |   open_id}            |                    |
  |                            |<----------------------|                    |
  |                            |                       |                    |
  |                            |  GET /v2/user/info/   |                    |
  |                            |  Bearer access_token  |                    |
  |                            |---------------------->|                    |
  |                            |  {display_name,       |                    |
  |                            |   avatar_url}         |                    |
  |                            |<----------------------|                    |
  |                            |                       |                    |
  |                            |  get_or_create_user() |                    |
  |                            |  (lookup by           |                    |
  |                            |   social_identity OR  |                    |
  |                            |   create new user)    |                    |
  |                            |-------------------------------------->|    |
  |                            |                       |               |    |
  |                            |  ensure_membership()  |               |    |
  |                            |  (create org +        |               |    |
  |                            |   workspace if new)   |               |    |
  |                            |-------------------------------------->|    |
  |                            |<--------------------------------------|    |
  |                            |                       |                    |
  |  {access_token,            |                       |                    |
  |   refresh_token}           |                       |                    |
  |<---------------------------|                       |                    |
```

**Step-by-step:**

1. Frontend calls `GET /api/auth/tiktok/login` to get the TikTok authorize URL.
2. URL includes `client_key`, `response_type=code`, `scope=user.info.basic,user.info.profile`, `redirect_uri`, and a random `state`.
3. User is redirected to TikTok, logs in, and authorizes the app.
4. TikTok redirects back to `/api/auth/tiktok/callback?code=X&state=Y`.
5. Backend exchanges the `code` for a TikTok access token via `POST https://open.tiktokapis.com/v2/oauth/token/`.
6. Backend fetches the user's TikTok profile (`open_id`, `display_name`, `avatar_url`).
7. `SocialAuthService.get_or_create_user()` checks `social_identities` table:
   - If a `SocialIdentity` with `(provider=tiktok, provider_user_id=open_id)` exists, return the linked user.
   - If not, check if a user with the same email exists and link the identity.
   - Otherwise, create a new user with `hashed_password=None` (social-only account).
8. `_ensure_membership()` creates org + workspace + membership if the user has none.
9. JWT access + refresh tokens are returned (same format as email/password login).

**Key files:**
- `backend/auth/routes.py` -- `tiktok_login()` (line 195), `tiktok_callback()` (line 203)
- `backend/auth/social.py` -- `SocialAuthService`, `get_or_create_user()`, `build_tiktok_login_url()`
- `backend/db/models/social_identity.py` -- SocialIdentity, SocialProvider

**Error handling:**
- Token exchange failure: 502 Bad Gateway
- Missing access_token in TikTok response: 502 Bad Gateway
- Existing social identity: links to existing user (no error)

---

### 1d. Google OAuth Social Login

```
Browser                    FastAPI Backend          Google OAuth         PostgreSQL
  |                            |                       |                    |
  |  GET /api/auth/            |                       |                    |
  |      google/login          |                       |                    |
  |--------------------------->|                       |                    |
  |  {authorize_url}           |                       |                    |
  |<---------------------------|                       |                    |
  |                            |                       |                    |
  |  User clicks authorize_url |                       |                    |
  |--------------------------------------->|           |                    |
  |  Google consent screen     |           |           |                    |
  |<---------------------------------------|           |                    |
  |  User authorizes,          |           |           |                    |
  |  redirect with ?code=X     |           |           |                    |
  |                            |                       |                    |
  |  GET /api/auth/            |                       |                    |
  |      google/callback       |                       |                    |
  |      ?code=X&state=Y       |                       |                    |
  |--------------------------->|                       |                    |
  |                            |  POST oauth2/token    |                    |
  |                            |  (code, client_id,    |                    |
  |                            |   client_secret)      |                    |
  |                            |---------------------->|                    |
  |                            |  {access_token}       |                    |
  |                            |<----------------------|                    |
  |                            |                       |                    |
  |                            |  GET /oauth2/v2/      |                    |
  |                            |      userinfo         |                    |
  |                            |---------------------->|                    |
  |                            |  {id, email, name,    |                    |
  |                            |   picture}            |                    |
  |                            |<----------------------|                    |
  |                            |                       |                    |
  |                            |  get_or_create_user() |                    |
  |                            |  (same as TikTok      |                    |
  |                            |   but with email      |                    |
  |                            |   matching)           |                    |
  |                            |-------------------------------------->|    |
  |                            |<--------------------------------------|    |
  |                            |                       |                    |
  |  {access_token,            |                       |                    |
  |   refresh_token}           |                       |                    |
  |<---------------------------|                       |                    |
```

**Step-by-step:**

1. Frontend calls `GET /api/auth/google/login` to get the Google OAuth URL.
2. URL uses `scope=openid email profile`, `access_type=offline`, `prompt=consent`.
3. User authorizes on Google consent screen, is redirected back with `code`.
4. Backend exchanges `code` at `https://oauth2.googleapis.com/token`.
5. Backend fetches user info from `https://www.googleapis.com/oauth2/v2/userinfo` to get `id`, `email`, `name`, `picture`.
6. `get_or_create_user()` is called with `provider=GOOGLE` and the Google `id`. If a user with the same email already exists, the social identity is linked to the existing account.
7. JWT tokens are returned.

**Key files:**
- `backend/auth/routes.py` -- `google_login()` (line 274), `google_callback()` (line 282)
- `backend/auth/social.py` -- `build_google_login_url()`, `get_or_create_user()`

---

### 1e. JWT Token Lifecycle

```
                        Token Creation
                        ===============
                        Access Token (15 min):
                          claims: {sub: user_id, org_id, role, type: "access", exp}
                          algorithm: HS256
                          key: settings.jwt_secret_key

                        Refresh Token (7 days):
                          claims: {sub: user_id, type: "refresh", exp}
                          algorithm: HS256
                          key: settings.jwt_secret_key


Client                     FastAPI Backend                     PostgreSQL
  |                            |                                   |
  |  API Request               |                                   |
  |  Authorization: Bearer     |                                   |
  |  <access_token>            |                                   |
  |--------------------------->|                                   |
  |                            |  decode_token(access_token)       |
  |                            |  Verify: HS256, expiry, type      |
  |                            |  Extract: user_id from "sub"      |
  |                            |                                   |
  |                            |  SELECT user WHERE id=user_id     |
  |                            |  AND is_active = true             |
  |                            |---------------------------------->|
  |                            |<----------------------------------|
  |                            |                                   |
  |  API Response              |                                   |
  |<---------------------------|                                   |
  |                            |                                   |
  |  --- Access token expired ---                                  |
  |                            |                                   |
  |  POST /api/auth/refresh    |                                   |
  |  {refresh_token}           |                                   |
  |--------------------------->|                                   |
  |                            |  decode_token(refresh_token)      |
  |                            |  Verify type == "refresh"         |
  |                            |  Extract user_id                  |
  |                            |                                   |
  |                            |  SELECT user WHERE id=user_id     |
  |                            |  AND is_active = true             |
  |                            |---------------------------------->|
  |                            |<----------------------------------|
  |                            |                                   |
  |                            |  SELECT membership for user       |
  |                            |  (to embed fresh org_id + role)   |
  |                            |---------------------------------->|
  |                            |<----------------------------------|
  |                            |                                   |
  |  {new_access_token,        |                                   |
  |   new_refresh_token}       |                                   |
  |<---------------------------|                                   |
```

**Token claims structure:**

| Claim    | Access Token         | Refresh Token   |
|----------|----------------------|-----------------|
| `sub`    | user_id (UUID)       | user_id (UUID)  |
| `type`   | "access"             | "refresh"       |
| `exp`    | now + 15 minutes     | now + 7 days    |
| `org_id` | organization_id      | (not included)  |
| `role`   | user role string     | (not included)  |

**Key files:**
- `backend/auth/jwt.py` -- `create_access_token()`, `create_refresh_token()`, `decode_token()`
- `backend/dependencies.py` -- `get_current_user()` (extracts user from Bearer token)
- `backend/auth/routes.py` -- `refresh_tokens()` (line 129)
- `backend/config.py` -- `jwt_secret_key`, `jwt_algorithm`, `jwt_access_token_expire_minutes`, `jwt_refresh_token_expire_days`

**Error handling:**
- Expired token: 401 Unauthorized
- Invalid signature: 401 Unauthorized
- Wrong token type (refresh used as access): 401 Unauthorized
- User not found or inactive: 401 Unauthorized

---

## 2. Organization & Workspace Setup Flow

```
                           Registration Path
                           =================

User registers
       |
       v
+------------------+
|   Create User    |  (email, hashed_password, full_name)
+------------------+
       |
       v
+------------------+
| Create Org       |  (name from request, slug auto-generated)
+------------------+
       |
       v
+------------------+
| Create Workspace |  (name="Default", slug="default", org_id)
+------------------+
       |
       v
+------------------+
| Create Membership|  (user_id, org_id, workspace_id, role=OWNER)
+------------------+
       |
       v
  Return JWT tokens
  (org_id + role embedded in access token)


                           Social Login Path
                           ================

Social user (no existing account)
       |
       v
+------------------+
|   Create User    |  (email from provider or synthetic,
|                  |   hashed_password=NULL)
+------------------+
       |
       v
+------------------+
| Create Social    |  (user_id, provider, provider_user_id)
| Identity         |
+------------------+
       |
       v
+------------------+
| _ensure_         |  Check: does user have any membership?
| membership()     |  If NO:
+------------------+    - Create org (name from email domain)
       |                - Create workspace ("Default")
       v                - Create membership (role=OWNER)
  Return JWT tokens
```

### Role Hierarchy (5-tier RBAC)

```
  OWNER (4)     Full control, billing, delete org
    |
  ADMIN (3)     Manage members, settings, all data
    |
  MANAGER (2)   Manage data within workspace
    |
  MEMBER (1)    Read/write own data
    |
  VIEWER (0)    Read-only access
```

RBAC enforcement uses `has_permission(user_role, required_role)` which compares hierarchy indices. The `require_role()` decorator is applied to route handlers that need permission checks.

**Key files:**
- `backend/auth/routes.py` -- `register()` (creates all 4 entities in one transaction)
- `backend/auth/social.py` -- `_ensure_membership()` (creates org/workspace/membership for social users)
- `backend/auth/rbac.py` -- `has_permission()`, `require_role()` decorator
- `backend/db/models/organization.py` -- Organization, Workspace, Membership, Role enum

**Data relationships:**

```
Organization (1) ---< Workspace (many)
Organization (1) ---< Membership (many)
User (1) ----------< Membership (many)
Workspace (1) -----< Membership (many)
                      (user_id + organization_id + workspace_id = unique)
```

---

## 3. TikTok Platform Connection Flow

Each TikTok platform (Shop, Developer, Marketing) has its own OAuth flow. They all follow the same pattern: authorize URL -> user consent -> callback -> token exchange -> encrypt & store -> redirect to frontend.

### 3a. TikTok Shop Connection

```
Browser                 FastAPI Backend          TikTok Shop OAuth        PostgreSQL
  |                          |                        |                       |
  |  GET /api/connect/       |                        |                       |
  |  shop/authorize          |                        |                       |
  |  ?workspace_id=X         |                        |                       |
  |------------------------->|                        |                       |
  |                          |  Build authorize URL   |                       |
  |                          |  state=workspace:user  |                       |
  |  {authorize_url}         |                        |                       |
  |<-------------------------|                        |                       |
  |                          |                        |                       |
  |  Redirect to TikTok      |                        |                       |
  |  Shop seller auth page   |                        |                       |
  |----------------------------------------->|        |                       |
  |  Seller authorizes       |               |        |                       |
  |<-----------------------------------------|        |                       |
  |                          |                        |                       |
  |  GET /api/connect/       |                        |                       |
  |  shop/callback           |                        |                       |
  |  ?code=X&state=Y         |                        |                       |
  |------------------------->|                        |                       |
  |                          |  GET /api/v2/token/get |                       |
  |                          |  (app_key, app_secret, |                       |
  |                          |   auth_code)           |                       |
  |                          |----------------------->|                       |
  |                          |  {access_token,        |                       |
  |                          |   refresh_token,       |                       |
  |                          |   seller_id,           |                       |
  |                          |   shop_cipher_list}    |                       |
  |                          |<-----------------------|                       |
  |                          |                        |                       |
  |                          |  encrypt_token()       |                       |
  |                          |  (AES-256-GCM)         |                       |
  |                          |                        |                       |
  |                          |  INSERT connected_account                      |
  |                          |  (workspace_id, platform=SHOP,                 |
  |                          |   platform_account_id=seller_id,               |
  |                          |   metadata={shop_ciphers: [...]})              |
  |                          |----------------------------------------------->|
  |                          |<-----------------------------------------------|
  |                          |                        |                       |
  |                          |  INSERT token_vault    |                       |
  |                          |  (connected_account_id,|                       |
  |                          |   encrypted_access,    |                       |
  |                          |   encrypted_refresh)   |                       |
  |                          |----------------------------------------------->|
  |                          |<-----------------------------------------------|
  |                          |                        |                       |
  |  302 Redirect to         |                        |                       |
  |  /connect/sync?           |                        |                       |
  |  platform=shop&           |                        |                       |
  |  account_id=UUID          |                        |                       |
  |<-------------------------|                        |                       |
```

### 3b. Token Encryption (AES-256-GCM Vault)

```
Plaintext Token              encrypt_token()                Token Vault DB
     |                            |                              |
     |   "tk_abc123..."           |                              |
     |--------------------------->|                              |
     |                            |                              |
     |                            |  1. Load 256-bit key from    |
     |                            |     TOKEN_VAULT_KEY env var  |
     |                            |     (base64-decoded)         |
     |                            |                              |
     |                            |  2. Generate random 96-bit   |
     |                            |     nonce (12 bytes)         |
     |                            |                              |
     |                            |  3. AES-256-GCM encrypt:     |
     |                            |     ciphertext = AESGCM(     |
     |                            |       key, nonce, plaintext) |
     |                            |                              |
     |                            |  4. Return base64(           |
     |                            |       nonce + ciphertext)    |
     |                            |                              |
     |                            |  Store as TEXT in             |
     |                            |  token_vault table            |
     |                            |------------------------------>|
```

**Key files:**
- `backend/modules/connect/routes.py` -- `shop_authorize()`, `shop_callback()`, `developer_authorize()`, `developer_callback()`, `marketing_authorize()`, `marketing_callback()`
- `backend/utils/crypto.py` -- `encrypt_token()`, `decrypt_token()`
- `backend/db/models/platform.py` -- ConnectedAccount, TokenVault, Platform, AccountStatus

### 3c. Token Auto-Refresh via Celery Beat

```
Celery Beat                    Celery Worker              TikTok API           PostgreSQL
  |                                |                         |                     |
  | (cron trigger)                 |                         |                     |
  | Every 12h: developer tokens    |                         |                     |
  | Daily:     shop tokens         |                         |                     |
  | Daily 6AM: marketing check     |                         |                     |
  |------------------------------->|                         |                     |
  |                                |                         |                     |
  |                                |  SELECT connected_accounts                    |
  |                                |  WHERE platform=X AND status=ACTIVE           |
  |                                |---------------------------------------------->|
  |                                |  [account1, account2, ...]                    |
  |                                |<----------------------------------------------|
  |                                |                         |                     |
  |                                |  For each account:      |                     |
  |                                |                         |                     |
  |                                |  SELECT token_vault     |                     |
  |                                |  WHERE connected_account_id = account.id      |
  |                                |---------------------------------------------->|
  |                                |<----------------------------------------------|
  |                                |                         |                     |
  |                                |  decrypt_token(         |                     |
  |                                |    encrypted_refresh)   |                     |
  |                                |                         |                     |
  |                                |  POST token refresh     |                     |
  |                                |  (refresh_token,        |                     |
  |                                |   client credentials)   |                     |
  |                                |------------------------>|                     |
  |                                |  {new_access_token,     |                     |
  |                                |   new_refresh_token}    |                     |
  |                                |<------------------------|                     |
  |                                |                         |                     |
  |                                |  encrypt_token()        |                     |
  |                                |  UPDATE token_vault     |                     |
  |                                |  SET encrypted_access,  |                     |
  |                                |      encrypted_refresh  |                     |
  |                                |---------------------------------------------->|
  |                                |                         |                     |
  |                                | (on failure)            |                     |
  |                                |  UPDATE connected_account                     |
  |                                |  SET status = ERROR     |                     |
  |                                |---------------------------------------------->|
```

**Refresh schedules (from `celery_app.py` beat_schedule):**

| Task                         | Schedule           | Platform   |
|------------------------------|--------------------|------------|
| `refresh_developer_tokens`   | Every 12 hours     | Developer  |
| `refresh_shop_tokens`        | Daily at midnight  | Shop       |
| `check_marketing_tokens`     | Daily at 6 AM      | Marketing  |

**Token refresh endpoints:**

| Platform   | URL                                                    | Method |
|------------|--------------------------------------------------------|--------|
| Developer  | `https://open.tiktokapis.com/v2/oauth/token/`          | POST   |
| Shop       | `https://auth.tiktok-shops.com/api/v2/token/refresh`   | GET    |
| Marketing  | Health check via `GET .../v1.3/user/info/`             | GET    |

**Error handling:**
- Refresh failure: Celery task retries 3 times with 60s delay.
- Persistent failure: Account `status` set to `ERROR`, logged as warning.
- Marketing tokens have no refresh (long-lived). Health check verifies validity; marks as ERROR if invalid.

**Key files:**
- `backend/workers/token_refresh.py` -- `refresh_developer_tokens`, `refresh_shop_tokens`, `check_marketing_tokens`
- `backend/workers/celery_app.py` -- Beat schedule (lines 27-39)

---

## 4. API Request Flow (Through Gateway)

Every TikTok API call goes through the `PlatformGateway`, which applies a three-stage middleware chain: rate limiting, circuit breaking, and retry.

```
Service Layer              PlatformGateway             Redis              TikTok API
  |                             |                        |                    |
  |  gateway.get("/products")   |                        |                    |
  |  or gateway.post(...)       |                        |                    |
  |---------------------------->|                        |                    |
  |                             |                        |                    |
  |                    +--------+--------+               |                    |
  |                    | 1. CIRCUIT      |               |                    |
  |                    |    BREAKER      |               |                    |
  |                    |                 |               |                    |
  |                    | Check state:    |               |                    |
  |                    | CLOSED: proceed |               |                    |
  |                    | OPEN: fail-fast |               |                    |
  |                    | HALF_OPEN:      |               |                    |
  |                    |   allow 1 probe |               |                    |
  |                    +---------+-------+               |                    |
  |                              |                       |                    |
  |                    +---------+-------+               |                    |
  |                    | 2. RATE LIMITER |               |                    |
  |                    |  (Token Bucket) |               |                    |
  |                    |                 |               |                    |
  |                    | HMGET tokens,   |               |                    |
  |                    |   last_refill   |               |                    |
  |                    |-----------------|-------------->|                    |
  |                    |                 |<-------------|                    |
  |                    | Refill tokens   |               |                    |
  |                    | (elapsed *      |               |                    |
  |                    |  refill_rate)   |               |                    |
  |                    | If tokens < 1:  |               |                    |
  |                    |   REJECT        |               |                    |
  |                    | Else:           |               |                    |
  |                    |   tokens -= 1   |               |                    |
  |                    |   HSET + EXPIRE |               |                    |
  |                    |-----------------|-------------->|                    |
  |                    +---------+-------+               |                    |
  |                              |                       |                    |
  |                    +---------+-------+               |                    |
  |                    | 3. RETRY LOGIC  |               |                    |
  |                    |  (Exp Backoff)  |               |                    |
  |                    |                 |               |                    |
  |                    | Attempt 1:      |               |                    |
  |                    |   client.request(method, path)  |                    |
  |                    |---------------------------------------->|           |
  |                    |                 |               |        |           |
  |                    | If 429 / 5xx:  |               |        |           |
  |                    |   wait 1s       |               |        |           |
  |                    | Attempt 2:      |               |        |           |
  |                    |   client.request(method, path)  |        |           |
  |                    |---------------------------------------->|           |
  |                    |                 |               |        |           |
  |                    | If 429 / 5xx:  |               |        |           |
  |                    |   wait 2s       |               |        |           |
  |                    | Attempt 3:      |               |        |           |
  |                    |   client.request(method, path)  |        |           |
  |                    |---------------------------------------->|           |
  |                    |                 |               |  response          |
  |                    |<----------------------------------------|           |
  |                    +---------+-------+               |                    |
  |                              |                       |                    |
  |                    On success:                       |                    |
  |                      circuit_breaker.record_success()                     |
  |                    On failure:                       |                    |
  |                      circuit_breaker.record_failure()                     |
  |                              |                       |                    |
  |  response data               |                       |                    |
  |<-----------------------------|                       |                    |
```

### Rate Limits by Platform

| Platform   | Max Tokens (QPS) | Refill Rate | Redis Key Prefix |
|------------|------------------|-------------|------------------|
| Shop       | 50               | 50/s        | `rate_limit:shop`      |
| Developer  | 10               | 10/s        | `rate_limit:developer` |
| Marketing  | 10               | 10/s        | `rate_limit:marketing` |
| Research   | 5                | 5/s         | `rate_limit:research`  |
| LIVE       | 100              | 100/s       | `rate_limit:live`      |

### Circuit Breaker States

```
          5 failures in 60s
  CLOSED =====================> OPEN
    ^                            |
    |                            | 30s recovery timeout
    |     success                v
    +<================ HALF_OPEN
    |     failure          |
    |                      |
    +----> OPEN <----------+
```

- **CLOSED**: Normal operation. Counts failures within a 60-second window.
- **OPEN**: All requests immediately fail with `CircuitBreakerOpen`. Transitions to HALF_OPEN after 30 seconds.
- **HALF_OPEN**: Allows one probe request. Success resets to CLOSED; failure reopens.

### Retry Logic

- Retries on: 429, 500, 502, 503, 504 and transport errors.
- Does NOT retry on: 400, 401, 403, 404 (client errors).
- Backoff: 1s, 2s, 4s (exponential, base_delay=1.0, `delay = base_delay * 2^attempt`).
- Max retries: 3 attempts (initial + 3 retries = 4 total).

**Key files:**
- `backend/tiktok/gateway.py` -- `PlatformGateway.request()` orchestrates the chain
- `backend/tiktok/rate_limiter.py` -- `TokenBucketRateLimiter`, pre-configured per-platform limiters
- `backend/tiktok/circuit_breaker.py` -- `CircuitBreaker` state machine
- `backend/tiktok/retry.py` -- `with_retry()` exponential backoff wrapper

**Error propagation:**
1. `RateLimitExceeded` -- raised if token bucket is empty (no retry).
2. `CircuitBreakerOpen` -- raised if circuit is OPEN (immediate fail).
3. After max retries exceeded -- original `httpx.HTTPStatusError` or `httpx.TransportError` propagates.
4. Service layer catches and translates to appropriate HTTP responses for the client.

---

## 5. Data Sync Pipeline

### 5a. Periodic Sync (Celery Beat)

```
Celery Beat              Celery Worker            Gateway + TikTok API       PostgreSQL
  |                          |                          |                       |
  | (every 15min: orders)    |                          |                       |
  | (every 30min: products)  |                          |                       |
  |------------------------->|                          |                       |
  |                          |                          |                       |
  |                          |  SELECT shops            |                       |
  |                          |  FROM shops              |                       |
  |                          |----------------------------------------------------->|
  |                          |  [shop1, shop2, ...]     |                       |
  |                          |<-----------------------------------------------------|
  |                          |                          |                       |
  |                          |  For each shop:          |                       |
  |                          |                          |                       |
  |                          |  GET/CREATE sync_cursor  |                       |
  |                          |  (shop_id, sync_type)    |                       |
  |                          |----------------------------------------------------->|
  |                          |  cursor.last_sync_at     |                       |
  |                          |<-----------------------------------------------------|
  |                          |                          |                       |
  |                          |  Calculate time range:   |                       |
  |                          |  from = last_sync_at     |                       |
  |                          |         - 5min overlap   |                       |
  |                          |  to = now                |                       |
  |                          |  (first sync: 48h back)  |                       |
  |                          |                          |                       |
  |                          |  order_service.sync_orders()                      |
  |                          |  (uses PlatformGateway)  |                       |
  |                          |------------------------->|                       |
  |                          |                          | GET /orders/search    |
  |                          |                          |---> TikTok Shop API   |
  |                          |                          |<--- order data        |
  |                          |<-------------------------|                       |
  |                          |                          |                       |
  |                          |  UPSERT orders           |                       |
  |                          |  (ON CONFLICT UPDATE)    |                       |
  |                          |----------------------------------------------------->|
  |                          |                          |                       |
  |                          |  UPDATE sync_cursor      |                       |
  |                          |  SET last_sync_at = now  |                       |
  |                          |----------------------------------------------------->|
  |                          |                          |                       |
  |                          |  COMMIT                  |                       |
```

### Sync Schedule (Complete)

| Task                           | Schedule              | What Gets Synced                   |
|--------------------------------|-----------------------|------------------------------------|
| `sync_shop_orders`             | Every 15 minutes      | Orders from all active shops       |
| `sync_shop_products`           | Every 30 minutes      | Products from all active shops     |
| `sync_all_ad_accounts`         | Every 6 hours         | Ad account metadata                |
| `sync_ad_campaigns`            | Every 30 minutes      | Campaign data + metrics snapshots  |
| `sync_ad_groups`               | Every 30 min (offset) | Ad group data                      |
| `sync_ads`                     | Every 30 min (offset) | Individual ad data                 |
| `sync_all_videos`              | Every 30 minutes      | Video list from Developer API      |
| `sync_video_metrics`           | Every 6 hours         | Video engagement metrics           |
| `refresh_creator_profiles`     | Every 12 hours        | Creator profile data               |
| `take_daily_kpi_snapshots`     | Daily at 1 AM         | Daily KPI snapshot for analytics   |
| `run_scheduled_reports`        | Every 30 minutes      | Check for and execute due reports  |
| `sync_trends`                  | Every 4 hours         | Trend data from Research API       |
| `sync_competitor_content`      | Every 6 hours         | Competitor content tracking        |
| `cleanup_stale_live_sessions`  | Every hour            | Remove stale LIVE session records  |
| `sync_conversations`           | Every 30 minutes      | Messaging conversations            |
| `sync_mentions`                | Every 2 hours         | Social mentions                    |

### Sync Cursor Pattern

The sync system uses a `SyncCursor` table to track progress:

```
sync_cursors
  shop_id      UUID     -- FK to shops
  sync_type    TEXT     -- "orders", "products", etc.
  last_sync_at TIMESTAMPTZ  -- when last successful sync completed
```

On each sync:
1. Load cursor for `(shop_id, sync_type)`.
2. Calculate time range: `from = last_sync_at - 5 min overlap` to `now`.
3. If no cursor exists (first sync): look back 48 hours max.
4. After successful sync, update `last_sync_at = now`.
5. The 5-minute overlap window catches late-arriving data.

**Key files:**
- `backend/workers/data_sync.py` -- `sync_shop_orders`, `sync_shop_products`, cursor management
- `backend/workers/ad_sync.py` -- Ad campaign/group/ad sync tasks
- `backend/workers/content_sync.py` -- Video and metrics sync
- `backend/workers/creator_sync.py` -- Creator profile refresh
- `backend/workers/analytics_sync.py` -- KPI snapshots and scheduled reports
- `backend/workers/celery_app.py` -- Complete beat schedule (lines 27-107)
- `backend/modules/commerce/services/order_service.py` -- `sync_orders()`
- `backend/modules/commerce/services/product_service.py` -- `sync_products()`

**Error handling:**
- Per-shop isolation: if one shop fails, others continue (`try/except` per shop).
- Failed shop sync: transaction is rolled back for that shop, error is logged.
- The next sync run will re-process the failed shop (cursor not updated on failure).

---

## 6. Webhook Processing Flow

```
TikTok Platform           FastAPI Backend              Redis               Celery Worker          PostgreSQL
  |                            |                        |                      |                     |
  |  POST /webhooks/shop       |                        |                      |                     |
  |  Authorization: <sig>      |                        |                      |                     |
  |  Body: {type: 1,           |                        |                      |                     |
  |   event_id: "...",         |                        |                      |                     |
  |   data: {...}}             |                        |                      |                     |
  |--------------------------->|                        |                      |                     |
  |                            |                        |                      |                     |
  |                    +-------+--------+               |                      |                     |
  |                    | 1. VERIFY      |               |                      |                     |
  |                    |    SIGNATURE   |               |                      |                     |
  |                    |                |               |                      |                     |
  |                    | Shop:          |               |                      |                     |
  |                    |  HMAC-SHA256(  |               |                      |                     |
  |                    |    app_secret, |               |                      |                     |
  |                    |    app_key +   |               |                      |                     |
  |                    |    body)       |               |                      |                     |
  |                    |  == auth hdr   |               |                      |                     |
  |                    |                |               |                      |                     |
  |                    | Developer:     |               |                      |                     |
  |                    |  Parse t=TS,   |               |                      |                     |
  |                    |    s=SIG       |               |                      |                     |
  |                    |  HMAC-SHA256(  |               |                      |                     |
  |                    |    secret,     |               |                      |                     |
  |                    |    TS.body)    |               |                      |                     |
  |                    +-------+--------+               |                      |                     |
  |                            |                        |                      |                     |
  |                    +-------+--------+               |                      |                     |
  |                    | 2. DEDUPLICATE |               |                      |                     |
  |                    |                |               |                      |                     |
  |                    | SET            |               |                      |                     |
  |                    |  webhook:dedup:|               |                      |                     |
  |                    |  <key>         |               |                      |                     |
  |                    |  NX EX 86400   |               |                      |                     |
  |                    |--------------->|-------------->|                      |                     |
  |                    |                |<-------------|                      |                     |
  |                    | If NOT set:    |               |                      |                     |
  |                    |  return        |               |                      |                     |
  |                    |  "duplicate"   |               |                      |                     |
  |                    +-------+--------+               |                      |                     |
  |                            |                        |                      |                     |
  |                    +-------+--------+               |                      |                     |
  |                    | 3. STORE EVENT |               |                      |                     |
  |                    |                |               |                      |                     |
  |                    | INSERT INTO    |               |                      |                     |
  |                    |  webhook_events|               |                      |                     |
  |                    |  (platform,    |               |                      |                     |
  |                    |   event_type,  |               |                      |                     |
  |                    |   payload,     |               |                      |                     |
  |                    |   status=      |               |                      |                     |
  |                    |   RECEIVED)    |               |                      |                     |
  |                    |----------------|--------------------------------------------->|            |
  |                    |                |               |                      |       |            |
  |                    +-------+--------+               |                      |                     |
  |                            |                        |                      |                     |
  |                    +-------+--------+               |                      |                     |
  |                    | 4. ENQUEUE     |               |                      |                     |
  |                    |    CELERY TASK |               |                      |                     |
  |                    |                |               |                      |                     |
  |                    | process_webhook|               |                      |                     |
  |                    |   .delay(      |               |                      |                     |
  |                    |   event_id)    |               |                      |                     |
  |                    |--------------->|--- (broker)-->|--------------------->|                     |
  |                    +-------+--------+               |                      |                     |
  |                            |                        |                      |                     |
  |  {"status":"received",     |                        |                      |                     |
  |   "event_id": "..."}       |                        |                      |                     |
  |<---------------------------|                        |                      |                     |
  |                            |                        |                      |                     |
  |                            |                        |      (async)         |                     |
  |                            |                        |                      |                     |
  |                            |                        |  SELECT webhook_event WHERE id=event_id    |
  |                            |                        |                      |-------------------->|
  |                            |                        |                      |<--------------------|
  |                            |                        |                      |                     |
  |                            |                        |  UPDATE status =     |                     |
  |                            |                        |    PROCESSING        |                     |
  |                            |                        |                      |-------------------->|
  |                            |                        |                      |                     |
  |                            |                        |  _get_handler(       |                     |
  |                            |                        |    platform,         |                     |
  |                            |                        |    event_type)       |                     |
  |                            |                        |                      |                     |
  |                            |                        |  handler(payload,    |                     |
  |                            |                        |    session)          |                     |
  |                            |                        |                      |                     |
  |                            |                        |  e.g. handle_order_  |                     |
  |                            |                        |    status_change()   |                     |
  |                            |                        |                      |-------------------->|
  |                            |                        |                      |   UPDATE orders     |
  |                            |                        |                      |   SET status = X    |
  |                            |                        |                      |<--------------------|
  |                            |                        |                      |                     |
  |                            |                        |  UPDATE status =     |                     |
  |                            |                        |    PROCESSED         |                     |
  |                            |                        |                      |-------------------->|
```

### Webhook Signature Verification

| Platform   | Signature Location       | Algorithm                                         |
|------------|--------------------------|---------------------------------------------------|
| Shop       | `Authorization` header   | `HMAC-SHA256(app_secret, app_key + body)`         |
| Developer  | `TikTok-Signature` header | Parse `t=TS,s=SIG`; verify `HMAC-SHA256(secret, TS.body)` |
| Marketing  | Varies by subscription   | Verification varies per subscription config       |

### Commerce Webhook Handler Registry

| Event Type | Name                        | Handler Function                      |
|------------|-----------------------------|---------------------------------------|
| `1`        | Order Status Change         | `handle_order_status_change()`        |
| `3`        | Recipient Address Update    | `handle_recipient_address_update()`   |
| `4`        | Package Update              | `handle_package_update()`             |
| `5`        | Product Status Change       | `handle_product_status_change()`      |
| `11`       | Cancellation Status Change  | `handle_cancellation_status_change()` |
| `12`       | Return Status Change        | `handle_return_status_change()`       |
| `15`       | Product Information Change  | `handle_product_information_change()` |
| `16`       | Product Creation            | `handle_product_creation()`           |
| `27`       | Inventory Status Change     | `handle_inventory_status_change()`    |

### Webhook Status Lifecycle

```
RECEIVED --> PROCESSING --> PROCESSED
                |
                +--> FAILED (with error_message)
```

**Key files:**
- `backend/modules/webhooks/routes.py` -- `/webhooks/shop`, `/webhooks/developer`, `/webhooks/marketing` endpoints
- `backend/modules/webhooks/verification.py` -- `verify_shop_webhook()`, `verify_developer_webhook()`
- `backend/workers/webhook_processor.py` -- `process_webhook` Celery task, `_get_handler()` routing
- `backend/modules/commerce/webhook_handlers.py` -- All commerce webhook handlers and `COMMERCE_WEBHOOK_HANDLERS` registry
- `backend/db/models/webhook.py` -- WebhookEvent, WebhookStatus

**Error handling:**
- Invalid signature: 401 Unauthorized (webhook rejected).
- Duplicate event: Redis `SETNX` returns false, response is `{"status": "duplicate"}` (24h TTL on dedup key).
- Processing failure: event status set to `FAILED`, error_message stored, Celery retries 3 times with 30s delay.
- No handler registered: event is stored but not processed (logged as info).

**Polling fallback:** Webhooks are not the sole data source. Celery periodic tasks poll TikTok APIs every 15-30 minutes as a reconciliation mechanism, catching any missed webhooks.

---

## 7. Real-Time Events Flow

### WebSocket Connection + Redis Pub/Sub

```
Frontend (React)           FastAPI Backend              Redis Pub/Sub
  |                            |                            |
  |  WebSocket CONNECT         |                            |
  |  /api/commerce/ws/{wid}    |                            |
  |  ?token=<jwt>              |                            |
  |--------------------------->|                            |
  |                            |                            |
  |                            |  _validate_ws_token(jwt)   |
  |                            |  Decode JWT, verify type   |
  |                            |  == "access", extract      |
  |                            |  user_id                   |
  |                            |                            |
  |  (if invalid token)        |                            |
  |  Close 4001: Invalid token |                            |
  |<---------------------------|                            |
  |                            |                            |
  |  (if valid)                |                            |
  |  WebSocket ACCEPT          |                            |
  |<---------------------------|                            |
  |                            |                            |
  |                            |  SUBSCRIBE                 |
  |                            |  commerce:ws:{workspace_id}|
  |                            |--------------------------->|
  |                            |                            |
  |                            |     (listening loop)       |
  |                            |                            |
  |                            |                            |
  |       --- Meanwhile, a webhook is processed ---         |
  |                            |                            |
  |                            |  PUBLISH                   |
  |                            |  commerce:ws:{workspace_id}|
  |                            |  {"event":"order_update",  |
  |                            |   "data":{...}}            |
  |                            |                   <--------|
  |                            |<---------------------------|
  |                            |                            |
  |  WS TEXT MESSAGE           |                            |
  |  {"event":"order_update",  |                            |
  |   "data":{...}}            |                            |
  |<---------------------------|                            |
  |                            |                            |
  |  (React hook updates UI)   |                            |
  |                            |                            |
  |  --- Disconnect ---        |                            |
  |                            |  UNSUBSCRIBE               |
  |                            |  commerce:ws:{workspace_id}|
  |                            |--------------------------->|
```

**Step-by-step:**

1. Frontend connects via WebSocket to `/api/commerce/ws/{workspace_id}?token=<jwt>`.
2. JWT is validated using the same `decode_token()` function as REST endpoints.
3. If token is missing or invalid, connection is closed with code 4001.
4. On success, the backend subscribes to Redis channel `commerce:ws:{workspace_id}`.
5. An async loop polls for messages every 100ms (`asyncio.sleep(0.1)`).
6. When a webhook handler or sync worker publishes to the Redis channel, the message is forwarded to the WebSocket client.
7. On disconnect, the subscription is cleaned up.

**Channel naming convention:**
- Commerce events: `commerce:ws:{workspace_id}`
- Sync progress: `sync:ws:{workspace_id}` (used by `useSyncWebSocket` hook)

**Frontend hooks:**
- `useCommerceWebSocket` -- subscribes to commerce events (order updates, product changes)
- `useSyncWebSocket` -- subscribes to sync progress events

**Key files:**
- `backend/modules/commerce/routes/ws.py` -- WebSocket endpoint, Redis pub/sub subscription
- `backend/tiktok/rate_limiter.py` -- `get_redis()` shared Redis connection
- `frontend/src/hooks/` -- `useCommerceWebSocket`, `useSyncWebSocket`

**Error handling:**
- `WebSocketDisconnect`: caught and logged, subscription cleaned up.
- Any other exception: logged, subscription cleaned up in `finally` block.
- No reconnection logic on the backend (frontend handles reconnection).

---

## 8. SDK Sidecar Flow

The Node.js sidecar handles HMAC-SHA256 signing for TikTok Shop API requests, since the signing algorithm is complex and the official SDK is JavaScript-only.

### Request Flow

```
Python Backend             Node.js Sidecar (Fastify)         TikTok Shop API
  |                            |                                  |
  |  TikTokShopSDKClient      |                                  |
  |  .request("POST",         |                                  |
  |   "/product/202502/...")   |                                  |
  |                            |                                  |
  |  POST /api/shop/proxy     |                                  |
  |  x-sidecar-auth: <token>  |                                  |
  |  {                         |                                  |
  |    method: "POST",         |                                  |
  |    path: "/product/...",   |                                  |
  |    access_token: "tk_...", |                                  |
  |    shop_cipher: "sc_...",  |                                  |
  |    query_params: {...},    |                                  |
  |    body: {...}             |                                  |
  |  }                         |                                  |
  |--------------------------->|                                  |
  |                            |                                  |
  |                    +-------+--------+                         |
  |                    | 1. AUTH CHECK  |                         |
  |                    |                |                         |
  |                    | Verify         |                         |
  |                    | x-sidecar-auth |                         |
  |                    | matches env    |                         |
  |                    | SIDECAR_AUTH_  |                         |
  |                    |   TOKEN        |                         |
  |                    +-------+--------+                         |
  |                            |                                  |
  |                    +-------+--------+                         |
  |                    | 2. VALIDATE    |                         |
  |                    |                |                         |
  |                    | - access_token |                         |
  |                    |   required     |                         |
  |                    | - path matches |                         |
  |                    |   API pattern  |                         |
  |                    | - method in    |                         |
  |                    |   allowed set  |                         |
  |                    +-------+--------+                         |
  |                            |                                  |
  |                    +-------+--------+                         |
  |                    | 3. BUILD QUERY |                         |
  |                    |    PARAMS      |                         |
  |                    |                |                         |
  |                    | allParams = {  |                         |
  |                    |  app_key,      |                         |
  |                    |  timestamp,    |                         |
  |                    |  shop_cipher,  |                         |
  |                    |  ...query_     |                         |
  |                    |    params      |                         |
  |                    | }              |                         |
  |                    +-------+--------+                         |
  |                            |                                  |
  |                    +-------+--------+                         |
  |                    | 4. GENERATE    |                         |
  |                    |    HMAC-SHA256 |                         |
  |                    |    SIGNATURE   |                         |
  |                    |                |                         |
  |                    | signString =   |                         |
  |                    |  appSecret +   |                         |
  |                    |  path +        |                         |
  |                    |  sorted(params |                         |
  |                    |    excl sign,  |                         |
  |                    |    access_     |                         |
  |                    |    token) +    |                         |
  |                    |  body +        |                         |
  |                    |  appSecret     |                         |
  |                    |                |                         |
  |                    | sign = HMAC-   |                         |
  |                    |  SHA256(       |                         |
  |                    |  appSecret,    |                         |
  |                    |  signString)   |                         |
  |                    +-------+--------+                         |
  |                            |                                  |
  |                    +-------+--------+                         |
  |                    | 5. SEND TO     |                         |
  |                    |    TIKTOK      |                         |
  |                    |                |                         |
  |                    | GET/POST       |                         |
  |                    | https://open-  |                         |
  |                    | api.tiktok     |                         |
  |                    | globalshop.com |                         |
  |                    | /path?app_key= |                         |
  |                    | &timestamp=    |                         |
  |                    | &sign=         |                         |
  |                    | &access_token= |                         |
  |                    |                |                         |
  |                    | Headers:       |                         |
  |                    |  Content-Type: |                         |
  |                    |   application/ |                         |
  |                    |   json         |                         |
  |                    |  x-tts-access- |                         |
  |                    |   token: tk_.. |                         |
  |                    |                |                         |
  |                    |----------------|------------------------>|
  |                    |                |                         |
  |                    |                |  TikTok response        |
  |                    |                |<------------------------|
  |                    +-------+--------+                         |
  |                            |                                  |
  |  {                         |                                  |
  |    success: true,          |                                  |
  |    data: { TikTok resp },  |                                  |
  |    request_id: "uuid"      |                                  |
  |  }                         |                                  |
  |<---------------------------|                                  |
```

### HMAC-SHA256 Signing Algorithm

```
Input:
  path       = "/product/202502/products/search"
  params     = {app_key, timestamp, shop_cipher, ...}  (exclude "sign" and "access_token")
  body       = JSON string of request body
  appSecret  = "your_app_secret"

Steps:
  1. Sort param keys alphabetically
  2. Concatenate: key1 + value1 + key2 + value2 + ...
  3. Build signString: appSecret + path + sortedParams + body + appSecret
  4. sign = HMAC-SHA256(appSecret, signString).hex()

Result: appended as ?sign=<hex> in query string
```

### SDK Operation Discovery

The sidecar also exposes `GET /api/shop/operations` which lists all available SDK operations grouped by domain and version (e.g., `product/V202502`, `order/V202502`). This helps the backend know which operations are available.

**Key files:**
- `backend/tiktok/shop/sdk_client.py` -- `TikTokShopSDKClient`, proxy interface to sidecar
- `tiktok-shop-sdk/src/index.ts` -- Fastify server entry point (port 4000)
- `tiktok-shop-sdk/src/router.ts` -- `/api/shop/proxy` endpoint, signature generation, auth hook
- `tiktok-shop-sdk/src/sdk-registry.ts` -- Operation discovery

**Error types from sidecar:**

| Error Code              | HTTP Status | Meaning                                  |
|-------------------------|-------------|------------------------------------------|
| `SIDECAR_UNREACHABLE`   | (exception) | Sidecar is down or network failure       |
| `SIDECAR_INVALID_RESPONSE` | (exception) | Non-JSON response from sidecar        |
| `SIDECAR_AUTH_FAILED`   | 401         | `SIDECAR_AUTH_TOKEN` mismatch            |
| `MISSING_ACCESS_TOKEN`  | 400         | access_token not provided in request     |
| `MISSING_PATH`          | 400         | path not provided in request             |
| `INVALID_METHOD`        | 400         | Unsupported HTTP method                  |
| `INVALID_PATH`          | 400         | Path doesn't match API pattern           |
| `API_ERROR`             | varies      | TikTok Shop API returned an error        |
| `UPSTREAM_TIMEOUT`      | 502         | Request to TikTok timed out (30s)        |
| `UPSTREAM_ERROR`        | 502         | Network error reaching TikTok            |

**Security:**
- All sidecar endpoints (except `/health`) require `x-sidecar-auth` header matching `SIDECAR_AUTH_TOKEN` env var.
- The sidecar never stores tokens; they are passed per-request.
- Path validation regex: `/^\/[a-z_]+\/\d{6}\/[a-z0-9_/{}]+$/` prevents path traversal.
- Request timeout: 30 seconds.
- Body size limit: 1MB.

---

## Middleware Stack (Request Lifecycle)

Every HTTP request to the FastAPI backend passes through this middleware stack in order:

```
Incoming Request
       |
       v
+----------------------+
| CORS Middleware       |  Allow-Origin: settings.frontend_url
| (first executed)     |  Allow-Credentials: true
+----------------------+
       |
       v
+----------------------+
| Tenant Middleware     |  Extract X-Workspace-Id header
|                      |  Set request.state.workspace_id
+----------------------+
       |
       v
+----------------------+
| Request Logging      |  Generate X-Request-Id (8-char UUID)
| Middleware            |  Log: [req_id] METHOD /path -> STATUS (duration_ms)
|                      |  Add X-Request-Id response header
+----------------------+
       |
       v
+----------------------+
| FastAPI Router       |  Route matching, dependency injection
| + Dependencies       |  get_current_user() extracts JWT
|                      |  get_db() provides async DB session
+----------------------+
       |
       v
  Route Handler
```

**Note on middleware ordering:** In FastAPI/Starlette, the last middleware added is executed first. The order in `main.py` is:
1. `RequestLoggingMiddleware` (added last, executed first)
2. `TenantMiddleware` (added second)
3. `CORSMiddleware` (added first, executed last before router)

**Key files:**
- `backend/main.py` -- Middleware registration and router mounting
- `backend/middleware/tenant.py` -- `TenantMiddleware`
- `backend/middleware/logging_mw.py` -- `RequestLoggingMiddleware`
- `backend/dependencies.py` -- `get_current_user()`, `CurrentUser`, `DBSession`

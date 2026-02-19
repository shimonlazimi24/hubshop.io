# TikTok Developer - OAuth & Token Management

## OAuth 2.0 Authorization Code Flow

### Step 1: Authorization Request

```
GET https://www.tiktok.com/v2/auth/authorize/
```

**Required Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `client_key` | String | App identifier from developer portal |
| `scope` | String | Comma-separated scopes (e.g., `user.info.basic,video.list`) |
| `redirect_uri` | String | Pre-registered callback URL (HTTPS, max 512 chars, max 10 per app) |
| `state` | String | Anti-CSRF token (random alphanumeric string) |
| `response_type` | String | Always `code` |
| `disable_auto_auth` | Integer | `0` = skip auth for valid sessions; `1` = always show consent |

### Step 2: Authorization Response (redirect to callback)

| Parameter | Description |
|-----------|-------------|
| `code` | Authorization code for token exchange |
| `scopes` | Comma-separated granted permissions |
| `state` | Must match original CSRF token |
| `error` | Error indicator if user ineligible |
| `error_description` | Human-readable error message |

### Step 3: Exchange Code for Access Token

```
POST https://open.tiktokapis.com/v2/oauth/token/
Content-Type: application/x-www-form-urlencoded

client_key={client_key}&
client_secret={client_secret}&
code={authorization_code}&
grant_type=authorization_code&
redirect_uri={redirect_uri}
```

**PKCE**: Mobile/desktop apps must also provide `code_verifier`.

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| `open_id` | string | User's unique identifier |
| `access_token` | string | Valid for **24 hours** (86400 seconds) |
| `expires_in` | integer | Access token validity in seconds (86400) |
| `refresh_token` | string | Valid for **365 days** |
| `refresh_expires_in` | integer | Refresh token expiration in seconds |
| `scope` | string | Comma-separated authorized permissions |
| `token_type` | string | Always `"Bearer"` |

**Error Response:**

| Field | Description |
|-------|-------------|
| `error` | Error code |
| `error_description` | Human-readable error message |
| `log_id` | Unique request identifier for debugging |

### Step 4: Use Access Token

```
Authorization: Bearer {access_token}
```

## Token Refresh

```
POST https://open.tiktokapis.com/v2/oauth/token/
Content-Type: application/x-www-form-urlencoded

client_key={client_key}&
client_secret={client_secret}&
grant_type=refresh_token&
refresh_token={refresh_token}
```

**Important:** The returned refresh token may differ from the submitted one. Always replace the stored refresh token with the new one.

**Recommendation:** Proactive refresh via background job every 12 hours.

## Token Revocation

```
POST https://open.tiktokapis.com/v2/oauth/revoke/
Content-Type: application/x-www-form-urlencoded

client_key={client_key}&
client_secret={client_secret}&
token={access_token}
```

Removes the app from user's "Manage app permissions" settings. Returns empty response on success.

## Token Lifecycle Summary

| Token | Validity | Renewal |
|-------|----------|---------|
| Access Token | 24 hours (86400 seconds) | Via refresh token |
| Refresh Token | 365 days | New refresh token returned on each refresh |
| Authorization Code | Short-lived | Single use, exchange for tokens |

**Best practices:**
- Store and manage all tokens on the server side
- Schedule background jobs to proactively refresh tokens without requiring user consent
- Always replace stored refresh token with newly returned one

## Platform-Specific Authorization

| Platform | Authorization URL | Notes |
|----------|-------------------|-------|
| Web | `https://www.tiktok.com/v2/auth/authorize/` | Standard redirect flow |
| Desktop | `https://www.tiktok.com/v2/auth/authorize/` | Requires registered redirect URI |
| iOS | TikTok OpenSDK (native) | PKCE flow with `code_verifier` |
| Android | TikTok OpenSDK (native) | PKCE flow with `code_verifier` |
| Legacy Web | `https://www.tiktok.com/auth/authorize/` | **Deprecated** - migration recommended |

## Available Scopes

| Scope | Description |
|-------|-------------|
| `user.info.basic` | Basic user info (avatar, display name) |
| `user.info.profile` | Extended profile info |
| `video.list` | List user's videos |
| `video.publish` | Post content to TikTok |
| `video.upload` | Upload video files |

## Redirect URI Rules

- HTTPS required (no HTTP)
- Static URLs only (no query parameters or fragments)
- Max 512 characters
- Max 10 per app
- Must be pre-registered in developer portal

## Rate Limits (TikTok Developer API)

Uses a **one-minute sliding window**.

| Endpoint | Requests per Minute |
|----------|-------------------|
| `/v2/user/info/` | 600 |
| `/v2/video/query/` | 600 |
| `/v2/video/list/` | 600 |

Exceeded: HTTP 429 with `rate_limit_exceeded` error code.

Higher limits can be requested via TikTok Support Page.

## Security Requirements

- Secure storage of client secrets and refresh tokens
- CSRF protection through state token validation
- Proactive access token refresh management
- Bearer token in `Authorization` header

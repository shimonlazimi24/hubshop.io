# TikTok Shop - Complete Authorization Flow

## Overview

TikTok Shop uses OAuth-style authorization to grant third-party apps access to seller, creator, and partner data. The flow involves generating an authorization link, seller approval, and token exchange via the TikTok auth server.

## Auth Server

- **Base URL**: `https://auth.tiktok-shops.com`
- **US Authorization Domain**: `https://services.tiktokshops.us`
- **ROW Authorization Domain**: `https://services.tiktokshop.com`
- **Token Prefix**: All tokens are prefixed with `TTP_`

## Developer Onboarding

### Step 1: Create Partner Center Account

| Market | URL |
|--------|-----|
| US | `partner.us.tiktokshop.com/account/sign-up` |
| Non-US | `partner.tiktokshop.com/account/sign-up` |

### Step 2: Register as Developer

| Type | App Type | Data Access |
|------|----------|-------------|
| **Seller Developer** | Custom apps only | Own seller data only |
| **App Developer / ISV** | Public + custom apps | Any authorized seller's data |

Seller developers must use the same email for both their TikTok Shop account and developer account.

### Step 3: Compliance Review

Required for US and UK partners (3+ weeks). Contact:
- US: `partner.us@tiktokshop.com`
- UK: `partner.uk@tiktokshop.com`
- Other: `partner@tiktokshop.com`

### Step 4: Create an App

Produces credentials:
- `app_key` - unique app identifier
- `app_secret` - secret key for token requests
- `service_id` - used in authorization links

## Authorization Link

### Format

**US market:**
```
https://services.tiktokshops.us/open/authorize?service_id={service_id}&state={csrf_token}
```

**ROW:**
```
https://services.tiktokshop.com/open/authorize?service_id={service_id}&state={csrf_token}
```

The `state` parameter is recommended for CSRF protection.

## Authorization Pathways

### Pathway A: Via Authorization Link (Custom or Public Apps)

1. Developer shares authorization link with seller
2. Seller opens link, logs in, fills required info
3. Seller approves authorization
4. Redirect to app's URL with `auth_code`:

```
{redirect_url}?code=FeBoANmHP3yqdoUI9fZOCw&state={state}
```

If rejected:
```
{redirect_url}?code=null&error=auth_denied
```

### Pathway B: Via Seller Center App Store (Public Apps Only)

1. Seller navigates to **Seller Center > Growth > App Store**
2. Finds and installs the app
3. Authorizes and is redirected with `auth_code`

**Note:** App Store pathway does NOT pass `state` parameter.

## Token Exchange

### Get Access Token

```
GET https://auth.tiktok-shops.com/api/v2/token/get
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `app_key` | Yes | App key from Partner Center |
| `app_secret` | Yes | App secret from Partner Center |
| `auth_code` | Yes | Authorization code (30min expiry, one-time use) |
| `grant_type` | Yes | Must be `authorized_code` |

**Response:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "TTP_Fw8rBwAAAAA...",
    "access_token_expire_in": 1660556783,
    "refresh_token": "TTP_NTUxZTNhYTQ...",
    "refresh_token_expire_in": 1691487031,
    "open_id": "7010736057180325637",
    "seller_name": "Test shop",
    "seller_base_region": "US",
    "user_type": 0,
    "granted_scopes": ["seller.affiliate_collaboration.read"]
  }
}
```

### Refresh Token

```
GET https://auth.tiktok-shops.com/api/v2/token/refresh
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `app_key` | Yes | App key |
| `app_secret` | Yes | App secret |
| `refresh_token` | Yes | Current refresh token |
| `grant_type` | Yes | Must be `refresh_token` |

Returns same structure as Get Access Token. **Always replace stored refresh token with newly returned one.**

## Token Lifecycle

| Token | Expiry | Notes |
|-------|--------|-------|
| `auth_code` | 30 minutes | One-time use only |
| `access_token` | 7 days | Passed in `x-tts-access-token` header |
| `refresh_token` | Seller's authorization duration | When expired, seller must re-authorize |

**All token endpoints use HTTP GET** (not POST).

## User Types

| Value | Type |
|-------|------|
| `0` | Seller |
| `1` | Creator |
| `3` | Partner |

## API Entity Tags

Each API endpoint is tagged with an entity type determining required tokens and identifiers:

| Entity Tag | Token Required | Additional Identifier | Use Case |
|-----------|----------------|----------------------|----------|
| **Seller** | Seller access token | None | Cross-shop operations, global products |
| **Shop** | Seller access token | `shop_cipher` | Shop-specific: orders, fulfillment, local products |
| **Account** | Partner access token | None | Partner's authorized category assets |
| **Creator** | Creator access token | None | Creator profile, affiliates |
| **Asset** | Partner access token | `category_asset_cipher` | Affiliate campaigns |

## Get Authorized Shops API

Required to obtain `shop_cipher` for Shop-tagged endpoints.

```
GET /authorization/202309/shops
```

**Headers:** `x-tts-access-token: {seller_access_token}`

**Response:**

```json
{
  "code": 0,
  "data": {
    "shops": [
      {
        "id": "7000714532876273420",
        "name": "Beauty shop",
        "region": "GB",
        "seller_type": "CROSS_BORDER",
        "cipher": "GCP_XF90igAAAABh00qsWgtvOiGFNqyubMt3",
        "code": "CNGBCBA4LLU8"
      }
    ]
  }
}
```

The `cipher` field is the `shop_cipher` passed to Shop-tagged endpoints.

## Authorization Renewal & Cancellation

- **30 days before expiry**: Type 7 webhook ("Upcoming Authorization Expiration") fires
- **Renewal**: Seller revisits auth link or uses Seller Center > App Store > My apps
- **Cancellation**: Seller uses Seller Center > App Store > My apps; triggers Type 6 webhook ("Seller Deauthorization")

## OAuth Flow Diagram

```
Developer                    Seller                    TikTok Auth Server
   |                           |                              |
   |-- Auth link (service_id)->|                              |
   |                           |-- Opens link, logs in ------>|
   |                           |<-- Auth form ----------------|
   |                           |-- Approves ----------------->|
   |<-- Redirect ?code=xxx ----|<-- Redirect with auth_code --|
   |                                                          |
   |-- GET /api/v2/token/get (app_key, secret, code) ------->|
   |<-- access_token + refresh_token -------------------------|
   |                                                          |
   |-- API calls with x-tts-access-token header              |
   |                                                          |
   |-- GET /api/v2/token/refresh (before 7-day expiry) ----->|
   |<-- New access_token + refresh_token ---------------------|
```

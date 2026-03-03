# TikTok Shop SDK Sidecar — Production Design

**Date:** 2026-03-02
**Status:** Approved
**Approach:** Generic Passthrough Proxy (Approach A)

## Context

The official TikTok Shop API SDK is a Node.js/TypeScript package with:
- 1,624 files, 202 API methods across 18 domains
- OpenAPI-generated typed models
- Built-in HMAC-SHA256 signing, serialization, token management

Frodo's backend is Python/FastAPI. The existing `TikTokShopClient` covers ~40 endpoints with hand-written HMAC signing. This design replaces it with the official SDK running as a Docker Compose sidecar.

## Architecture

```
Docker Compose Network (frodo)

  Python API (:8000)  ──httpx──>  tiktok-shop-sdk (:3000)  ──>  TikTok API
  Celery Workers      ──httpx──>  (Node/Fastify, internal)       (HMAC signed)

  Postgres (:5432)    Redis (:6379)
```

- Sidecar runs Fastify on port 3000, internal network only
- Single dynamic route resolves any SDK operation at runtime
- Stateless — credentials per-request, app_key/app_secret via env vars
- Python side gets a new `TikTokShopSDKClient` that integrates with existing `PlatformGateway`

## API Contract

### Endpoint

```
POST /api/shop/:domain/:version/:operation
```

### Example

```
POST /api/shop/product/V202502/ProductsSearchPost
```

### Request Body

```json
{
  "access_token": "ROW_xxx...",
  "shop_cipher": "TTP_xxx...",
  "params": {
    "pageSize": 50,
    "contentType": "application/json"
  },
  "body": {
    "status": "LIVE"
  }
}
```

### Success Response

```json
{
  "success": true,
  "data": { "...raw SDK response..." },
  "request_id": "uuid"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "INVALID_OPERATION",
    "message": "Operation 'FooBar' not found on ProductV202502Api",
    "details": {}
  },
  "request_id": "uuid"
}
```

### Discovery

```
GET /api/shop/operations
```

Returns all available domain/version/operation combinations.

### Health

```
GET /health
```

## SDK Domains (18 total, 202 operations)

| Domain | Versions | Operations | Models |
|--------|----------|------------|--------|
| Product | 15 versions (202309–202601) | 33+ | 704 |
| Analytics | 7 versions (202405–202512) | 11+ | 221 |
| Fulfillment | 7 versions (202309–202601) | 22+ | 135 |
| Promotion | 2 versions | 7+ | 90 |
| FBT | 4 versions | 5+ | 73 |
| Order | 5 versions | 3+ | 67 |
| Return/Refund | 3 versions | 12+ | 65 |
| Finance | 3 versions | 5+ | 49 |
| Customer Service | 3 versions | 8+ | 30 |
| Logistics | 2 versions | 4+ | 26 |
| Data Reconciliation | 3 versions | — | 24 |
| Customer Engagement | 2 versions | 4+ | 24 |
| Authorization | 4 versions | — | 10 |
| Supply Chain | 1 version | — | 9 |
| Event | 1 version | 3+ | 7 |
| Seller | 1 version | — | 5 |
| Open | 1 version | — | 3 |

## File Structure

```
tiktok-shop-sdk/                    # New top-level directory
├── Dockerfile                      # Node 20 Alpine
├── package.json                    # fastify, typescript, SDK deps
├── tsconfig.json
├── src/
│   ├── index.ts                    # Fastify server entry
│   ├── router.ts                   # Dynamic operation resolver
│   ├── sdk-registry.ts             # Maps domain+version → SDK API class
│   └── health.ts                   # Health check
└── sdk/                            # Official SDK (dropped in)
    ├── api/
    ├── client/
    ├── model/
    └── utils/

backend/tiktok/shop/
├── sdk_client.py                   # NEW — httpx wrapper to sidecar
├── client.py                       # EXISTING — kept until migration done
```

## Docker Compose

```yaml
tiktok-shop-sdk:
  build: ./tiktok-shop-sdk
  env_file: .env
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
    interval: 15s
    timeout: 5s
    retries: 3
```

No ports exposed externally. Only reachable within Docker network.

## Environment Variables

```
TIKTOK_SHOP_SDK_URL=http://tiktok-shop-sdk:3000
```

App credentials (already in .env):
```
TIKTOK_SHOP_APP_KEY=...
TIKTOK_SHOP_APP_SECRET=...
```

## Migration Plan

1. Build sidecar, verify with live credentials
2. Add `TikTokShopSDKClient` alongside existing `TikTokShopClient`
3. Wire one service (product sync) to SDK client, verify parity
4. Migrate remaining services one by one
5. Remove old `TikTokShopClient` when complete

## What Stays The Same

- `PlatformGateway` — circuit breaker + rate limiter + retry
- `TokenVault` — encrypted token storage in Postgres
- All existing service interfaces
- Docker Compose workflow (`docker compose up`)

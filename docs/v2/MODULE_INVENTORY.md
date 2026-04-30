# Frodo v2 — Module inventory & scope

This document maps the **legacy Python/FastAPI** surface to **v2 packages** and records **defer / kill** decisions for migration planning.

## Backend route inventory (FastAPI)

| Prefix / area | Legacy module | v2 home | Phase |
|----------------|---------------|---------|-------|
| `/api/auth` | [backend/auth/routes.py](../../backend/auth/routes.py) | `apps/api` → `AuthModule` | 3–4 |
| `/api/connect`, OAuth | `backend/modules/connect` | `ConnectModule` (OAuth + token vault) | 4 |
| `/api` sync, WS | `connect/sync_routes`, `connect/ws` | `JobsModule` + `RealtimeModule` | 5–7 |
| `/api/commerce` | `backend/modules/commerce` | `CommerceModule` | 6 |
| `/api` advertising | `backend/modules/advertising` | `AdvertisingModule` | 8 |
| `/api/content` | `backend/modules/content` | `ContentModule` | 8 |
| `/api/creators` | `backend/modules/creators` | `CreatorsModule` | 8 |
| `/api/customer_engagement` | `backend/modules/customer_engagement` | `EngagementModule` | 8 |
| `/api/gmvmax` | `backend/modules/gmvmax` | `GmvmaxModule` | 8 |
| `/api/intelligence` | `backend/modules/intelligence` | `IntelligenceModule` | 8 |
| `/api/live` | `backend/modules/live` | `LiveModule` | 8 |
| `/api/messaging` | `backend/modules/messaging` | `MessagingModule` | 8 |
| `/api/organic` | `backend/modules/organic` | `OrganicModule` | 8 |
| `/api/analytics` | `backend/modules/analytics` | `AnalyticsModule` | 8 |
| Webhooks | [backend/modules/webhooks](../../backend/modules/webhooks) | `WebhooksModule` | 5 |
| TikTok gateway | [backend/tiktok](../../backend/tiktok) | `packages/domain` (clients + middleware) | 4–6 |

## Celery workers inventory

| Task group | Legacy file | v2 job type (SQS envelope) | Phase |
|------------|-------------|------------------------------|-------|
| Token refresh | `workers/token_refresh` | `token_refresh_tick`, `refresh_workspace_tokens` | 4 |
| Data / shop sync | `workers/data_sync` | `sync_shop_orders`, `sync_shop_products` | 6 |
| Ads sync | `workers/ad_sync` | `sync_ad_*` | 8 |
| Content | `workers/content_sync` | `sync_*_videos` | 8 |
| Webhooks | `workers/webhook_processor` | `process_webhook_event` | 5 |
| Analytics | `workers/analytics_sync` | `analytics_rollups` | 8 |
| Other domains | `creator_sync`, `intelligence_sync`, … | Per-module jobs | 8 |

## Kill list / redesign (explicit)

| Item | Action | Rationale |
|------|--------|-----------|
| Celery + Redis as broker | **Remove** | Replaced by SQS + worker |
| Celery Beat schedules | **Replace** | Scheduler service enqueues SQS messages |
| Next.js App Router app | **Replace** | Vite SPA per ADR-001 |
| Standalone `tiktok-shop-sdk` sidecar (v2 path) | **Merge** | Signing in `@frodo/domain`; legacy sidecar until cutover |
| Mock-only TikTok tests as gate | **Discard** | Replace with contract tests + sandbox recordings |
| 1500-line monolithic `api.ts` | **Redesign** | Generated or modular clients from `@frodo/contracts` |

## Keep (concepts & constraints)

- Organization → Workspace → Membership hierarchy
- Tenant-scoped tables keyed by `workspace_id`
- JWT access + refresh; RBAC roles (`owner` … `viewer`)
- AES-GCM or equivalent for TikTok tokens at rest
- Webhook persistence + idempotency keys + async processing
- Gateway ordering: rate limit → circuit breaker → retry for TikTok HTTP

## Parity checkpoints

Per phase acceptance uses **staging DB clones**, **sample workspaces**, and **TikTok sandbox credentials** where applicable—see phase checklist in the migration plan.

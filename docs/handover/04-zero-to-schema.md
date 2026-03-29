# 04 -- Zero to Schema

> For each domain, start from the business problem (zero/nothing), walk through the data flow, and arrive at the database schema.

---

## Table of Contents

1. [Global Patterns](#global-patterns)
2. [Overall Entity Relationship Overview](#overall-entity-relationship-overview)
3. [Domain 1 -- Auth & Multi-Tenancy](#domain-1----auth--multi-tenancy)
4. [Domain 2 -- Token Vault & Platform Connections](#domain-2----token-vault--platform-connections)
5. [Domain 3 -- Commerce / Shop](#domain-3----commerce--shop)
6. [Domain 4 -- Finance](#domain-4----finance)
7. [Domain 5 -- Affiliate](#domain-5----affiliate)
8. [Domain 6 -- Advertising / Marketing](#domain-6----advertising--marketing)
9. [Domain 7 -- Content](#domain-7----content)
10. [Domain 8 -- Creators](#domain-8----creators)
11. [Domain 9 -- Analytics & Notifications](#domain-9----analytics--notifications)
12. [Domain 10 -- Messaging](#domain-10----messaging)
13. [Domain 11 -- LIVE](#domain-11----live)
14. [Domain 12 -- Intelligence](#domain-12----intelligence)
15. [Domain 13 -- Organic Monitoring](#domain-13----organic-monitoring)
16. [Domain 14 -- Webhooks](#domain-14----webhooks)
17. [Domain 15 -- Data Sync](#domain-15----data-sync)

---

## Global Patterns

Before diving into domains, understand the patterns that apply to every table.

### Base Mixins (backend/db/models/base.py)

Every model inherits from two mixins:

```
UUIDMixin
  id: UUID  (primary key, auto-generated uuid4)

TimestampMixin
  created_at: TIMESTAMPTZ  (server_default=now(), NOT NULL)
  updated_at: TIMESTAMPTZ  (server_default=now(), onupdate=now(), NOT NULL)
```

One exception: `LiveEvent` skips `TimestampMixin` because it has its own `timestamp` column.

### Multi-Tenant Isolation

Every tenant-scoped table carries a `workspace_id` UUID foreign key to `workspaces(id)` with `ON DELETE CASCADE`. The hierarchy is:

```
Organization  (agency-level account)
  └── Workspace  (brand or sub-account within the agency)
       └── All domain data (orders, campaigns, videos, etc.)
```

PostgreSQL Row-Level Security (RLS) uses `workspace_id` to guarantee tenant isolation. Every query on tenant-scoped data MUST filter by `workspace_id`.

### JSONB Columns

Several tables include `detail_json`, `metadata_json`, or similar JSONB columns. These store the full TikTok API response snapshot for debugging and forward compatibility. They are NOT the source of truth for structured fields -- those are extracted into dedicated columns.

### Money as Strings

All monetary amounts (`total_amount`, `price_amount`, `budget`, `commission_rate`) are stored as `String(20)` rather than DECIMAL. This avoids floating-point precision issues in Python and JavaScript while keeping exact representation. Parse to `Decimal` in business logic.

### Platform IDs

Every synced entity stores its TikTok platform identifier (e.g., `platform_order_id`, `tiktok_shop_id`, `platform_campaign_id`) as a unique string column. This is the join key for upserts during sync operations.

---

## Overall Entity Relationship Overview

```
                    +------------------+
                    |  organizations   |
                    +--------+---------+
                             |
                    +--------v---------+
                    |    workspaces    |
                    +--------+---------+
                             |
         +-------------------+-------------------+
         |                   |                   |
+--------v------+  +---------v--------+  +-------v--------+
|   users       |  | connected_accounts|  |  (all domain   |
|               |  | (Shop/Dev/Mkt/   |  |   tables have  |
|   social_     |  |  Live/Research)  |  |   workspace_id)|
|   identities  |  +--------+---------+  +----------------+
|               |           |
|  memberships  |  +--------v---------+
+---------------+  |   token_vault    |
                   +------------------+

DOMAIN DATA (all scoped to workspace_id):

Commerce:       shops -> products -> product_skus
                shops -> orders -> order_line_items, packages, order_status_events
                shops -> promotions
                orders -> return_requests

Finance:        shops -> settlements, transactions, payments

Affiliate:      shops -> affiliate_products, open_collaborations,
                         target_collaborations, creator_applications

Advertising:    ad_accounts -> campaigns -> ad_groups -> ads
                ad_accounts -> audiences, pixels, catalogs, report_cache
                ad_accounts -> ad_sync_cursors

Content:        videos -> video_metrics, comments
                content_publish_jobs
                content_sync_cursors

Creators:       creator_profiles -> creator_invitations <- creator_campaigns
                creator_profiles -> content_authorizations

Analytics:      unified_kpi_snapshots, scheduled_reports
                notifications, notification_preferences, api_keys

Messaging:      conversations -> messages
                auto_messages

LIVE:           live_sessions -> live_events
                live_sessions -> live_analytics

Intelligence:   trend_snapshots
                competitor_trackers -> competitor_content
                research_queries

Organic:        brand_mentions, mention_keywords, organic_comments

Webhooks:       webhook_events (cross-cutting)

Sync:           sync_jobs (cross-cutting)
                sync_cursors (commerce), ad_sync_cursors (ads),
                content_sync_cursors (content)
```

---

## Domain 1 -- Auth & Multi-Tenancy

### The Problem (Zero)

An agency has multiple team members who need different access levels. The agency manages multiple brands, each needing isolated data. There is no TikTok concept of "agency workspace" -- Frodo must build this hierarchy from scratch. Users should be able to sign up with email/password or use TikTok/Google social login.

### The Process

1. **Registration**: User submits email + password + organization name. Frodo creates a `User`, an `Organization`, a default `Workspace`, and a `Membership` (role=OWNER) in a single transaction.
2. **Social login**: User clicks "Login with TikTok" or "Login with Google". The OAuth flow creates a `SocialIdentity` linked to a `User`. If the social identity already exists, it resolves to the existing user.
3. **Authentication**: Login returns a JWT access token (15 min, HS256) containing `user_id`, `organization_id`, and `role`. A refresh token (7 days) enables silent renewal.
4. **Authorization**: The 5-tier RBAC hierarchy (owner > admin > manager > member > viewer) is checked on every protected endpoint via `CurrentUser` dependency.
5. **Workspace switching**: A user may belong to multiple workspaces. The `workspace_id` is passed as a query parameter or header, validated against the user's memberships.

### The Schema

**Table: `users`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default uuid4 |
| email | VARCHAR(255) | UNIQUE, NOT NULL, indexed |
| hashed_password | VARCHAR(255) | NULLABLE (null for social-only users) |
| full_name | VARCHAR(255) | NOT NULL |
| is_active | BOOLEAN | default true |
| is_superuser | BOOLEAN | default false |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

**Table: `organizations`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(255) | NOT NULL |
| slug | VARCHAR(255) | UNIQUE, indexed, NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

**Table: `workspaces`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(255) | NOT NULL |
| slug | VARCHAR(255) | NOT NULL |
| organization_id | UUID | FK -> organizations(id) CASCADE, indexed |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

Unique constraint: `(organization_id, slug)`

**Table: `memberships`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK -> users(id) CASCADE, NOT NULL |
| organization_id | UUID | FK -> organizations(id) CASCADE, NOT NULL |
| workspace_id | UUID | FK -> workspaces(id) CASCADE, NULLABLE |
| role | ENUM(owner,admin,manager,member,viewer) | NOT NULL, default 'member' |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

Unique constraint: `(user_id, organization_id, workspace_id)`

**Table: `social_identities`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK -> users(id) CASCADE, NOT NULL, indexed |
| provider | VARCHAR(50) | NOT NULL (tiktok, google) |
| provider_user_id | VARCHAR(255) | NOT NULL |
| email | VARCHAR(255) | NULLABLE |
| display_name | VARCHAR(255) | NULLABLE |
| avatar_url | VARCHAR(1024) | NULLABLE |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

Unique constraint: `(provider, provider_user_id)`

```
ER Diagram:

  organizations ----< workspaces
       |
       |         users ----< social_identities
       |           |
       +-----< memberships >----- workspaces
```

### The API Surface

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create user + org + workspace + membership |
| POST | `/auth/login` | Email/password login, returns JWT pair |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/auth/me` | Get current user profile |
| GET | `/auth/tiktok/login` | Get TikTok OAuth URL |
| GET | `/auth/tiktok/callback` | TikTok OAuth callback |
| GET | `/auth/google/login` | Get Google OAuth URL |
| GET | `/auth/google/callback` | Google OAuth callback |

---

## Domain 2 -- Token Vault & Platform Connections

### The Problem (Zero)

TikTok has 4+ separate platforms (Shop, Developer, Marketing, LIVE, Research), each with its own OAuth flow, token format, and signing mechanism. An agency needs to connect multiple accounts across these platforms. Tokens must be stored securely and refreshed on different schedules. Accounts across platforms may belong to the same TikTok identity but there is no cross-platform API to link them.

### The Process

1. **Connect**: User selects a platform (Shop, Developer, or Marketing) and clicks "Connect." Frodo redirects to the platform-specific OAuth URL.
2. **Callback**: TikTok redirects back with an auth code. Frodo exchanges it for access + refresh tokens via the platform-specific token endpoint.
3. **Encrypt & store**: Tokens are encrypted with AES-256-GCM and stored in `token_vault`. The `connected_account` row stores platform metadata (seller IDs, shop ciphers, advertiser IDs, scopes).
4. **Auto-refresh**: Celery Beat runs token refresh tasks on schedule: Shop every 24h, Developer every 12h, Marketing daily health check.
5. **Failure handling**: After 3 failed refresh attempts, the account status is set to `error` and the user is notified.
6. **Identity linking**: Users manually assign an `identity_group_id` UUID to connected accounts that belong to the same TikTok identity.

### The Schema

**Table: `connected_accounts`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK -> workspaces(id) CASCADE, indexed |
| platform | ENUM(shop,developer,marketing,live,research) | NOT NULL |
| platform_account_id | VARCHAR(255) | NOT NULL |
| platform_account_name | VARCHAR(255) | NULLABLE |
| status | ENUM(active,error,disconnected,refreshing) | NOT NULL, default 'active' |
| identity_group_id | UUID | NULLABLE, indexed |
| metadata_json | JSONB | NULLABLE |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

**Table: `token_vault`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| connected_account_id | UUID | FK -> connected_accounts(id) CASCADE, UNIQUE |
| encrypted_access_token | TEXT | NOT NULL |
| encrypted_refresh_token | TEXT | NULLABLE |
| access_token_expires_at | VARCHAR(50) | NULLABLE |
| refresh_token_expires_at | VARCHAR(50) | NULLABLE |
| scopes | TEXT | NULLABLE |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

One-to-one relationship: each connected account has exactly one token vault entry.

**Table: `platform_app_credentials`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| platform | ENUM(...) | UNIQUE, NOT NULL |
| app_id | VARCHAR(255) | NOT NULL |
| encrypted_app_secret | TEXT | NOT NULL |
| redirect_uri | VARCHAR(512) | NOT NULL |
| extra_config | JSONB | NULLABLE |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

```
ER Diagram:

  workspaces ----< connected_accounts ----1 token_vault
                         |
                   platform_app_credentials (singleton per platform)
```

### The API Surface

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/connect/shop/authorize` | Get Shop OAuth URL |
| GET | `/connect/shop/callback` | Shop OAuth callback |
| GET | `/connect/developer/authorize` | Get Developer OAuth URL |
| GET | `/connect/developer/callback` | Developer OAuth callback |
| GET | `/connect/marketing/authorize` | Get Marketing OAuth URL |
| GET | `/connect/marketing/callback` | Marketing OAuth callback |
| GET | `/connect/accounts` | List all connected accounts for workspace |

---

## Domain 3 -- Commerce / Shop

### The Problem (Zero)

Agencies sell products on TikTok Shop. They need to see all their shops, manage product catalogs, track orders from placement through fulfillment and delivery, handle returns/refunds, and run promotions. TikTok Shop data must be synced from the Shop API and kept up to date via webhooks + polling.

### The Process

1. **Shop discovery**: After connecting a Shop account, Frodo calls the Shop API to list all authorized shops and creates `shops` rows for each `shop_cipher`.
2. **Product sync**: A Celery task fetches products for each shop. Products are upserted by `platform_product_id`. SKU variants are stored separately in `product_skus`.
3. **Order sync**: Orders are fetched periodically and on webhook events. Each order has line items, packages (for fulfillment tracking), and status events (audit trail of state changes).
4. **Fulfillment**: When a seller ships an order, the API creates a `Package` with tracking info and the order transitions to `IN_TRANSIT`.
5. **Returns**: Buyer-initiated returns create `ReturnRequest` rows linked to the original order. Status flows through PENDING -> APPROVED -> BUYER_SHIPPED -> SELLER_RECEIVED -> REFUNDED.
6. **Promotions**: Discount/flash sale/free shipping promotions are synced from the Shop API with time windows and discount configuration.
7. **Sync cursors**: `sync_cursors` track the last successful sync position for incremental fetches.

### The Schema

**Table: `shops`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK -> workspaces(id) CASCADE, indexed |
| connected_account_id | UUID | FK -> connected_accounts(id) CASCADE |
| shop_id | VARCHAR(255) | UNIQUE, NOT NULL |
| shop_cipher | VARCHAR(255) | NOT NULL |
| shop_name | VARCHAR(255) | NOT NULL |
| region | VARCHAR(10) | NOT NULL |
| last_product_sync_at | TIMESTAMPTZ | NULLABLE |
| last_order_sync_at | TIMESTAMPTZ | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

**Table: `products`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| shop_id | UUID | FK -> shops(id) CASCADE, indexed |
| platform_product_id | VARCHAR(255) | UNIQUE |
| title | VARCHAR(500) | NOT NULL |
| status | ENUM(draft,pending,live,seller_deactivated,...) | NOT NULL |
| main_image_url | TEXT | NULLABLE |
| price_amount | VARCHAR(20) | NULLABLE |
| currency | VARCHAR(3) | NULLABLE |
| inventory_total | INT | default 0 |
| sku_count | INT | default 0 |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(workspace_id, status)`

**Table: `product_skus`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| product_id | UUID | FK -> products(id) CASCADE, indexed |
| platform_sku_id | VARCHAR(255) | UNIQUE |
| seller_sku | VARCHAR(255) | NULLABLE |
| price_amount | VARCHAR(20) | NULLABLE |
| inventory_quantity | INT | default 0 |
| sku_name | VARCHAR(500) | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

**Table: `orders`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| shop_id | UUID | FK -> shops(id) CASCADE, indexed |
| platform_order_id | VARCHAR(255) | UNIQUE |
| status | ENUM(unpaid,on_hold,awaiting_shipment,...,cancelled) | NOT NULL |
| total_amount | VARCHAR(20) | NOT NULL |
| currency | VARCHAR(3) | default 'USD' |
| item_count | INT | default 0 |
| fulfillment_type | VARCHAR(50) | NULLABLE |
| rts_sla | TIMESTAMPTZ | NULLABLE |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Indexes: `(workspace_id, status)`, `(workspace_id, created_at)`

**Table: `order_line_items`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| order_id | UUID | FK -> orders(id) CASCADE, indexed |
| platform_sku_id | VARCHAR(255) | NULLABLE |
| product_name | VARCHAR(500) | NOT NULL |
| quantity | INT | default 1 |
| unit_price | VARCHAR(20) | NOT NULL |
| total_price | VARCHAR(20) | NOT NULL |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

**Table: `packages`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| order_id | UUID | FK -> orders(id) CASCADE, indexed |
| platform_package_id | VARCHAR(255) | UNIQUE |
| status | ENUM(pending,processing,shipped,...,failed) | NOT NULL |
| tracking_number | VARCHAR(255) | NULLABLE |
| shipping_provider | VARCHAR(255) | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

**Table: `order_status_events`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| order_id | UUID | FK -> orders(id) CASCADE, indexed |
| from_status | VARCHAR(50) | NULLABLE |
| to_status | VARCHAR(50) | NOT NULL |
| source | VARCHAR(20) | NOT NULL (webhook, sync, api) |
| occurred_at | TIMESTAMPTZ | NOT NULL |

Note: Uses `UUIDMixin` only (no `TimestampMixin`).

**Table: `return_requests`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| order_id | UUID | FK -> orders(id) CASCADE, indexed |
| platform_return_id | VARCHAR(255) | UNIQUE |
| return_type | ENUM(return_and_refund, refund_only) | NOT NULL |
| status | ENUM(pending,...,closed) | NOT NULL |
| reason | TEXT | NULLABLE |
| refund_amount | VARCHAR(20) | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

**Table: `promotions`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| shop_id | UUID | FK -> shops(id) CASCADE, indexed |
| platform_activity_id | VARCHAR(255) | UNIQUE |
| promotion_type | VARCHAR(100) | NOT NULL |
| title | VARCHAR(500) | NOT NULL |
| status | VARCHAR(50) | default 'ACTIVE' |
| start_time / end_time | TIMESTAMPTZ | NULLABLE |
| discount_type | VARCHAR(50) | NULLABLE |
| discount_value | VARCHAR(20) | NULLABLE |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(workspace_id, status)`

**Table: `sync_cursors`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| shop_id | UUID | FK -> shops(id) CASCADE |
| sync_type | VARCHAR(50) | NOT NULL (products, orders) |
| cursor_value | VARCHAR(255) | NULLABLE |
| last_sync_at | TIMESTAMPTZ | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Unique index: `(shop_id, sync_type)`

```
ER Diagram:

  shops ----< products ----< product_skus
    |
    +----< orders ----< order_line_items
    |        |
    |        +----< packages
    |        +----< order_status_events
    |        +----< return_requests
    |
    +----< promotions
    +----< sync_cursors
```

### The API Surface

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/commerce/shops` | List shops for workspace |
| GET | `/commerce/shops/{id}` | Get shop details |
| GET | `/commerce/products` | List products with filtering |
| GET | `/commerce/products/{id}` | Get product detail + SKUs |
| GET | `/commerce/orders` | List orders with filtering/pagination |
| GET | `/commerce/orders/{id}` | Get order detail + line items + packages |
| POST | `/commerce/fulfillment/...` | Ship orders, create packages |
| GET | `/commerce/returns` | List return requests |
| POST | `/commerce/returns/{id}/approve` | Approve a return |
| GET | `/commerce/promotions` | List promotions |
| GET | `/commerce/analytics/...` | Commerce KPIs |
| GET | `/commerce/finance/...` | Settlement and transaction data |
| WS | `/commerce/ws` | Real-time order updates via WebSocket |

---

## Domain 4 -- Finance

### The Problem (Zero)

Agencies need visibility into their TikTok Shop financial data: how much money came in, what commissions were charged, when settlements were processed, and individual transaction-level records. Without this, reconciling payments across multiple shops is manual and error-prone.

### The Process

1. **Settlement sync**: Celery tasks fetch settlement records from the Shop Finance API. Each settlement covers a time period and shows the net amount paid out.
2. **Transaction sync**: Individual transactions (order payments, refunds, commissions) are synced and linked to their settlement.
3. **Payment tracking**: Payment records track the actual disbursement to the seller's bank account.

### The Schema

**Table: `settlements`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| shop_id | UUID | FK -> shops(id) CASCADE, indexed |
| platform_settlement_id | VARCHAR(255) | UNIQUE |
| amount | VARCHAR(20) | NOT NULL |
| currency | VARCHAR(10) | NOT NULL |
| status | VARCHAR(50) | NOT NULL |
| period_start / period_end | TIMESTAMPTZ | NULLABLE |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(workspace_id, status)`

**Table: `transactions`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| shop_id | UUID | FK -> shops(id) CASCADE, indexed |
| platform_transaction_id | VARCHAR(255) | UNIQUE |
| transaction_type | VARCHAR(100) | NOT NULL |
| amount | VARCHAR(20) | NOT NULL |
| currency | VARCHAR(10) | NOT NULL |
| order_id | VARCHAR(255) | NULLABLE |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

**Table: `payments`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| shop_id | UUID | FK -> shops(id) CASCADE, indexed |
| platform_payment_id | VARCHAR(255) | UNIQUE |
| amount | VARCHAR(20) | NOT NULL |
| currency | VARCHAR(10) | NOT NULL |
| status | VARCHAR(50) | NOT NULL |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

```
ER Diagram:

  shops ----< settlements
    |
    +----< transactions
    |
    +----< payments
```

### The API Surface

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/commerce/finance/settlements` | List settlements with date range |
| GET | `/commerce/finance/transactions` | List transactions |
| GET | `/commerce/finance/payments` | List payments |

---

## Domain 5 -- Affiliate

### The Problem (Zero)

TikTok Shop has an affiliate/commission system where creators promote products in exchange for a percentage. Agencies need to manage which products are in the affiliate program, set commission rates, create open collaborations (any creator can apply) or targeted collaborations (invite specific creators), and review creator applications.

### The Process

1. **Product enrollment**: A seller enrolls products in the affiliate program, creating `affiliate_products` with commission rates.
2. **Open collaborations**: Seller sets up open collaboration offers. Any qualifying creator can apply.
3. **Target collaborations**: Seller invites specific creators to promote a product at a negotiated commission rate.
4. **Applications**: Creators apply to open collaborations. Seller reviews and approves/rejects via `creator_applications`.

### The Schema

**Table: `affiliate_products`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| shop_id | UUID | FK -> shops(id) CASCADE, indexed |
| product_id | VARCHAR(255) | NOT NULL |
| commission_rate | VARCHAR(20) | NULLABLE |
| status | VARCHAR(50) | default 'ACTIVE' |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Unique index: `(shop_id, product_id)`

**Table: `open_collaborations`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| product_id | VARCHAR(255) | NOT NULL |
| commission_rate | VARCHAR(20) | NOT NULL |
| status | VARCHAR(50) | default 'ACTIVE' |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

**Table: `target_collaborations`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| product_id | VARCHAR(255) | NOT NULL |
| creator_id | VARCHAR(255) | NOT NULL |
| commission_rate | VARCHAR(20) | NOT NULL |
| status | VARCHAR(50) | default 'ACTIVE' |
| invite_status | VARCHAR(50) | default 'PENDING' |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

**Table: `creator_applications`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| collaboration_id | UUID | NOT NULL |
| creator_id | VARCHAR(255) | NOT NULL |
| status | VARCHAR(50) | default 'PENDING' |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

```
ER Diagram:

  shops ----< affiliate_products

  open_collaborations ----< creator_applications
  target_collaborations
```

### The API Surface

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/commerce/affiliate/products` | List affiliate products |
| POST | `/commerce/affiliate/products` | Enroll a product |
| GET | `/commerce/affiliate/collaborations/open` | List open collaborations |
| GET | `/commerce/affiliate/collaborations/target` | List target collaborations |
| GET | `/commerce/affiliate/applications` | List creator applications |
| POST | `/commerce/affiliate/applications/{id}/approve` | Approve application |

---

## Domain 6 -- Advertising / Marketing

### The Problem (Zero)

Agencies run TikTok ad campaigns across multiple advertiser accounts. They need to manage the full campaign hierarchy (campaigns > ad groups > ads), track performance metrics, manage audiences and pixels, cache report data, and support advanced features like catalogs, creatives, Symphony automation, and Business Center.

### The Process

1. **Ad account discovery**: After connecting a Marketing account, Frodo discovers all advertiser IDs from the token response and creates `ad_accounts`.
2. **Campaign sync**: Celery tasks sync the hierarchy: campaigns first, then ad groups for each campaign, then ads for each ad group. Each level is upserted by platform ID.
3. **Reporting**: The report engine requests metrics from the Marketing Reporting API. Results are cached in `report_cache` with a 1-hour TTL to avoid redundant API calls.
4. **Audiences**: Custom and Lookalike audiences are synced for targeting configuration.
5. **Pixels**: Tracking pixel configuration is synced for conversion measurement.
6. **Catalogs**: Product catalogs (for Catalog Sales campaigns) are synced.
7. **Ad sync cursors**: Track incremental sync state per entity type per ad account.

### The Schema

**Table: `ad_accounts`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| connected_account_id | UUID | FK -> connected_accounts(id) CASCADE |
| advertiser_id | VARCHAR(255) | UNIQUE |
| advertiser_name | VARCHAR(255) | NOT NULL |
| currency | VARCHAR(10) | NULLABLE |
| timezone | VARCHAR(100) | NULLABLE |
| last_sync_at | TIMESTAMPTZ | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

**Table: `campaigns`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| ad_account_id | UUID | FK -> ad_accounts(id) CASCADE, indexed |
| platform_campaign_id | VARCHAR(255) | UNIQUE |
| campaign_name | VARCHAR(500) | NOT NULL |
| objective_type | VARCHAR(100) | NULLABLE |
| budget_mode | VARCHAR(50) | NULLABLE |
| budget | VARCHAR(20) | NULLABLE |
| operation_status | VARCHAR(50) | default 'ENABLE' |
| secondary_status | VARCHAR(100) | NULLABLE |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(workspace_id, operation_status)`

**Table: `ad_groups`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| ad_account_id | UUID | FK, indexed |
| campaign_id | UUID | FK -> campaigns(id) CASCADE, indexed |
| platform_adgroup_id | VARCHAR(255) | UNIQUE |
| adgroup_name | VARCHAR(500) | NOT NULL |
| placement_type | VARCHAR(100) | NULLABLE |
| bid_type | VARCHAR(50) | NULLABLE |
| bid_amount | VARCHAR(20) | NULLABLE |
| budget | VARCHAR(20) | NULLABLE |
| optimization_goal | VARCHAR(100) | NULLABLE |
| operation_status | VARCHAR(50) | default 'ENABLE' |
| targeting_json | JSONB | NULLABLE |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(workspace_id, operation_status)`

**Table: `ads`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| ad_account_id | UUID | FK, indexed |
| adgroup_id | UUID | FK -> ad_groups(id) CASCADE, indexed |
| platform_ad_id | VARCHAR(255) | UNIQUE |
| ad_name | VARCHAR(500) | NOT NULL |
| ad_format | VARCHAR(50) | NULLABLE |
| ad_text | VARCHAR(1000) | NULLABLE |
| call_to_action | VARCHAR(100) | NULLABLE |
| landing_page_url | VARCHAR(2048) | NULLABLE |
| image_url | VARCHAR(2048) | NULLABLE |
| operation_status | VARCHAR(50) | default 'ENABLE' |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(workspace_id, operation_status)`

**Table: `audiences`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| ad_account_id | UUID | FK, indexed |
| platform_audience_id | VARCHAR(255) | UNIQUE |
| name | VARCHAR(500) | NOT NULL |
| audience_type | VARCHAR(50) | NOT NULL (CUSTOM, LOOKALIKE) |
| size | INT | NULLABLE |
| status | VARCHAR(50) | default 'ENABLE' |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(workspace_id, audience_type)`

**Table: `pixels`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| ad_account_id | UUID | FK, indexed |
| platform_pixel_id | VARCHAR(255) | UNIQUE |
| name | VARCHAR(500) | NOT NULL |
| pixel_code | TEXT | NULLABLE |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

**Table: `catalogs`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| ad_account_id | UUID | FK, indexed |
| platform_catalog_id | VARCHAR(255) | UNIQUE |
| name | VARCHAR(500) | NOT NULL |
| product_count | INT | default 0 |
| status | VARCHAR(50) | default 'ACTIVE' |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

**Table: `report_cache`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| ad_account_id | UUID | FK, indexed |
| report_type | VARCHAR(50) | NOT NULL |
| data_level | VARCHAR(50) | NOT NULL |
| date_range_start | VARCHAR(10) | NOT NULL |
| date_range_end | VARCHAR(10) | NOT NULL |
| report_data | JSONB | NULLABLE |
| expires_at | TIMESTAMPTZ | NOT NULL |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Composite index: `(ad_account_id, report_type, data_level, date_range_start, date_range_end)`

**Table: `ad_sync_cursors`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| ad_account_id | UUID | FK -> ad_accounts(id) CASCADE |
| sync_type | VARCHAR(50) | NOT NULL |
| last_sync_at | TIMESTAMPTZ | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Unique index: `(ad_account_id, sync_type)`

```
ER Diagram:

  ad_accounts ----< campaigns ----< ad_groups ----< ads
       |
       +----< audiences
       +----< pixels
       +----< catalogs
       +----< report_cache
       +----< ad_sync_cursors
```

### The API Surface

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ads/accounts` | List ad accounts |
| GET | `/ads/accounts/{id}` | Get ad account details |
| GET | `/ads/campaigns` | List campaigns with filtering |
| POST | `/ads/campaigns` | Create a campaign |
| PATCH | `/ads/campaigns/{id}` | Update campaign |
| GET | `/ads/ad-groups` | List ad groups |
| GET | `/ads/ads` | List ads |
| GET | `/ads/reports` | Generate/fetch reports |
| GET | `/ads/audiences` | List audiences |
| GET | `/ads/pixels` | List pixels |
| GET | `/ads/catalogs` | List catalogs |
| GET | `/ads/creatives/...` | Creative management |
| GET | `/ads/business-center/...` | Business Center operations |
| GET | `/ads/symphony/...` | Symphony (AI) automation |

---

## Domain 7 -- Content

### The Problem (Zero)

Agencies need a unified view of all TikTok videos across their connected Developer accounts. They need to track video performance over time, post new content via the Direct Post API, manage a content calendar, and moderate comments.

### The Process

1. **Video sync**: Celery tasks call the Developer Video List API and upsert `videos` rows by `platform_video_id`. Engagement counts (views, likes, comments, shares) are updated on each sync.
2. **Metrics snapshots**: Daily snapshots of per-video metrics are stored in `video_metrics` for time-series analysis (growth tracking).
3. **Content publishing**: Users initiate a post from the Frodo UI. A `content_publish_jobs` row tracks the publish lifecycle (PENDING -> UPLOADING -> PROCESSING -> PUBLISHED or FAILED).
4. **Comment sync**: Comments on owned videos are synced and stored in `comments`, including threaded replies.
5. **Sync cursors**: `content_sync_cursors` track incremental sync state per connected account.

### The Schema

**Table: `videos`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| connected_account_id | UUID | FK -> connected_accounts(id) CASCADE |
| platform_video_id | VARCHAR(255) | UNIQUE |
| title | VARCHAR(500) | NULLABLE |
| description | VARCHAR(5000) | NULLABLE |
| cover_url | VARCHAR(2048) | NULLABLE |
| video_url | VARCHAR(2048) | NULLABLE |
| embed_link | VARCHAR(2048) | NULLABLE |
| duration | INT | NULLABLE (seconds) |
| status | VARCHAR(50) | default 'PUBLIC' |
| view_count | INT | default 0 |
| like_count | INT | default 0 |
| comment_count | INT | default 0 |
| share_count | INT | default 0 |
| create_time | TIMESTAMPTZ | NULLABLE |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(workspace_id, status)`

**Table: `video_metrics`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| video_id | UUID | FK -> videos(id) CASCADE, indexed |
| date | DATE | NOT NULL |
| views | INT | default 0 |
| likes | INT | default 0 |
| comments | INT | default 0 |
| shares | INT | default 0 |
| avg_watch_time | FLOAT | NULLABLE |
| reach | INT | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Unique index: `(video_id, date)`

**Table: `content_publish_jobs`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| connected_account_id | UUID | FK |
| publish_id | VARCHAR(255) | UNIQUE |
| title | VARCHAR(500) | NULLABLE |
| video_url | VARCHAR(2048) | NULLABLE |
| privacy_level | VARCHAR(50) | default 'PUBLIC_TO_EVERYONE' |
| status | VARCHAR(50) | default 'PENDING' |
| platform_video_id | VARCHAR(255) | NULLABLE (set on completion) |
| error_message | TEXT | NULLABLE |
| disable_duet | BOOLEAN | default false |
| disable_comment | BOOLEAN | default false |
| disable_stitch | BOOLEAN | default false |
| brand_content_toggle | BOOLEAN | default false |
| brand_organic_toggle | BOOLEAN | default false |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(workspace_id, status)`

**Table: `comments`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| video_id | UUID | FK -> videos(id) CASCADE, indexed |
| platform_comment_id | VARCHAR(255) | UNIQUE |
| parent_comment_id | VARCHAR(255) | NULLABLE (for replies) |
| text | TEXT | NOT NULL |
| like_count | INT | default 0 |
| reply_count | INT | default 0 |
| author_username | VARCHAR(255) | NULLABLE |
| author_avatar_url | VARCHAR(2048) | NULLABLE |
| comment_create_time | TIMESTAMPTZ | NULLABLE |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(video_id, parent_comment_id)`

**Table: `content_sync_cursors`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| connected_account_id | UUID | FK |
| sync_type | VARCHAR(50) | NOT NULL |
| cursor_value | VARCHAR(255) | NULLABLE |
| last_sync_at | TIMESTAMPTZ | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Unique index: `(connected_account_id, sync_type)`

```
ER Diagram:

  videos ----< video_metrics
    |
    +----< comments (self-referencing via parent_comment_id)

  content_publish_jobs (standalone, linked by connected_account_id)
  content_sync_cursors (per connected account)
```

### The API Surface

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/content/videos` | List videos with filtering |
| GET | `/content/videos/{id}` | Get video detail + metrics history |
| POST | `/content/publish` | Initiate content publish |
| GET | `/content/publish/{id}/status` | Check publish job status |
| GET | `/content/calendar` | Content calendar view |
| GET | `/content/comments` | List comments for a video |
| POST | `/content/comments/{id}/reply` | Reply to a comment |
| GET | `/content/commercial/...` | Commercial music/content data |
| POST | `/content/bridge/...` | Content bridge operations |

---

## Domain 8 -- Creators

### The Problem (Zero)

Agencies need to discover TikTok creators for partnership campaigns, track their profiles and audience demographics, send campaign invitations, and authorize creator content for use as Spark Ads. This bridges the gap between organic content and paid advertising.

### The Process

1. **Creator discovery**: Search TikTok's creator marketplace (TTCM/TikTok One). Results are stored in `creator_profiles` with audience demographics, engagement rates, and tier classification.
2. **Campaign creation**: Agency creates a `creator_campaign` with budget, date range, target categories, and creator requirements.
3. **Invitation**: Agency invites specific creators to a campaign via `creator_invitations`. Creators accept, decline, or let invitations expire.
4. **Content authorization**: For Spark Ads, creators authorize specific videos. The authorization code is stored in `content_authorizations` with an expiry date.
5. **Spark Ads creation**: The authorized video + authorization code are used in the Advertising module to create a Spark Ad.

### The Schema

**Table: `creator_profiles`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| platform_creator_id | VARCHAR(255) | NOT NULL |
| username | VARCHAR(255) | NULLABLE |
| display_name | VARCHAR(500) | NULLABLE |
| avatar_url | VARCHAR(2048) | NULLABLE |
| bio | TEXT | NULLABLE |
| follower_count | INT | default 0 |
| following_count | INT | default 0 |
| likes_count | INT | default 0 |
| video_count | INT | default 0 |
| tier | VARCHAR(50) | NULLABLE (NANO, MICRO, MID, MACRO, MEGA) |
| categories | JSONB | NULLABLE |
| audience_demographics | JSONB | NULLABLE |
| engagement_rate | VARCHAR(20) | NULLABLE |
| is_saved | BOOLEAN | default false |
| detail_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Unique index: `(workspace_id, platform_creator_id)`
Index: `(workspace_id, is_saved)`

**Table: `creator_campaigns`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| name | VARCHAR(500) | NOT NULL |
| description | TEXT | NULLABLE |
| status | VARCHAR(50) | default 'DRAFT' |
| budget | VARCHAR(20) | NULLABLE |
| start_date / end_date | TIMESTAMPTZ | NULLABLE |
| target_categories | JSONB | NULLABLE |
| requirements | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(workspace_id, status)`

**Table: `creator_invitations`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| campaign_id | UUID | FK -> creator_campaigns(id) CASCADE, indexed |
| creator_id | UUID | FK -> creator_profiles(id) CASCADE, indexed |
| status | VARCHAR(50) | default 'PENDING' |
| message | TEXT | NULLABLE |
| offered_amount | VARCHAR(20) | NULLABLE |
| responded_at | TIMESTAMPTZ | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Unique index: `(campaign_id, creator_id)`

**Table: `content_authorizations`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| creator_id | UUID | FK -> creator_profiles(id) CASCADE, indexed |
| platform_video_id | VARCHAR(255) | NULLABLE |
| authorization_code | VARCHAR(500) | NULLABLE |
| status | VARCHAR(50) | default 'PENDING' |
| expires_at | TIMESTAMPTZ | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(workspace_id, status)`

```
ER Diagram:

  creator_campaigns ----< creator_invitations >---- creator_profiles
                                                          |
                                                          +----< content_authorizations
```

### The API Surface

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/creators/profiles` | Search/list creator profiles |
| GET | `/creators/profiles/{id}` | Get creator detail + demographics |
| POST | `/creators/profiles/{id}/save` | Save creator to workspace list |
| GET | `/creators/campaigns` | List creator campaigns |
| POST | `/creators/campaigns` | Create a campaign |
| POST | `/creators/campaigns/{id}/invite` | Invite creator to campaign |
| GET | `/creators/invitations` | List invitations |
| GET | `/creators/authorizations` | List Spark Ads authorizations |
| POST | `/creators/authorizations` | Request content authorization |

---

## Domain 9 -- Analytics & Notifications

### The Problem (Zero)

Agencies need a unified dashboard that aggregates KPIs across all domains (commerce, advertising, content, creators). They need scheduled reports in multiple formats, a notification system for important events, notification preferences, and API keys for programmatic access.

### The Process

1. **KPI snapshots**: A nightly Celery task computes unified metrics across all modules and writes a `unified_kpi_snapshots` row per workspace per day. This includes total orders, revenue, AOV, active campaigns, ad spend, impressions, clicks, video counts, views, ROAS, CTR.
2. **Scheduled reports**: Users configure `scheduled_reports` with module selection, metric selection, frequency (daily/weekly/monthly), and format (CSV/XLSX/JSON). Celery Beat generates and delivers them.
3. **Notifications**: System events (order anomalies, token failures, campaign status changes) create `notifications` for the relevant user. Users configure `notification_preferences` per module and channel (in-app, email, webhook).
4. **API keys**: Workspaces can generate `api_keys` for programmatic access. Keys are hashed with SHA-256 and only the prefix is stored for identification.

### The Schema

**Table: `unified_kpi_snapshots`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| date | DATE | NOT NULL |
| total_orders | INT | default 0 |
| total_revenue | VARCHAR(20) | default '0' |
| average_order_value | VARCHAR(20) | default '0' |
| active_campaigns | INT | default 0 |
| total_ad_spend | VARCHAR(20) | default '0' |
| total_impressions | INT | default 0 |
| total_clicks | INT | default 0 |
| total_videos | INT | default 0 |
| total_views | INT | default 0 |
| total_likes | INT | default 0 |
| total_shares | INT | default 0 |
| saved_creators | INT | default 0 |
| active_creator_campaigns | INT | default 0 |
| roas | VARCHAR(20) | NULLABLE |
| ctr | VARCHAR(20) | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Unique index: `(workspace_id, date)`

**Table: `scheduled_reports`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| created_by | UUID | FK -> users(id) CASCADE |
| name | VARCHAR(500) | NOT NULL |
| description | TEXT | NULLABLE |
| modules | JSONB | NOT NULL |
| metrics | JSONB | NOT NULL |
| frequency | VARCHAR(50) | default 'WEEKLY' |
| format | VARCHAR(10) | default 'CSV' |
| is_active | BOOLEAN | default true |
| last_run_at | TIMESTAMPTZ | NULLABLE |
| next_run_at | TIMESTAMPTZ | NULLABLE |
| last_result_json | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(workspace_id, is_active)`

**Table: `notifications`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| user_id | UUID | FK -> users(id) CASCADE, indexed |
| notification_type | VARCHAR(50) | default 'INFO' |
| title | VARCHAR(500) | NOT NULL |
| message | TEXT | NOT NULL |
| module | VARCHAR(50) | NULLABLE |
| action_url | VARCHAR(2048) | NULLABLE |
| is_read | BOOLEAN | default false |
| read_at | TIMESTAMPTZ | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Indexes: `(user_id, is_read)`, `(workspace_id, created_at)`

**Table: `notification_preferences`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK -> users(id) CASCADE |
| module | VARCHAR(50) | NOT NULL |
| channel | VARCHAR(50) | default 'IN_APP' |
| is_enabled | BOOLEAN | default true |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Unique index: `(user_id, module, channel)`

**Table: `api_keys`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| created_by | UUID | FK -> users(id) CASCADE |
| name | VARCHAR(255) | NOT NULL |
| key_prefix | VARCHAR(12) | NOT NULL |
| key_hash | VARCHAR(128) | UNIQUE |
| scopes | JSONB | NOT NULL |
| is_active | BOOLEAN | default true |
| last_used_at | TIMESTAMPTZ | NULLABLE |
| expires_at | TIMESTAMPTZ | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(workspace_id, is_active)`

Key generation: `frodo_{random_token}`, prefix = first 12 chars, hash = SHA-256.

```
ER Diagram:

  workspace ----< unified_kpi_snapshots
      |
      +----< scheduled_reports >---- users
      +----< notifications >---- users
      +----< api_keys >---- users

  users ----< notification_preferences
```

### The API Surface

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/overview` | Unified KPI dashboard |
| GET | `/analytics/overview/history` | KPI time series |
| GET | `/analytics/reports` | List scheduled reports |
| POST | `/analytics/reports` | Create a scheduled report |
| PATCH | `/analytics/reports/{id}` | Update report config |
| DELETE | `/analytics/reports/{id}` | Delete a report |
| GET | `/analytics/notifications` | List notifications |
| PATCH | `/analytics/notifications/{id}/read` | Mark as read |
| GET | `/analytics/api-keys` | List API keys |
| POST | `/analytics/api-keys` | Generate a new API key |
| DELETE | `/analytics/api-keys/{id}` | Revoke an API key |

---

## Domain 10 -- Messaging

### The Problem (Zero)

TikTok Shop sellers communicate with buyers through in-platform messaging. Agencies need to view conversations, send replies, and configure automated responses (welcome messages, suggested questions, chat prompts) across their shops.

### The Process

1. **Conversation sync**: Messages are fetched from the TikTok Shop Customer Service API. Each conversation is identified by a TikTok conversation ID and associated with a participant.
2. **Message history**: Individual messages are stored with direction (INBOUND/OUTBOUND), content, optional media attachments, and timestamp.
3. **Sending replies**: Outbound messages are sent via the API and stored locally.
4. **Auto-messages**: Sellers configure automated welcome messages, suggested questions, and chat prompts. These are synced to TikTok via the API.

### The Schema

**Table: `conversations`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| connected_account_id | UUID | FK, indexed |
| tiktok_conversation_id | VARCHAR(255) | UNIQUE |
| participant_user_id | VARCHAR(255) | NULLABLE |
| participant_display_name | VARCHAR(500) | NULLABLE |
| status | VARCHAR(50) | default 'ACTIVE' |
| last_message_at | TIMESTAMPTZ | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(workspace_id, status)`

**Table: `messages`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| conversation_id | UUID | FK -> conversations(id) CASCADE, indexed |
| tiktok_message_id | VARCHAR(255) | UNIQUE |
| direction | VARCHAR(50) | NOT NULL (INBOUND, OUTBOUND) |
| content | TEXT | NULLABLE |
| media_url | VARCHAR(2048) | NULLABLE |
| sent_at | TIMESTAMPTZ | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(conversation_id, sent_at)`

**Table: `auto_messages`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| connected_account_id | UUID | FK, indexed |
| tiktok_auto_message_id | VARCHAR(255) | UNIQUE, NULLABLE |
| message_type | VARCHAR(50) | NOT NULL (WELCOME, SUGGESTED_QUESTION, CHAT_PROMPT) |
| content | TEXT | NOT NULL |
| is_active | BOOLEAN | default true |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(workspace_id, message_type)`

```
ER Diagram:

  conversations ----< messages

  auto_messages (linked to connected_account)
```

### The API Surface

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/messaging/conversations` | List conversations |
| GET | `/messaging/conversations/{id}` | Get conversation + messages |
| POST | `/messaging/conversations/{id}/send` | Send a message |
| GET | `/messaging/auto-messages` | List auto-message configs |
| POST | `/messaging/auto-messages` | Create auto-message |
| PATCH | `/messaging/auto-messages/{id}` | Update auto-message |
| DELETE | `/messaging/auto-messages/{id}` | Delete auto-message |

---

## Domain 11 -- LIVE

### The Problem (Zero)

TikTok LIVE streams are increasingly important for commerce (live selling) and engagement. Agencies need to monitor active streams, capture real-time events (comments, gifts, likes, follows, joins, commerce events), and analyze session performance post-stream.

### The Process

1. **Session creation**: When a monitored account starts a LIVE stream, a `live_sessions` row is created with the TikTok username and room ID.
2. **Event capture**: During the stream, events are captured and stored in `live_events`. Each event has a type, optional user info, a JSONB payload, and a precise timestamp.
3. **Analytics aggregation**: When the session ends, a `live_analytics` row is computed with aggregated metrics: total viewers, peak concurrent, total engagement, gift revenue, top commenters/gifters.
4. **Post-session**: The session status transitions from `monitoring` to `ended`.

### The Schema

**Table: `live_sessions`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| unique_id | VARCHAR(255) | NOT NULL (TikTok username) |
| room_id | VARCHAR(255) | NULLABLE |
| status | VARCHAR(50) | default 'monitoring' |
| started_at | TIMESTAMPTZ | NOT NULL |
| ended_at | TIMESTAMPTZ | NULLABLE |
| error_message | TEXT | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(workspace_id, status)`

**Table: `live_events`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| session_id | UUID | FK -> live_sessions(id) CASCADE, indexed |
| event_type | VARCHAR(50) | NOT NULL |
| user_id | VARCHAR(255) | NULLABLE |
| username | VARCHAR(255) | NULLABLE |
| payload | JSONB | NOT NULL |
| timestamp | TIMESTAMPTZ | NOT NULL |

Note: Uses `UUIDMixin` only -- no `TimestampMixin` (events have their own timestamp).

Indexes: `(session_id, event_type)`, `(session_id, timestamp)`

**Table: `live_analytics`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| session_id | UUID | FK -> live_sessions(id) CASCADE, UNIQUE |
| total_viewers | INT | default 0 |
| peak_concurrent | INT | default 0 |
| total_comments | INT | default 0 |
| total_likes | INT | default 0 |
| total_shares | INT | default 0 |
| total_follows | INT | default 0 |
| gift_revenue | FLOAT | default 0.0 |
| engagement_rate | FLOAT | default 0.0 |
| top_commenters | JSONB | NULLABLE |
| top_gifters | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

One-to-one with `live_sessions`.

```
ER Diagram:

  live_sessions ----< live_events
       |
       +----1 live_analytics
```

### The API Surface

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/live/sessions` | List LIVE sessions |
| GET | `/live/sessions/{id}` | Get session detail |
| POST | `/live/sessions` | Start monitoring a session |
| PATCH | `/live/sessions/{id}/end` | End a session |
| GET | `/live/sessions/{id}/events` | Get events for a session |
| GET | `/live/analytics/{session_id}` | Get session analytics |

---

## Domain 12 -- Intelligence

### The Problem (Zero)

Agencies need market intelligence: what hashtags/sounds/products are trending, what competitors are posting, and the ability to run research queries against TikTok's Research API. Without this, agencies react to trends instead of anticipating them.

### The Process

1. **Trend tracking**: Celery tasks periodically capture trending hashtags, sounds, and products from TikTok's APIs. Each snapshot records the trend name, engagement score, region, and timestamp.
2. **Competitor tracking**: Users add competitor TikTok accounts to watch. Celery syncs their public profile data and recent content with engagement metrics.
3. **Research queries**: Users define saved research queries with parameters. These can be re-run on demand against TikTok's Research API.

### The Schema

**Table: `trend_snapshots`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| trend_type | VARCHAR(50) | NOT NULL (hashtag, sound, product) |
| name | VARCHAR(255) | NOT NULL |
| engagement_score | FLOAT | default 0.0 |
| region | VARCHAR(10) | NULLABLE |
| metadata_json | JSONB | NULLABLE |
| captured_at | TIMESTAMPTZ | NOT NULL |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Index: `(workspace_id, trend_type, captured_at)`

**Table: `competitor_trackers`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| username | VARCHAR(255) | NOT NULL |
| display_name | VARCHAR(255) | NULLABLE |
| platform_user_id | VARCHAR(255) | NULLABLE |
| profile_data | JSONB | NULLABLE |
| last_synced_at | TIMESTAMPTZ | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Unique index: `(workspace_id, username)`

**Table: `competitor_content`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| tracker_id | UUID | FK -> competitor_trackers(id) CASCADE, indexed |
| video_id | VARCHAR(255) | NOT NULL |
| description | TEXT | NULLABLE |
| metrics | JSONB | NOT NULL |
| hashtags | JSONB | NULLABLE |
| published_at | TIMESTAMPTZ | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Unique index: `(tracker_id, video_id)`

**Table: `research_queries`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| name | VARCHAR(255) | NOT NULL |
| query_params | JSONB | NOT NULL |
| last_run_at | TIMESTAMPTZ | NULLABLE |
| created_by | UUID | FK -> users(id) CASCADE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

```
ER Diagram:

  competitor_trackers ----< competitor_content

  trend_snapshots (standalone, time-series)
  research_queries (standalone, per user)
```

### The API Surface

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/intelligence/trends` | List trending items |
| GET | `/intelligence/trends/history` | Trend time series |
| GET | `/intelligence/competitors` | List tracked competitors |
| POST | `/intelligence/competitors` | Add a competitor to track |
| DELETE | `/intelligence/competitors/{id}` | Remove competitor |
| GET | `/intelligence/competitors/{id}/content` | Get competitor's content |
| GET | `/intelligence/creators` | Creator intelligence queries |
| GET | `/intelligence/sources` | Data sources configuration |

---

## Domain 13 -- Organic Monitoring

### The Problem (Zero)

Agencies need to know when their brand is mentioned on TikTok -- in posts, comments, or hashtags. They also need to manage comments on their own organic content (not just owned videos, but brand-related posts by others).

### The Process

1. **Keyword setup**: Users configure `mention_keywords` -- brand names, hashtags, or product names to monitor.
2. **Mention detection**: Background tasks search for mentions using the configured keywords. Found mentions are stored in `brand_mentions` with engagement data.
3. **Comment monitoring**: `organic_comments` tracks comments on posts where the brand is mentioned, enabling community management.

### The Schema

**Table: `brand_mentions`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| connected_account_id | UUID | FK |
| tiktok_post_id | VARCHAR(255) | NOT NULL |
| mention_type | VARCHAR(50) | NOT NULL (POST, COMMENT) |
| author_username | VARCHAR(255) | NOT NULL |
| content_snippet | TEXT | NULLABLE |
| engagement_count | INT | default 0 |
| mentioned_at | TIMESTAMPTZ | NOT NULL |
| metadata_ | JSONB | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

**Table: `mention_keywords`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| keyword | VARCHAR(255) | NOT NULL |
| is_hashtag | BOOLEAN | default false |
| is_active | BOOLEAN | default true |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Unique index: `(workspace_id, keyword)`

**Table: `organic_comments`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| tiktok_comment_id | VARCHAR(255) | UNIQUE |
| tiktok_post_id | VARCHAR(255) | NOT NULL |
| author_username | VARCHAR(255) | NOT NULL |
| content | TEXT | NOT NULL |
| like_count | INT | default 0 |
| reply_count | INT | default 0 |
| is_hidden | BOOLEAN | default false |
| commented_at | TIMESTAMPTZ | NOT NULL |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

```
ER Diagram:

  mention_keywords (config)

  brand_mentions (detected mentions)

  organic_comments (community comments)
```

### The API Surface

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/organic/accounts` | List organic monitoring accounts |
| GET | `/organic/mentions` | List brand mentions |
| GET | `/organic/mentions/keywords` | List monitored keywords |
| POST | `/organic/mentions/keywords` | Add a keyword |
| DELETE | `/organic/mentions/keywords/{id}` | Remove a keyword |

---

## Domain 14 -- Webhooks

### The Problem (Zero)

TikTok sends webhook events when state changes (order status updates, product changes, account deauthorizations, video publish completions, campaign status changes). Frodo must receive, verify, deduplicate, and process these events reliably across all platforms.

### The Process

1. **Receive**: Three separate endpoints (`/webhooks/shop`, `/webhooks/developer`, `/webhooks/marketing`) receive POST requests from TikTok.
2. **Verify signature**: Each platform uses a different signing mechanism (HMAC-SHA256 for Shop, TikTok-Signature header for Developer, subscription-specific for Marketing).
3. **Deduplicate**: Redis SETNX on idempotency key prevents duplicate processing.
4. **Store**: The raw payload is stored in `webhook_events` with status `received`.
5. **Enqueue**: A Celery task is dispatched for async processing.
6. **Process**: The worker parses the event, routes to the appropriate domain handler, updates local DB, publishes to Redis pub/sub for real-time UI updates, and marks the event as `processed`.
7. **Failure handling**: Failed events are marked with an error message for retry or investigation.

### The Schema

**Table: `webhook_events`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| platform | ENUM(shop,developer,marketing,...) | NOT NULL, indexed |
| event_type | VARCHAR(255) | NOT NULL, indexed |
| idempotency_key | VARCHAR(255) | UNIQUE, indexed |
| payload | JSONB | NOT NULL |
| status | ENUM(received,processing,processed,failed) | NOT NULL, default 'received' |
| error_message | TEXT | NULLABLE |
| workspace_id | UUID | FK -> workspaces(id) SET NULL, NULLABLE, indexed |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

Note: `workspace_id` uses `ON DELETE SET NULL` (not CASCADE) because webhook events are an audit trail that should survive workspace deletion.

```
ER Diagram:

  webhook_events (standalone, cross-cutting audit table)
```

### The API Surface

Webhook events are not exposed via the REST API for external consumption. They are received at:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/webhooks/shop` | TikTok Shop webhook receiver |
| POST | `/webhooks/developer` | TikTok Developer webhook receiver |
| POST | `/webhooks/marketing` | TikTok Marketing webhook receiver |

---

## Domain 15 -- Data Sync

### The Problem (Zero)

All TikTok data in Frodo is a local cache of platform data. Sync jobs must run reliably on schedule, track progress, handle failures, and allow manual re-triggers. The system must never rely solely on webhooks -- polling is the primary sync mechanism with webhooks for real-time supplementation.

### The Process

1. **Job creation**: Celery Beat schedules periodic sync jobs. Users can also trigger manual syncs via the API.
2. **Job execution**: A `sync_jobs` row tracks the workspace, connected account, platform, sync type, status, item counts, and timing.
3. **Progress tracking**: As items are synced, `items_synced` is updated. WebSocket publishes progress to the frontend.
4. **Completion**: On success, status moves to `completed` with `completed_at` timestamp. On failure, status moves to `failed` with `error_message`.
5. **Cursor management**: Domain-specific cursor tables (`sync_cursors`, `ad_sync_cursors`, `content_sync_cursors`) track the incremental position for each entity type.

### The Schema

**Table: `sync_jobs`**

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workspace_id | UUID | FK, indexed |
| connected_account_id | UUID | FK -> connected_accounts(id) CASCADE, indexed |
| platform | VARCHAR(50) | NOT NULL |
| sync_type | VARCHAR(50) | NOT NULL (orders, products, campaigns, etc.) |
| status | ENUM(pending,running,completed,failed) | NOT NULL, default 'pending' |
| items_synced | INT | default 0 |
| items_total | INT | NULLABLE |
| error_message | TEXT | NULLABLE |
| started_at | TIMESTAMPTZ | NULLABLE |
| completed_at | TIMESTAMPTZ | NULLABLE |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL |

The cursor tables (`sync_cursors`, `ad_sync_cursors`, `content_sync_cursors`) are documented in their respective domain sections above.

```
ER Diagram:

  sync_jobs (cross-cutting, linked to connected_accounts + workspaces)

  sync_cursors (commerce, per shop)
  ad_sync_cursors (advertising, per ad account)
  content_sync_cursors (content, per connected account)
```

### The API Surface

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/connect/sync/jobs` | List recent sync jobs |
| GET | `/connect/sync/active` | Get currently running sync jobs |
| POST | `/connect/sync/trigger` | Manually trigger a sync |
| WS | `/connect/ws` | Real-time sync progress via WebSocket |

---

## Summary: Table Count by Domain

| Domain | Tables | Key Patterns |
|--------|--------|-------------|
| Auth & Multi-Tenancy | 4 | users, organizations, workspaces, memberships |
| Social Identity | 1 | social_identities |
| Token Vault & Connections | 3 | connected_accounts, token_vault, platform_app_credentials |
| Commerce | 8 | shops, products, product_skus, orders, order_line_items, packages, order_status_events, return_requests |
| Commerce Extras | 2 | promotions, sync_cursors |
| Finance | 3 | settlements, transactions, payments |
| Affiliate | 4 | affiliate_products, open_collaborations, target_collaborations, creator_applications |
| Advertising | 8 | ad_accounts, campaigns, ad_groups, ads, audiences, pixels, catalogs, report_cache |
| Advertising Extras | 1 | ad_sync_cursors |
| Content | 5 | videos, video_metrics, content_publish_jobs, comments, content_sync_cursors |
| Creators | 4 | creator_profiles, creator_campaigns, creator_invitations, content_authorizations |
| Analytics & Notifications | 5 | unified_kpi_snapshots, scheduled_reports, notifications, notification_preferences, api_keys |
| Messaging | 3 | conversations, messages, auto_messages |
| LIVE | 3 | live_sessions, live_events, live_analytics |
| Intelligence | 4 | trend_snapshots, competitor_trackers, competitor_content, research_queries |
| Organic | 3 | brand_mentions, mention_keywords, organic_comments |
| Webhooks | 1 | webhook_events |
| Data Sync | 1 | sync_jobs |
| **Total** | **63** | |

All tables use UUID primary keys and TIMESTAMPTZ timestamps. All tenant-scoped tables have a `workspace_id` foreign key with CASCADE delete. The codebase is at `backend/db/models/` with one file per domain.

# TikTok Shop End-to-End Brand Operations — Design Spec

**Date:** 2026-03-30
**Status:** Draft
**Author:** Amit + Claude
**Project:** Frodo — Unified TikTok SaaS Platform

## Overview

Frodo currently covers ~60% of what a TikTok Shop brand owner needs for daily operations. This spec adds the missing 40% across 6 phases and 7 new backend modules, bringing the platform to full end-to-end coverage.

### What's Being Built

| Phase | Module | Purpose |
|-------|--------|---------|
| A | `promotions` | Flash Deals, Product Discounts, Coupon sync |
| B | `finance` | Settlements, Transactions, Payments, Withdrawals |
| C | `gmvmax` | Guided GMV Max workflow + deep-link to Ads Manager + reporting |
| D | `customer_service` + `customer_engagement` | Buyer messaging inbox + proactive CRM re-engagement |
| E | `affiliate` | Creator discovery, collaborations, samples, commissions |
| F | `shop_health` | SPS tracking, violation monitoring, unified analytics, LIVE diagnosis |

### What's NOT in Scope

- Seller onboarding/registration (deferred)
- Coupon creation (TikTok API is read-only — sync only)
- GMV Max campaign creation via API (no open API exists — guided workflow + deep-link instead)
- Shop Design / storefront builder (Seller Center only, no API)
- TikTok-funded promotion enrollment (Seller Center only)
- Tax/bank info management (Seller Center only)

### Architecture Approach

**Module-per-feature** following existing project conventions:
- Each module: `routes/ + services/ + schemas.py` (+ `webhook_handlers.py` where applicable)
- New TikTok client method groups in `backend/tiktok/shop/`
- Frontend dashboard sections mirroring each backend module
- Celery workers for periodic sync and background processing

### Total Scope

| Metric | Count |
|--------|-------|
| New backend modules | 7 |
| New TikTok API integrations | ~56 endpoints |
| New database models | ~28 |
| New Celery workers | ~17 |
| New frontend dashboard sections | 7 |

---

## Phase A: Promotions Module

### Goal
Enable brand owners to create and manage Product Discounts and Flash Deals directly from Frodo, and browse synced Coupons. These are core sales drivers on TikTok Shop.

### Backend Structure

```
backend/modules/promotions/
├── __init__.py
├── routes/
│   ├── discount_routes.py
│   ├── flash_deal_routes.py
│   └── coupon_routes.py
├── services/
│   ├── discount_service.py
│   ├── flash_deal_service.py
│   └── coupon_service.py
├── schemas.py
└── webhook_handlers.py
```

### TikTok API Integration

**Client:** `backend/tiktok/shop/promotions.py`

| Operation | Method | API Endpoint | Notes |
|-----------|--------|-------------|-------|
| Create Activity | POST | `/promotion/activity` | type=PRODUCT_DISCOUNT or FLASH_DEAL |
| Update Activity | PUT | `/promotion/activity` | Modify discount, schedule, products |
| Deactivate Activity | POST | `/promotion/activity/deactivate` | End promotion early |
| Get Activity | GET | `/promotion/activity` | Full promotion details |
| Search Activities | GET | `/promotion/activity/search` | Filter by type, status, date |
| Add Activity Products | PUT | `/promotion/activity/product` | Add products to active promotion |
| Remove Activity Products | DELETE | `/promotion/activity/product` | Remove products |
| Search Coupons | GET | `/promotion/coupon/search` | Read-only sync |
| Get Coupon Detail | GET | `/promotion/coupon` | Read-only |

### Database Models

**Promotion** (extend existing model):
- Add: `max_quantity` (INT, nullable) — for flash deals with limited stock
- Add: `countdown_duration_hours` (INT, nullable) — flash deal duration, max 72
- Add: `price_rules` (JSONB) — per-SKU pricing: `[{sku_id, original_price, discount_price}]`
- Add: `stacking_rules` (JSONB) — which other promotion types this stacks with
- Add: `product_count` (INT) — number of products in promotion

**Coupon** (new):
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK, tenant scope |
| platform_coupon_id | VARCHAR | TikTok's coupon ID |
| code | VARCHAR(8) | 2-8 char coupon code |
| discount_type | ENUM | percentage, fixed_amount |
| discount_value | DECIMAL | % or $ amount |
| min_order_amount | DECIMAL | Minimum order to apply |
| validity_start | TIMESTAMP | |
| validity_end | TIMESTAMP | |
| total_claim_limit | INT | Max total claims |
| per_user_limit | INT | Max claims per buyer |
| claimed_count | INT | Current claims |
| used_count | INT | Actually redeemed |
| status | ENUM | active, expired, depleted |
| synced_at | TIMESTAMP | Last sync from TikTok |

**PromotionProduct** (new):
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| promotion_id | UUID | FK → Promotion |
| product_id | UUID | FK → Product |
| sku_id | UUID | FK → ProductSku, nullable |
| original_price | DECIMAL | Price before discount |
| discount_price | DECIMAL | Price after discount |
| quantity_limit | INT | Per-product stock limit, nullable |

### Validation Rules
- Flash Deals: discount_price must be ≤ 30-day lowest price (fetch from Product price history)
- Flash Deals: countdown_duration_hours ≤ 72
- Product Discounts: percentage off must be 1-99%
- Fixed price discounts: discount_price > 0

### Frontend Pages

`frontend/src/app/(dashboard)/promotions/`

| Page | Route | Description |
|------|-------|-------------|
| Promotions List | `/promotions` | Tabbed: Active / Scheduled / Ended. Filter by type. Summary cards. |
| Create Discount | `/promotions/create/discount` | Product selector, discount type toggle (fixed/%), schedule picker |
| Create Flash Deal | `/promotions/create/flash-deal` | Product selector, deal price with 30-day price validation, quantity, countdown preview |
| Promotion Detail | `/promotions/[id]` | Performance: orders, revenue, conversion lift vs non-promoted |
| Coupon Browser | `/promotions/coupons` | Synced from TikTok, search/filter, usage stats |

### Celery Workers
- `sync_promotions` — every 30min, sync promotion statuses from TikTok
- `sync_coupons` — every 2h, sync active coupons

---

## Phase B: Finance & Settlements Module

### Goal
Give brand owners visibility into revenue, fees, settlements, and payouts. Read-only data from TikTok Finance API — the financial dashboard they check daily for reconciliation.

### Backend Structure

```
backend/modules/finance/
├── __init__.py
├── routes/
│   ├── statement_routes.py
│   ├── transaction_routes.py
│   ├── payment_routes.py
│   └── withdrawal_routes.py
├── services/
│   ├── statement_service.py
│   ├── transaction_service.py
│   ├── payment_service.py
│   ├── withdrawal_service.py
│   └── finance_analytics.py
└── schemas.py
```

### TikTok API Integration

**Client:** `backend/tiktok/shop/finance.py`

| Operation | Method | API Endpoint | Notes |
|-----------|--------|-------------|-------|
| Get Statements | GET | `/finance/statements` | Daily statements |
| Get Statement Detail | GET | `/finance/statement` | Full breakdown |
| Get Payments | GET | `/finance/payments` | Payout records |
| Get Withdrawals | GET | `/finance/withdrawals` | Withdrawal history |
| Get Transactions by Order | GET | `/finance/transactions/order` | Order-level detail |
| Get Transactions by Statement | GET | `/finance/transactions/statement` | Per-statement breakdown |
| Get Unsettled Transactions | GET | `/finance/transactions/unsettled` | Pending with fees |

### Database Models

**Settlement**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK, tenant scope |
| platform_statement_id | VARCHAR | TikTok's statement ID |
| period_start | DATE | Statement period start |
| period_end | DATE | Statement period end |
| net_sales | DECIMAL | |
| shipping_total | DECIMAL | |
| fees_total | DECIMAL | |
| adjustments_total | DECIMAL | |
| payout_amount | DECIMAL | Net payout |
| currency | VARCHAR(3) | USD, GBP, etc. |
| status | ENUM | pending, issued, paid |
| issued_at | TIMESTAMP | |

**Transaction**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| settlement_id | UUID | FK → Settlement, nullable (unsettled) |
| platform_order_id | VARCHAR | TikTok order ID |
| sku_id | VARCHAR | SKU-level detail |
| transaction_type | ENUM | sale, refund, adjustment, chargeback |
| gross_amount | DECIMAL | |
| fee_breakdown | JSONB | `{referral_fee, affiliate_commission, shipping_cost, fbt_fee, refund_admin_fee}` |
| net_amount | DECIMAL | |
| transacted_at | TIMESTAMP | |

**Payment**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| settlement_id | UUID | FK → Settlement |
| platform_payment_id | VARCHAR | |
| amount | DECIMAL | |
| status | ENUM | pending, processing, completed, failed |
| bank_reference | VARCHAR | For reconciliation |
| paid_at | TIMESTAMP | |

**Withdrawal**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| platform_withdrawal_id | VARCHAR | |
| amount | DECIMAL | Min $2.00 |
| status | ENUM | requested, processing, completed, failed |
| requested_at | TIMESTAMP | |
| completed_at | TIMESTAMP | |

### Frontend Pages

`frontend/src/app/(dashboard)/finance/`

| Page | Route | Description |
|------|-------|-------------|
| Finance Overview | `/finance` | Period selector, net revenue chart, fee pie chart, settlement tier badge |
| Statements | `/finance/statements` | Daily statement list, expandable detail rows |
| Statement Detail | `/finance/statements/[id]` | Line-by-line breakdown |
| Transactions | `/finance/transactions` | Searchable by order ID, filterable by type, exportable CSV |
| Payments | `/finance/payments` | Payout history with bank reconciliation status |
| Unsettled | `/finance/unsettled` | Pending revenue, estimated payout date based on settlement tier |
| Fee Analysis | `/finance/fees` | Breakdown by fee type over time, cost driver identification |

### Settlement Tier Display
Show current tier + progress to next:
| Tier | Hold Period | Requirement |
|------|------------|-------------|
| Introductory | 31 days | New sellers |
| Standard | 8 days | Default |
| Accelerated | 5 days | SPS >= 3.5 |
| Express | 1 day | SPS >= 4.0 |

### Celery Workers
- `sync_statements` — daily at UTC 01:00 (after TikTok closes daily statements at UTC 00:00)
- `sync_unsettled` — every 4h, refresh pending transactions

---

## Phase C: GMV Max Campaign Module

### Goal
Help brand owners plan, validate, and launch GMV Max campaigns through a guided workflow. Since there's no open API for campaign creation, Frodo adds value through pre-validation, recommendations, deep-linking to Ads Manager, and post-creation performance tracking.

### Backend Structure

```
backend/modules/gmvmax/
├── __init__.py
├── routes/
│   ├── workflow_routes.py
│   ├── reporting_routes.py
│   └── deeplink_routes.py
├── services/
│   ├── workflow_service.py
│   ├── reporting_service.py
│   ├── deeplink_service.py
│   └── recommendation_service.py
└── schemas.py
```

### Guided Workflow (4 Steps)

**Step 1 — Campaign Type:**
- Product GMV Max: maximize non-live product sales via feed, search, shop tab
- LIVE GMV Max: maximize liveroom GMV via video-to-LIVE + LIVE-to-LIVE

**Step 2 — Product Selection:**
- Product picker with Frodo data overlay: conversion rate, margin (from Finance), stock level, active promotions
- Eligibility indicators: sufficient stock, valid pricing, product status = live
- "All products" option or specific selection

**Step 3 — Budget & ROI:**
- Daily budget input with recommendation based on: historical ad spend, product margins, category benchmarks
- ROI target input with benchmark comparison from past campaigns
- Estimated daily GMV projection: `budget × expected_roi`

**Step 4 — Review & Launch:**
- Summary of all selections
- Pre-validation results (eligibility, budget, product status)
- "Save Draft" button — persists config in Frodo
- "Open in Ads Manager" button — deep-link with campaign type context

### Deep-Link Strategy
Generate Ads Manager URL: `https://ads.tiktok.com/i18n/perf/campaign/create?type=gmvmax&subtype={product|live}`

After user creates the campaign in Ads Manager, Frodo matches it back via:
1. Periodic sync of active GMV Max campaigns from reporting API
2. Match by product overlap + creation timestamp proximity
3. User can manually link a draft to a synced campaign

### Database Models

**GmvMaxDraft**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| campaign_type | ENUM | product, live |
| product_ids | JSONB | Selected product IDs |
| daily_budget | DECIMAL | |
| roi_target | DECIMAL | |
| status | ENUM | draft, submitted, linked, archived |
| ads_manager_campaign_id | VARCHAR | Nullable, linked after creation in Ads Manager |
| notes | TEXT | User notes |
| created_by | UUID | FK → User |
| created_at | TIMESTAMP | |

**GmvMaxReport** (cached from reporting API):
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| campaign_id | VARCHAR | Ads Manager campaign ID |
| draft_id | UUID | FK → GmvMaxDraft, nullable |
| date | DATE | Report date |
| spend | DECIMAL | |
| total_gmv | DECIMAL | |
| paid_gmv | DECIMAL | |
| organic_gmv | DECIMAL | |
| orders | INT | |
| roi | DECIMAL | total_gmv / spend |
| impressions | INT | |
| clicks | INT | |

**GmvMaxRecommendation**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| product_id | UUID | FK → Product |
| recommended_budget | DECIMAL | |
| recommended_roi_target | DECIMAL | |
| confidence_score | DECIMAL | 0.0–1.0 |
| reasoning | JSONB | `{factors: [{name, value, weight}]}` |
| generated_at | TIMESTAMP | |

### Frontend Pages

`frontend/src/app/(dashboard)/gmvmax/`

| Page | Route | Description |
|------|-------|-------------|
| Campaign List | `/gmvmax` | Active campaigns from Ads Manager + Frodo drafts, spend/GMV/ROI cards |
| Create Wizard | `/gmvmax/create` | 4-step wizard (type → products → budget → review) |
| Campaign Detail | `/gmvmax/[id]` | Spend vs GMV chart, ROI trend, organic vs paid split, top products |
| Recommendations | `/gmvmax/recommendations` | Budget/ROI suggestions per product based on margins + history |

### Celery Workers
- `sync_gmvmax_reports` — every 6h, pull performance data for active campaigns
- `generate_recommendations` — daily, analyze performance + margins + inventory

### Cross-Module Dependencies
- Finance (Phase B): product margins for ROI recommendations
- Promotions (Phase A): active promotions affect pricing and GMV attribution
- Commerce (existing): product inventory + pricing data

---

## Phase D: Customer Service & Engagement Module

### Goal
Enable brand owners to manage buyer conversations from within Frodo (meeting the 80%+ 24h response rate SPS requirement), and proactively re-engage past buyers via TikTok's CRM-style engagement API.

### Backend Structure — Customer Service

```
backend/modules/customer_service/
├── __init__.py
├── routes/
│   ├── conversation_routes.py
│   ├── message_routes.py
│   ├── agent_routes.py
│   └── performance_routes.py
├── services/
│   ├── conversation_service.py
│   ├── message_service.py
│   ├── agent_service.py
│   └── performance_service.py
├── schemas.py
└── webhook_handlers.py
```

### Backend Structure — Customer Engagement

```
backend/modules/customer_engagement/
├── __init__.py
├── routes/
│   ├── template_routes.py
│   ├── engagement_routes.py
│   └── analytics_routes.py
├── services/
│   ├── template_service.py
│   ├── engagement_service.py
│   └── analytics_service.py
└── schemas.py
```

### TikTok API Integration — Customer Service

**Client:** `backend/tiktok/shop/customer_service.py`

| Operation | Method | API Endpoint |
|-----------|--------|-------------|
| Create Conversation | POST | `/customer_service/conversations` |
| Get Conversations | GET | `/customer_service/conversations` |
| Read Messages | GET | `/customer_service/conversations/messages` |
| Send Message | POST | `/customer_service/conversations/messages` |
| Upload Image | POST | `/customer_service/media/upload` |
| Get Agent Settings | GET | `/customer_service/agents/settings` |
| Update Agent Settings | PUT | `/customer_service/agents/settings` |
| Get CS Performance | GET | `/customer_service/performance` |
| Search Sessions | GET | `/customer_service/sessions` |

### TikTok API Integration — Customer Engagement

**Client:** `backend/tiktok/shop/customer_engagement.py`

| Operation | Method | API Endpoint |
|-----------|--------|-------------|
| Get Message Templates | GET | `/customer_engagement/templates` |
| Create Engagement Task | POST | `/customer_engagement/tasks` |
| Send Engagement Message | POST | `/customer_engagement/messages` |
| Get Task Performance | GET | `/customer_engagement/tasks/performance` |
| Create Custom Task | POST | `/customer_engagement/tasks/custom` |
| Get Feature Permissions | GET | `/customer_engagement/permissions` |

### Database Models

**Conversation**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| platform_conversation_id | VARCHAR | TikTok conversation ID |
| buyer_id | VARCHAR | TikTok buyer ID |
| buyer_name | VARCHAR | Display name |
| status | ENUM | open, resolved, closed |
| last_message_at | TIMESTAMP | |
| unread_count | INT | |
| linked_order_id | UUID | FK → Order, nullable |

**Message**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| conversation_id | UUID | FK → Conversation |
| platform_message_id | VARCHAR | |
| direction | ENUM | inbound, outbound |
| content_type | ENUM | text, image |
| content | TEXT | Message body or image URL |
| sent_at | TIMESTAMP | |
| read_at | TIMESTAMP | Nullable |

**AgentConfig**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK, unique |
| online_hours | JSONB | `{mon: {start: "09:00", end: "18:00"}, ...}` |
| auto_reply_enabled | BOOLEAN | |
| auto_reply_message | TEXT | Sent when offline |
| greeting_message | TEXT | Sent on first contact |

**CsPerformanceSnapshot**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| date | DATE | |
| response_rate_24h | DECIMAL | Target >= 80% |
| resolution_rate | DECIMAL | Target >= 65% |
| satisfaction_score | DECIMAL | Target >= 75% |
| total_conversations | INT | |
| avg_response_time_seconds | INT | |

**EngagementTask**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| platform_task_id | VARCHAR | |
| template_id | VARCHAR | FK → EngagementTemplate, nullable (custom tasks) |
| task_type | ENUM | template, custom |
| audience_filter | JSONB | `{purchased_last_days: 30, no_return: true}` |
| custom_message | TEXT | For custom tasks |
| status | ENUM | draft, sent, completed |
| sent_count | INT | |
| open_count | INT | |
| click_count | INT | |
| conversion_count | INT | |
| created_at | TIMESTAMP | |

**EngagementTemplate**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| platform_template_id | VARCHAR | |
| name | VARCHAR | |
| content_preview | TEXT | |
| template_type | VARCHAR | |
| synced_at | TIMESTAMP | |

### WebSocket Integration
Extend existing Redis pub/sub for real-time message notifications:
- Channel: `customer_service:{workspace_id}`
- Events: `new_message`, `conversation_updated`, `unread_count_changed`
- Frontend hook: `useCustomerServiceWebSocket`

### Frontend Pages — Customer Service

`frontend/src/app/(dashboard)/customer-service/`

| Page | Route | Description |
|------|-------|-------------|
| Inbox | `/customer-service` | Two-panel: conversation list (left) + message thread (right), buyer details |
| Agent Settings | `/customer-service/settings` | Online hours, auto-reply, greeting config |
| CS Dashboard | `/customer-service/analytics` | 3 KPI cards (response rate, resolution, satisfaction) + trends |

### Frontend Pages — Customer Engagement

`frontend/src/app/(dashboard)/engagement/`

| Page | Route | Description |
|------|-------|-------------|
| Templates | `/engagement` | Browse available templates |
| Create Task | `/engagement/create` | Select template or custom, define audience, schedule |
| Task History | `/engagement/history` | Sent tasks with performance (open, click, conversion rates) |

### Celery Workers
- `sync_conversations` — every 15min, pull new/updated conversations
- `sync_cs_performance` — daily, snapshot CS metrics
- `sync_engagement_templates` — daily, refresh available templates

---

## Phase E: Affiliate Program Module

### Goal
Full affiliate/creator collaboration management. This is how brand owners get creators to promote their products — one of the biggest GMV drivers on TikTok Shop. ~25 API endpoints.

### Backend Structure

```
backend/modules/affiliate/
├── __init__.py
├── routes/
│   ├── creator_routes.py
│   ├── open_collab_routes.py
│   ├── target_collab_routes.py
│   ├── sample_routes.py
│   ├── order_routes.py
│   └── messaging_routes.py
├── services/
│   ├── creator_service.py
│   ├── open_collab_service.py
│   ├── target_collab_service.py
│   ├── sample_service.py
│   ├── order_service.py
│   └── messaging_service.py
├── schemas.py
└── webhook_handlers.py
```

### TikTok API Integration

**Client:** `backend/tiktok/shop/affiliate.py`

**Creator Discovery:**
| Operation | Method | API Endpoint |
|-----------|--------|-------------|
| Search Creators | GET | `/affiliate/seller/creators` |
| Get Creator Performance | GET | `/affiliate/seller/creators/performance` |
| Get Creator Profile | GET | `/affiliate/seller/creators/profile` |

**Open Collaboration:**
| Operation | Method | API Endpoint |
|-----------|--------|-------------|
| Get Settings | GET | `/affiliate/seller/open_collaboration/settings` |
| Update Settings | PUT | `/affiliate/seller/open_collaboration/settings` |
| Add Products | POST | `/affiliate/seller/open_collaboration/products` |
| Remove Products | DELETE | `/affiliate/seller/open_collaboration/products` |
| Get Products | GET | `/affiliate/seller/open_collaboration/products` |

**Target Collaboration:**
| Operation | Method | API Endpoint |
|-----------|--------|-------------|
| Create | POST | `/affiliate/seller/target_collaboration` |
| List | GET | `/affiliate/seller/target_collaborations` |
| Update | PUT | `/affiliate/seller/target_collaboration` |
| Cancel | POST | `/affiliate/seller/target_collaboration/cancel` |

**Samples:**
| Operation | Method | API Endpoint |
|-----------|--------|-------------|
| Get Requests | GET | `/affiliate/seller/samples` |
| Review Request | POST | `/affiliate/seller/samples/review` |
| Get Shipment Status | GET | `/affiliate/seller/samples/shipment` |

**Orders & Links:**
| Operation | Method | API Endpoint |
|-----------|--------|-------------|
| Get Affiliate Orders | GET | `/affiliate/seller/orders` |
| Generate Promotion Link | POST | `/affiliate/seller/promotion_links` |

**Messaging:**
| Operation | Method | API Endpoint |
|-----------|--------|-------------|
| Get Conversations | GET | `/affiliate/seller/conversations` |
| Send Message | POST | `/affiliate/seller/conversations/messages` |

### Database Models

**AffiliateCreator**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| platform_creator_id | VARCHAR | TikTok creator ID |
| username | VARCHAR | |
| display_name | VARCHAR | |
| avatar_url | VARCHAR | |
| follower_count | INT | |
| engagement_rate | DECIMAL | |
| category | VARCHAR | Content niche |
| total_gmv | DECIMAL | Historical |
| avg_order_value | DECIMAL | |
| synced_at | TIMESTAMP | |

**OpenCollabConfig**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK, unique |
| enabled | BOOLEAN | |
| global_commission_rate | DECIMAL | % for all products |
| auto_add_products | BOOLEAN | Auto-add new products |
| require_approval | BOOLEAN | Approve creator applications |
| updated_at | TIMESTAMP | |

**OpenCollabProduct**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| product_id | UUID | FK → Product |
| commission_rate | DECIMAL | Override of global rate |
| status | ENUM | active, paused, removed |
| added_at | TIMESTAMP | |

**TargetCollaboration**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| platform_collab_id | VARCHAR | |
| creator_id | UUID | FK → AffiliateCreator |
| product_ids | JSONB | Selected products |
| commission_rate | DECIMAL | Custom rate for this creator |
| status | ENUM | pending, accepted, rejected, cancelled, expired, active, completed |
| invitation_message | TEXT | |
| created_at | TIMESTAMP | |
| responded_at | TIMESTAMP | |

**SampleRequest**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| platform_request_id | VARCHAR | |
| collaboration_id | UUID | FK → TargetCollaboration, nullable |
| creator_id | UUID | FK → AffiliateCreator |
| product_id | UUID | FK → Product |
| status | ENUM | pending, approved, rejected, shipped, received |
| rejection_reason | TEXT | Nullable |
| shipping_tracking | VARCHAR | Nullable |
| reviewed_at | TIMESTAMP | |
| shipped_at | TIMESTAMP | |

**AffiliateOrder**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| platform_order_id | VARCHAR | |
| creator_id | UUID | FK → AffiliateCreator |
| collab_type | ENUM | open, target |
| product_id | UUID | FK → Product |
| order_amount | DECIMAL | |
| commission_rate | DECIMAL | Rate at time of order |
| commission_amount | DECIMAL | |
| ordered_at | TIMESTAMP | |

**PromotionLink**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| creator_id | UUID | FK → AffiliateCreator |
| product_id | UUID | FK → Product |
| url | VARCHAR | Trackable link |
| click_count | INT | |
| order_count | INT | |
| gmv | DECIMAL | |
| created_at | TIMESTAMP | |

### Frontend Pages

`frontend/src/app/(dashboard)/affiliate/`

| Page | Route | Description |
|------|-------|-------------|
| Overview | `/affiliate` | Total affiliate GMV, active creators, pending actions, top creators leaderboard |
| Creator Discovery | `/affiliate/creators` | Search/filter by category, followers, engagement, GMV. Creator cards. Invite button. |
| Open Collaboration | `/affiliate/open` | Toggle, global commission, product list with overrides, approval queue |
| Target Collaborations | `/affiliate/target` | Create invitation, status pipeline, performance per collaboration |
| Collaboration Detail | `/affiliate/target/[id]` | Creator info, products, commission, messages, orders from this collaboration |
| Samples | `/affiliate/samples` | Request queue (approve/reject), shipment tracking |
| Affiliate Orders | `/affiliate/orders` | By creator, product, date. Commission breakdown. CSV export. |
| Creator Messaging | `/affiliate/messages` | IM interface for creator conversations |

### Celery Workers
- `sync_affiliate_creators` — daily, refresh performance data for saved creators
- `sync_affiliate_orders` — every 2h, pull affiliate-attributed orders
- `sync_sample_requests` — every 30min, check for new sample requests
- `sync_open_collab_products` — daily, reconcile product list with TikTok

---

## Phase F: Analytics & Shop Health Module

### Goal
The intelligence layer that ties all modules together. Estimated SPS tracking (TikTok doesn't expose SPS via API), violation monitoring, unified analytics, LIVE diagnosis, and proactive health alerts. This is the "morning command center" brand owners open first.

### Backend Structure

```
backend/modules/shop_health/
├── __init__.py
├── routes/
│   ├── sps_routes.py
│   ├── violation_routes.py
│   ├── analytics_routes.py
│   └── live_diagnosis_routes.py
├── services/
│   ├── sps_service.py
│   ├── violation_service.py
│   ├── analytics_service.py
│   ├── live_diagnosis_service.py
│   └── alert_service.py
└── schemas.py
```

### SPS Estimation Strategy

TikTok doesn't expose SPS via API. Frodo estimates it from data already available:

| SPS Metric | Frodo Data Source | Calculation |
|------------|-------------------|-------------|
| Negative Review Rate | Not available via API | Manual input or "check Seller Center" prompt |
| Non-Buyer Fault Return Rate | Returns module | non_buyer_fault_returns / total_orders (30-day window) |
| Seller Fault Cancellation Rate | Orders module | seller_cancelled / total_orders (30-day window) |
| On-Time Delivery Rate | Fulfillment module | shipped_on_time / total_shipped (30-day window) |
| IM Dissatisfaction Rate | Customer Service (Phase D) | CS performance metrics |
| After-Sales Handling Time | Returns module | avg hours to resolve returns (30-day window) |

5 of 6 metrics computed natively. Review rate allows manual input.

### Alert Thresholds

| Condition | Severity | Message |
|-----------|----------|---------|
| SPS < 3.5 | WARNING | Settlement tier at risk — will drop from Accelerated to Standard |
| SPS < 3.0 | CRITICAL | Shop health degrading — review returns and CS response time |
| Violation points >= 12 | WARNING | Losing campaign access at 12 points |
| Violation points >= 24 | CRITICAL | Livestream traffic reduction + new listing block imminent |
| 24h CS response rate < 85% | WARNING | Approaching 80% threshold — IM dissatisfaction will increase |
| OTDR < 90% | WARNING | On-time delivery rate degrading — check fulfillment pipeline |

### Database Models

**SpsSnapshot**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| date | DATE | |
| estimated_score | DECIMAL | 0.0–5.0 |
| return_rate | DECIMAL | Non-buyer fault |
| cancellation_rate | DECIMAL | Seller fault |
| otdr | DECIMAL | On-time delivery rate |
| im_dissatisfaction_rate | DECIMAL | From CS module |
| after_sales_handling_hours | DECIMAL | Avg resolution time |
| review_rate | DECIMAL | Nullable — manual input |
| settlement_tier_eligible | ENUM | introductory, standard, accelerated, express |

**ViolationRecord**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| violation_type | VARCHAR | Category of violation |
| points | INT | Points assessed |
| description | TEXT | |
| occurred_at | TIMESTAMP | |
| expires_at | TIMESTAMP | 90 days from occurred_at |
| resolved | BOOLEAN | |
| source | ENUM | manual, webhook |

**HealthAlert**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| alert_type | ENUM | sps_drop, violation_threshold, cs_degradation, otdr_warning |
| severity | ENUM | info, warning, critical |
| message | TEXT | |
| metric_name | VARCHAR | Which metric triggered |
| current_value | DECIMAL | |
| threshold_value | DECIMAL | |
| triggered_at | TIMESTAMP | |
| acknowledged_at | TIMESTAMP | Nullable |

**LiveSessionDiagnosis**:
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| platform_session_id | VARCHAR | |
| started_at | TIMESTAMP | |
| duration_minutes | INT | |
| peak_viewers | INT | |
| avg_viewers | INT | |
| products_pinned | INT | |
| orders_during_live | INT | |
| gmv_during_live | DECIMAL | |
| engagement_rate | DECIMAL | |
| traffic_source_breakdown | JSONB | `{organic: 60, paid: 30, affiliate: 10}` |

**UnifiedDailyMetrics** (denormalized rollup for fast dashboard queries):
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| workspace_id | UUID | FK |
| date | DATE | |
| total_gmv | DECIMAL | |
| order_count | INT | |
| return_count | INT | |
| cancellation_count | INT | |
| avg_order_value | DECIMAL | |
| affiliate_gmv | DECIMAL | |
| paid_gmv | DECIMAL | |
| organic_gmv | DECIMAL | |
| cs_response_rate | DECIMAL | |
| active_promotions | INT | |
| active_campaigns | INT | |

### Frontend Pages

`frontend/src/app/(dashboard)/shop-health/`

| Page | Route | Description |
|------|-------|-------------|
| Health Dashboard | `/shop-health` | SPS gauge (0-5), 6 metric cards, violation tracker, alert feed |
| Violation Tracker | `/shop-health/violations` | Current points (0-48), 90-day countdown, threshold markers, violation list |
| Alerts | `/shop-health/alerts` | Chronological alert feed, acknowledge/dismiss, fix action links |

`frontend/src/app/(dashboard)/analytics/` (enhance existing)

| Page | Route | Description |
|------|-------|-------------|
| Unified Analytics | `/analytics` | Revenue breakdown (organic/paid/affiliate), channel performance, cross-module KPIs |
| Trend Comparison | `/analytics/trends` | Overlay any two metrics over time |
| Export | `/analytics/export` | CSV/PDF for all analytics views |

`frontend/src/app/(dashboard)/live/diagnosis/`

| Page | Route | Description |
|------|-------|-------------|
| Session List | `/live/diagnosis` | Past LIVE sessions with quick stats |
| Session Detail | `/live/diagnosis/[id]` | Timeline: viewers, product pins, order spikes, engagement |

### Celery Workers
- `calculate_daily_sps` — daily at UTC 01:00, aggregate metrics into SpsSnapshot
- `calculate_daily_unified_metrics` — daily, roll up cross-module data
- `check_health_alerts` — every 2h, evaluate metrics against thresholds
- `sync_live_sessions` — after LIVE ends, generate diagnosis

---

## Cross-Module Data Flow

```
Commerce (existing) ─────┐
Promotions (Phase A) ─────┤
Finance (Phase B) ────────┤
GMV Max (Phase C) ────────┼──→ Shop Health (Phase F) ──→ Unified Dashboard
Customer Service (Phase D)┤                               ├── SPS Estimation
Affiliate (Phase E) ──────┤                               ├── Health Alerts
LIVE (existing) ──────────┘                               └── Analytics Rollup
```

### Inter-Phase Dependencies

| Consumer | Depends On | Data Needed |
|----------|-----------|-------------|
| GMV Max (C) | Finance (B) | Product margins for ROI recommendations |
| GMV Max (C) | Promotions (A) | Active promotions affecting GMV attribution |
| Shop Health (F) | Customer Service (D) | CS performance for SPS estimation |
| Shop Health (F) | Finance (B) | Revenue data, settlement tier |
| Shop Health (F) | Promotions (A) | Active promotion count |
| Shop Health (F) | GMV Max (C) | Ad spend, ROI |
| Shop Health (F) | Affiliate (E) | Affiliate GMV, creator count |
| Affiliate (E) | Finance (B) | Commission costs reconciliation |

**Build order must be:** A → B → C → D → E → F (each phase can reference prior phases)

---

## Migration Strategy

Each phase adds its own Alembic migration:
- `migrations/versions/XXXX_add_promotions_models.py`
- `migrations/versions/XXXX_add_finance_models.py`
- `migrations/versions/XXXX_add_gmvmax_models.py`
- `migrations/versions/XXXX_add_customer_service_models.py`
- `migrations/versions/XXXX_add_affiliate_models.py`
- `migrations/versions/XXXX_add_shop_health_models.py`

Existing `Promotion` model gets extended (not replaced) in Phase A migration.

## Testing Strategy

Each phase follows TDD:
1. Unit tests for all services (mocked TikTok API responses)
2. Integration tests for routes (TestClient + test DB)
3. Target 80%+ coverage per module

Current test count: 879. Expected addition: ~300-400 tests across all phases.

## Frontend Navigation Updates

Add to `frontend/src/config/navigation.ts`:

```typescript
// New nav items
{ name: 'Promotions', href: '/promotions', icon: TagIcon },
{ name: 'Finance', href: '/finance', icon: BanknotesIcon },
{ name: 'GMV Max', href: '/gmvmax', icon: RocketLaunchIcon },
{ name: 'Customer Service', href: '/customer-service', icon: ChatBubbleLeftRightIcon },
{ name: 'Engagement', href: '/engagement', icon: MegaphoneIcon },
{ name: 'Affiliate', href: '/affiliate', icon: UsersIcon },
{ name: 'Shop Health', href: '/shop-health', icon: HeartIcon },
```

Existing Analytics nav item gets enhanced with new sub-pages.

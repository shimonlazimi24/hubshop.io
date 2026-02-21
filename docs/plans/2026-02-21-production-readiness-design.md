# Frodo Production Readiness Design

**Date**: 2026-02-21
**Status**: Approved
**Approach**: Depth-First with parallel agents within phases

---

## Vision

Frodo is a production-ready SaaS platform — "one platform to rule them all" — that replaces the daily reality of TikTok teams jumping between Seller Center, Ads Manager, Creator tools, Business Center, and more. Every team member (e-commerce ops, marketers, content creators, agencies) works in one place.

**Target bar**: Production-ready for paying customers. Real users, real TikTok data, handles errors gracefully, has onboarding, supports multiple concurrent users.

**MVP user**: All-in-one from day 1. No narrowing scope — Seller, Creator, Advertiser, and Agency workflows all supported.

---

## Current State

- **Architecture**: Solid — 550+ tests, 237+ API endpoints, 8 phases complete, real API calls (not stubbed)
- **Modules**: 11 business domain modules, all with backend services + frontend pages
- **Infrastructure**: Docker Compose (5 services), Celery workers, Redis, PostgreSQL with RLS
- **Knowledge Base**: 60 markdown files documenting the entire TikTok ecosystem

### What Needs Work

1. **Auth model**: Developer-focused, needs social login (TikTok, Google, email)
2. **OAuth scopes**: Too narrow — only basic permissions, need full data access scopes
3. **App registration**: TikTok apps not yet registered on Partner Center / Dev Portal
4. **Module depth**: All 11 modules exist but are surface-level vs. what TikTok APIs offer
5. **UX**: No onboarding, rough error handling, no real-time sync status
6. **Connect flow**: Feels like developer setup, should feel like app installation

---

## Design

### 1. Auth Overhaul

**Sign up / Sign in options:**
- "Continue with TikTok" — TikTok Developer OAuth (`user.info.basic` scope) for identity
- "Continue with Google" — Google OAuth for identity
- "Continue with Email" — Existing email/password flow

**Implementation:**
- New `social_identity` table: `provider`, `provider_user_id`, `email`, `avatar`, `user_id` FK
- All three paths create/find a `User` record in Frodo's database
- First social login = account creation (no separate registration step)
- Subsequent logins = match by `provider + provider_user_id`
- Users can link multiple social identities to one account

**Key distinction:** "Login with TikTok" uses Developer OAuth for **identity only**. "Connect TikTok Shop" uses Shop OAuth for **data access** with full scopes. These are different flows.

### 2. Connect Pipeline Overhaul

**Connect page redesign:**
- Three platform cards: TikTok Shop, TikTok Account (Developer), TikTok Ads (Marketing)
- Each card shows: platform logo, data access description, connection status
- Connected cards show: account name, last sync time, sync health indicator

**OAuth scopes — expanded to full access:**

| Platform | Current Scopes | Production Scopes |
|----------|---------------|-------------------|
| Shop | Basic cipher list | All 13 API domains: products, orders, fulfillment, logistics, returns, finance, customer service, promotions, seller, supply chain, affiliate, event |
| Developer | `user.info.basic, video.list` | `user.info.basic, user.info.profile, user.info.stats, video.list, video.publish, video.upload, comment.list, comment.list.manage` |
| Marketing | Advertiser ID list | Full Marketing API: campaign management, audience, creative, pixel, conversion, reporting, catalog |

**Post-connect onboarding:**
1. User clicks "Connect TikTok Shop" -> TikTok OAuth with full scopes
2. After approval: "Syncing your data..." progress screen
3. Background: Celery kicks off initial full sync (products, orders, etc.)
4. User sees data appear in real-time (WebSocket or polling)
5. Complete: "Your TikTok Shop is connected! X products, Y orders, Z campaigns"

**Sync status dashboard:**
- Per-platform sync health (last sync, next sync, error count)
- Manual "Sync Now" button
- Sync log/history

### 3. Module Deepening Strategy

**Order**: Commerce -> Advertising -> Content/Creators -> Intelligence/LIVE/Messaging/Organic -> Production Hardening

#### Phase 1: Commerce Deep-Dive (Shop API — 203+ endpoints across 13 domains)

| Domain | Current | Needs Adding |
|--------|---------|-------------|
| Products | List/search | Create, update, activate/deactivate, inventory management, variants, images, categories, product certification |
| Orders | List/search | Order detail view, status updates, shipping labels, package management, split orders, buyer messaging |
| Fulfillment | Basic | Shipping providers, package tracking, pickup/dropoff, delivery instructions, SLA management |
| Logistics | Minimal | Warehouse management, shipping templates, delivery options, return addresses |
| Returns | Basic | Approve/reject with reasons, return shipping, refund processing, dispute resolution |
| Finance | Basic | Payment settlement, transaction history, statement downloads, fee breakdowns, withdrawal management |
| Customer Service | None | Conversation management, canned responses, escalation, satisfaction tracking |
| Promotions | Basic | Flash deals, coupons, bundle deals, discount codes, promotion analytics |
| Seller | None | Shop profile, shop score/health, policy compliance, seller verification |
| Supply Chain | None | Inventory forecasting, stock alerts, supplier management |
| Affiliate | Basic | Commission management, affiliate performance, sample management, marketplace listings |
| Events/Webhooks | 32 types | Ensure all 32 webhook types are handled and processed correctly |

#### Phase 2: Advertising Deep-Dive (Marketing API — hundreds of endpoints)

- **Campaign Builder**: Full creation wizard with targeting, budget, scheduling, bid strategies
- **Creative Management**: Upload/manage creatives, Spark Ads creative flow, dynamic creative optimization
- **Audience Builder**: Custom audiences, lookalike audiences, DMP integration, pixel-based retargeting
- **Automated Rules**: Pause if ROAS < X, increase budget if CTR > Y
- **GMV Max**: TikTok Shop-specific campaign type integration
- **Conversion Tracking**: Full pixel + events API setup, conversion attribution
- **Reporting Engine**: Custom report builder, scheduled exports, multi-dimension breakdown
- **Catalog Ads**: Product catalog -> dynamic product ads pipeline

#### Phase 3: Content & Creator Deep-Dive

**Content:**
- Full video analytics (views, likes, shares, comments over time)
- Comment management (read, reply, delete, filter)
- Content scheduling with calendar
- Hashtag research and trend integration
- Video performance benchmarking

**Creators:**
- Creator discovery with filters (niche, engagement rate, follower count, region)
- Campaign management (brief -> invite -> content review -> payment)
- Spark Ads authorization flow (creator authorizes brand to use their content)
- Creator performance reporting

#### Phase 4: Intelligence, LIVE, Messaging, Organic

- **Intelligence**: Deeper trend analysis, competitor tracking with historical data, research API queries with saved searches
- **LIVE**: Stream monitoring dashboard (via TikTokLive library), real-time analytics, commerce event tracking during streams
- **Messaging**: Conversation management, auto-reply rules, template messages, conversation assignment
- **Organic**: Brand mention monitoring, comment management, community engagement metrics

#### Phase 5: Production Hardening

- Proper error boundaries on every page
- Loading/skeleton states for all data-fetching components
- Empty states with CTAs
- Onboarding tour for new users
- Rate limit handling with user-visible retry
- WebSocket or SSE for real-time sync updates
- Monitoring dashboards (error rates, API health, sync status)
- Multi-tenant security audit
- Performance optimization (pagination, lazy loading, caching)

### 4. Execution Model

**Per-phase pattern:**
```
Research -> Gap Analysis -> Task List -> Parallel Implementation -> Review -> Verify
```

**Agent roles per phase:**
1. **Research agent**: Reads knowledge base, maps API endpoints to existing code, produces gap analysis
2. **Planner agent**: Takes gap analysis, produces detailed task list with dependencies
3. **Implementation agents** (parallel): Backend (models, services, routes), Frontend (pages, components), Tests (TDD)
4. **Code review agent**: Reviews each completed chunk
5. **Integration verification**: Full test suite, regression check

**Scope per session:** One phase at a time. Within a phase, parallel agents handle independent sub-modules.

---

## Operations Required (Outside Code)

These are manual/ops tasks the developer (Amit) needs to do:

1. **Register TikTok Shop app** on TikTok Shop Partner Center
   - Configure OAuth redirect URIs
   - Request all 13 API domain permissions
   - Get app_key and app_secret

2. **Register TikTok Developer app** on TikTok Developer Portal
   - Configure OAuth redirect URIs
   - Request all content/user scopes
   - Get client_key and client_secret

3. **Register TikTok Marketing API app** on TikTok Marketing portal
   - Configure OAuth redirect URIs
   - Request full Marketing API access
   - Get app_id and secret

4. **Set up Google OAuth** via Google Cloud Console
   - Create OAuth 2.0 credentials
   - Configure consent screen
   - Get client_id and client_secret

5. **Domain/SSL** for production deployment
6. **Database** (managed PostgreSQL for production)
7. **Redis** (managed Redis for production)

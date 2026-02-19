# TikTok & TikTok Shop Developer Knowledge Base

Comprehensive reference covering the **entire TikTok ecosystem**: Developer Platform, Shop API, Marketing/Business API, LIVE, Creator tools, and advertising products.

## Structure (60 files across 6 directories)

```
knowledge-base/
  tiktok-shop/ (9 files)
    01-getting-started.md           # Developer types, onboarding, app creation
    02-authentication.md            # OAuth, API signing, access tokens
    03-api-concepts.md              # Endpoints, parameters, versioning, rate limits
    04-webhooks.md                  # Event subscriptions, configuration, retry policy
    05-sdk-and-widgets.md           # Official SDKs (Java/Go/Node.js), Widgets
    06-regions-and-languages.md     # Supported markets, locales, currencies
    07-authorization-flow.md        # Complete OAuth flow, entity tags, shop_cipher
    08-webhook-events.md            # 32 webhook event types across 10 categories
    09-use-case-guides.md           # OMS, Connector, Affiliate, Engagement guides

  tiktok-developer/ (16 files)
    01-platform-overview.md         # API products, kits, getting started
    02-oauth-and-tokens.md          # OAuth 2.0 flow, token management, PKCE
    03-display-api.md               # User info, video listing, video query
    04-content-posting-api.md       # Video/photo posting, upload flow
    05-research-api.md              # Video query, user info for research
    06-share-kit.md                 # iOS/Android sharing to TikTok
    07-embed-and-oembed.md          # Video embedding, oEmbed API
    08-data-portability-api.md      # User data export, 8 scope types
    09-commercial-content-api.md    # Ad library queries, 31 countries
    10-webhooks.md                  # 4 event types, signature verification
    11-scopes-reference.md          # 20+ scopes across 5 categories
    12-rate-limits.md               # Per-endpoint limits, sliding window
    13-green-screen-kit.md          # Green screen background sharing
    14-mobile-sdk.md                # iOS/Android SDK setup and integration
    15-tiktok-minis.md              # Mini app framework within TikTok
    16-cross-platform-integration.md # TikTok + TikTok Shop integration analysis

  tiktok-business/ (8 files)
    01-marketing-api-overview.md    # Base URL, auth, account hierarchy, 15+ API categories
    02-campaign-management.md       # Campaigns, Ad Groups, Ads, Smart+, GMV Max, Reporting
    03-events-and-pixel.md          # Events API 2.0, Pixel, App SDK, Custom Conversions
    04-product-catalog.md           # Catalog CRUD, feeds, product sets, diagnostics
    05-spark-ads.md                 # Organic boosting, auth methods, TikTok One integration
    06-pangle.md                    # Ad network, publisher SDK, SKAN campaigns
    07-audience-network.md          # Audience management, targeting, lookalikes, segments
    08-business-center.md           # BC management, finance, billing, Business Messaging

  tiktok-live/ (5 files)
    01-live-platform-overview.md    # LIVE Events API, WebSocket, gifts, moderation
    02-live-commerce.md             # LIVE Shopping, product pinning, 8 markets
    03-effect-house.md              # AR effects, Script API (JS/TS), no external REST API
    04-creator-marketplace.md       # TTCM, creator discovery, campaign management
    05-sound-library.md             # Commercial Music Library, SoundOn

  tiktok-ecosystem/ (10 files)
    01-creative-center.md           # Trend intelligence, Top Ads, Discovery API
    02-symphony-ai.md               # AI video generation, Smart Creative/Text/Fix
    03-tiktok-one.md                # Unified creative platform, TTO API (20+ endpoints)
    04-promote.md                   # Self-serve in-app promotion tool
    05-branded-mission.md           # Crowdsourced creator advertising
    06-search-ads.md                # Keyword-based search ads, keyword management APIs
    07-local-services.md            # TikTok GO, location-based commerce
    08-capcut-integration.md        # ByteDance video editor, integration points
    09-pulse.md                     # Premium contextual advertising (top 4% content)
    10-additional-platforms.md      # 20+ additional APIs (Business Messaging, Organic, etc.)

  api-reference/ (13 files)
    seller-api.md                   # Shop info, global settings (2 endpoints)
    products-api.md                 # Product CRUD, categories, images (53 endpoints)
    orders-api.md                   # Order listing, details, external refs (7 endpoints)
    fulfillment-api.md              # Package management, shipping (24 endpoints)
    logistics-api.md                # Warehouses, delivery options (5 endpoints)
    finance-api.md                  # Statements, payments, withdrawals (6 endpoints)
    returns-refunds-api.md          # Returns, cancellations, refunds (13 endpoints)
    promotion-api.md                # Discounts, flash deals, coupons (9 endpoints)
    customer-service-api.md         # Buyer messaging, agent settings (10 endpoints)
    customer-engagement-api.md      # Marketing messages to past buyers (6 endpoints)
    affiliate-seller-api.md         # Creator discovery, collaborations (31 endpoints)
    affiliate-creator-api.md        # Showcase, video posting, orders (22 endpoints)
    affiliate-partner-api.md        # Campaign management, links (15 endpoints)
```

## Quick Reference

| Platform | Base URL | Auth Method | Token Expiry |
|----------|----------|-------------|--------------|
| TikTok Shop API | `https://open-api.tiktokglobalshop.com` | HMAC-SHA256 + `x-tts-access-token` | Access: 7d, Refresh: seller-set |
| TikTok Shop Auth | `https://auth.tiktok-shops.com` | Token exchange via HTTP GET | auth_code: 30 min |
| TikTok Developer API | `https://open.tiktokapis.com` | OAuth 2.0 Bearer token | Access: 24h, Refresh: 365d |
| TikTok Marketing API | `https://business-api.tiktok.com/open_api/v1.3/` | OAuth 2.0 long-term token | Long-term (no expiry) |

## Total API Coverage

- **TikTok Shop**: 203+ endpoints, 13 API domains, 32 webhook types
- **TikTok Developer**: 6 API products, 3 SDK kits, 4 webhook types, 20+ scopes
- **TikTok Marketing**: Hundreds of endpoints across 15+ categories (campaigns, ads, events, catalogs, audiences, reporting, Business Center, etc.)
- **TikTok LIVE**: LIVE Events API (partner-only), WebSocket real-time events
- **TTCM/TikTok One**: Creator discovery, campaign management, Spark Ads (20+ endpoints)
- **Effect House**: Desktop AR tool, Script API only (no REST API)
- **Ecosystem**: Creative Center, Symphony AI, Promote, Branded Mission, Search Ads, Pulse, Local Services, CapCut

## Cross-Platform Architecture

| Platform | Auth Server | Separate App Required |
|----------|------------|----------------------|
| TikTok Developer | `open.tiktokapis.com` | Yes |
| TikTok Shop | `auth.tiktok-shops.com` | Yes |
| TikTok Marketing | `business-api.tiktok.com` | Yes |

No cross-authentication exists between platforms. See `tiktok-developer/16-cross-platform-integration.md`.

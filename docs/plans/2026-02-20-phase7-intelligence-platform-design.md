# Phase 7: The Intelligence Platform — Design Document

**Date:** 2026-02-20
**Status:** Approved
**Scope:** SDK Modernization + Content Intelligence + LIVE Commerce

## Goal

Transform Frodo from a TikTok dashboard into a unified intelligence platform. Phase 7 expands the platform layer from 3 to 5 clients, adds a Content Intelligence module with aggregator pattern, introduces real-time LIVE Commerce monitoring, and wires 7 new capability areas into the advertising module via the official TikTok Business API SDK.

## Context

Research into 48+ GitHub repos (official and community) revealed significant capability gaps in Frodo. The `knowledge-base/Githubrepors` document catalogs these repos. Key findings:

- The official `tiktok-business-api-sdk` Python SDK covers 22 API classes — Frodo only uses ~5 endpoint groups
- The `TikTokResearchApi` wrapper provides public data access (video search, user profiles, comments, hashtags) that Frodo has zero access to
- The `TikTokLive` Python library enables real-time LIVE stream monitoring — Frodo's biggest feature gap
- Server-side event tracking (`pixel_track`/`pixel_batch`) is available via the SDK but not implemented

## 1. Platform Layer Expansion

### Current State (3 platforms)

| Client | Auth | Base URL |
|--------|------|----------|
| TikTokShopClient | HMAC-SHA256 | `open-api.tiktokglobalshop.com` |
| TikTokDeveloperClient | OAuth Bearer | `open.tiktokapis.com/v2` |
| TikTokMarketingClient | Access-Token header | `business-api.tiktok.com/open_api/v1.3` |

### Phase 7 State (5 platforms)

| Client | Auth | Source | Change |
|--------|------|--------|--------|
| TikTokShopClient | HMAC-SHA256 | Custom (unchanged) | None |
| TikTokDeveloperClient | OAuth Bearer | Custom (unchanged) | None |
| TikTokMarketingAdapter | Access-Token | Official `tiktok-business-api-sdk` | **Upgraded** |
| TikTokResearchClient | Client credentials OAuth | `TikTokResearchApi` package | **New** |
| TikTokLiveClient | WebSocket/protobuf | `TikTokLive` package | **New** |

### Marketing Client Upgrade

Replace `backend/tiktok/marketing/client.py` (raw httpx) with an adapter that wraps the official SDK:

- Adapter exposes the same `.get()`/`.post()` interface for backward compatibility
- PlatformGateway middleware (circuit breaker, rate limiter, retry) is preserved
- SDK provides typed request/response models, automatic pagination, error codes
- Adapter delegates to SDK where possible, falls back to raw HTTP for uncovered endpoints

### Research API Client (New)

- Package: `TikTokResearchApi` (official, `pip install TikTokResearchApi`)
- Auth: Client credentials OAuth (app_key + app_secret)
- Capabilities: `query_videos`, `query_user_info`, `query_video_comments`, `query_user_liked_videos`, `query_user_pinned_videos`, `query_user_followers`, `query_user_following`, `query_user_reposted_videos`
- Built-in rate limiting via `qps` parameter
- Automatic pagination with `fetch_all_pages=True`
- Requires Research API access approval from TikTok

### LIVE Client (New)

- Package: `TikTokLive` (community, `pip install TikTokLive`)
- Connection: WebSocket + protobuf (no official API needed)
- Events: Comment, Gift, Like, Follow, Share, Join, LiveEnd, Commerce Order (321 proto event types)
- Runs as persistent Celery worker per monitored stream

## 2. Intelligence Module

### Architecture

New module: `backend/modules/intelligence/`

Uses the **aggregator pattern** — a `DataSourceRegistry` abstracts multiple data sources behind a common `DataSource` protocol. Services query the registry, which routes to available sources.

```
DataSourceRegistry
├── ResearchApiSource (default, official)
├── MarketingApiSource (Creative Center trending data)
└── ScraperSource (optional, pluggable, disabled by default)
```

### Module Structure

```
backend/modules/intelligence/
├── __init__.py
├── routes/
│   ├── __init__.py
│   ├── trends.py              # Trending hashtags, sounds, products
│   ├── competitors.py         # Competitor tracking and analysis
│   ├── creators.py            # Creator scouting beyond TTCM
│   └── research.py            # Raw Research API queries
├── services/
│   ├── data_source_registry.py
│   ├── trend_service.py
│   ├── competitor_service.py
│   ├── creator_scout_service.py
│   └── content_analyzer.py    # Video subtitle extraction + analysis
├── sources/
│   ├── base.py                # DataSource protocol
│   ├── research_api_source.py
│   ├── marketing_api_source.py
│   └── scraper_source.py      # Optional enrichment
└── models.py
```

### API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/intelligence/trends/hashtags` | Trending hashtags with engagement data |
| GET | `/intelligence/trends/sounds` | Trending sounds/music |
| GET | `/intelligence/trends/products` | Trending shop products |
| POST | `/intelligence/competitors` | Add a competitor to track |
| GET | `/intelligence/competitors` | List tracked competitors |
| GET | `/intelligence/competitors/{id}` | Competitor detail |
| GET | `/intelligence/competitors/{id}/content` | Competitor's latest content |
| GET | `/intelligence/creators/search` | Scout creators by niche/metrics |
| GET | `/intelligence/creators/{id}` | Creator profile analysis |
| POST | `/intelligence/analyze/video` | Analyze a video (subtitles, metrics) |
| POST | `/intelligence/research/videos` | Raw Research API video query |
| POST | `/intelligence/research/users` | Raw Research API user query |

### Database Models

```
TrendSnapshot       — periodic snapshots (type, name, engagement_score, region, captured_at)
CompetitorTracker   — tracked accounts (username, platform, added_at, last_synced)
CompetitorContent   — competitor videos (tracker_id, video_id, description, metrics, published_at)
ResearchQuery       — saved queries (name, query_params, created_by, last_run)
```

## 3. LIVE Commerce Module

### Architecture

New module: `backend/modules/live/`

WebSocket-based real-time monitoring of TikTok LIVE streams. Events captured and stored for analytics.

### Module Structure

```
backend/modules/live/
├── __init__.py
├── routes/
│   ├── __init__.py
│   ├── streams.py         # Start/stop monitoring, list active
│   ├── events.py          # Query captured events
│   └── analytics.py       # Session analytics and summaries
├── services/
│   ├── stream_monitor_service.py
│   ├── event_service.py
│   └── live_analytics_service.py
└── models.py
```

### API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/live/streams/monitor` | Start monitoring a LIVE stream |
| DELETE | `/live/streams/{sessionId}/stop` | Stop monitoring |
| GET | `/live/streams` | List active monitored streams |
| GET | `/live/streams/{sessionId}` | Stream detail + status |
| GET | `/live/streams/{sessionId}/events` | Paginated event feed |
| GET | `/live/streams/{sessionId}/events/comments` | Comments only |
| GET | `/live/streams/{sessionId}/events/gifts` | Gifts only |
| GET | `/live/streams/{sessionId}/analytics` | Session analytics summary |
| GET | `/live/history` | Past LIVE sessions |

### Events Captured

| Event | Data | Use Case |
|-------|------|----------|
| Comment | user, text, timestamp | Sentiment, moderation |
| Gift | user, gift_name, value, repeat_count | Revenue tracking |
| Like | count, timestamp | Engagement spikes |
| Follow | user, timestamp | Conversion tracking |
| Share | user, platform, timestamp | Virality metrics |
| Join | user, timestamp | Viewer flow |
| Commerce Order | product, buyer, amount | LIVE selling revenue |

### Database Models

```
LiveSession     — monitored stream (unique_id, room_id, started_at, ended_at, status)
LiveEvent       — individual event (session_id, event_type, user_id, payload, timestamp)
LiveAnalytics   — computed summary (session_id, total_viewers, peak_concurrent, gift_revenue,
                   total_comments, total_shares, engagement_rate, top_commenters, computed_at)
```

### Celery Workers

| Worker | Trigger | Purpose |
|--------|---------|---------|
| `monitor_live_stream` | On-demand | Persistent WebSocket per stream |
| `compute_live_analytics` | On stream end | Compute session summary |
| `cleanup_stale_sessions` | Every 1h | Clean up disconnected sessions |

## 4. Advertising Module SDK Expansion

7 new capability areas wired into existing `backend/modules/advertising/`:

### Enhanced Existing Services

**AudienceService** (extended):
- Audience sharing between advertisers
- Audience overlap analysis
- File-based upload with SHA-256 PII hashing (email, phone, IDFA, GAID)
- Rule-based audience creation
- Sharing logs

**ReportService** (extended):
- Async report create/check/cancel for large datasets
- GMV Max campaign reports
- Smart+ material reports (breakdown + overview)

**CatalogService** (extended):
- Product feeds CRUD (create/get/update/delete)
- Product sets management
- Feed logs
- Event source binding/unbinding

**PixelService** (extended):
- `pixel_track()` — fire single server-side event
- `pixel_batch()` — fire batch server-side events
- 23 standard event types (AddToCart, Purchase, etc.)
- Automatic SHA-256 hashing of PII fields

### New Services

**CreativeService** (new):
- Creative portfolio CRUD
- AI-powered smart text generation
- Image editing operations
- Trending hashtag discovery via Marketing API
- Playable ad upload/save/validate/delete
- Asset sharing between accounts

**AutomationService** (new):
- Automated optimization rules for campaigns and ad groups
- Rule CRUD operations

**CommentService** (new):
- Ad comment listing, reply, hide/unhide, delete

## 5. Frontend Pages

### New: Intelligence Section

```
frontend/src/app/(dashboard)/intelligence/
├── page.tsx                       # Intelligence hub overview
├── trends/
│   ├── page.tsx                   # Trending hashtags, sounds, products
│   └── [type]/page.tsx            # Detail view per trend type
├── competitors/
│   ├── page.tsx                   # Tracked competitors list
│   ├── add/page.tsx               # Add competitor to track
│   └── [id]/page.tsx              # Competitor detail + content feed
├── creators/
│   ├── page.tsx                   # Creator scouting search
│   └── [id]/page.tsx              # Creator profile analysis
└── research/
    └── page.tsx                   # Research API query builder
```

### New: LIVE Section

```
frontend/src/app/(dashboard)/live/
├── page.tsx                       # Active streams overview
├── monitor/page.tsx               # Start monitoring form
├── [sessionId]/
│   ├── page.tsx                   # Real-time event feed
│   └── analytics/page.tsx         # Post-stream analytics
└── history/page.tsx               # Past LIVE sessions
```

### Expanded: Ads Section

```
frontend/src/app/(dashboard)/ads/
├── creatives/page.tsx             # Creative portfolio management
├── automation/page.tsx            # Automated optimization rules
├── events/page.tsx                # Server-side event tracking dashboard
└── comments/page.tsx              # Ad comment management
```

### Sidebar Navigation

Add top-level sections:
- **Intelligence** (icon: lightbulb) — Trends, Competitors, Creators, Research
- **LIVE** (icon: radio) — Active Streams, History

## 6. Celery Workers Summary

| Worker | Schedule | Module |
|--------|---------|--------|
| `sync_trends` | Every 4h | Intelligence |
| `sync_competitor_content` | Every 6h | Intelligence |
| `monitor_live_stream` | On-demand | LIVE |
| `compute_live_analytics` | On stream end | LIVE |
| `cleanup_stale_sessions` | Every 1h | LIVE |
| `sync_creative_portfolios` | Every 12h | Advertising |

## 7. Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `tiktok-business-api-sdk` | Latest | Official Marketing API SDK |
| `TikTokResearchApi` | Latest | Official Research API wrapper |
| `TikTokLive` | Latest | LIVE stream WebSocket client |

## 8. GitHub Repos Leveraged

| Repo | How Used |
|------|----------|
| `tiktok/tiktok-business-api-sdk` | Direct dependency — Marketing client adapter |
| `tiktok/tiktok-research-api-wrapper` | Direct dependency — Research API client |
| `isaackogan/TikTokLive` | Direct dependency — LIVE stream monitoring |
| `bellingcat/tiktok-hashtag-analysis` | Pattern reference — hashtag co-occurrence analysis |
| `stel-oberts/tiktok-trending-creators-insights` | Pattern reference — creator scouting metrics |
| `stape-io/tiktok-tag` | Pattern reference — S2S event schema (23 event types) |
| `aws-samples/uploading-audiences-to-tiktok-ads` | Pattern reference — audience upload + SHA-256 hashing |
| `Seym0n/tiktok-mcp` | Pattern reference — video subtitle extraction approach |

## 9. Metrics

| Metric | Before Phase 7 | After Phase 7 |
|--------|----------------|---------------|
| Platform clients | 3 | 5 |
| Backend modules | 7 | 9 |
| API endpoints | ~147 | ~180+ |
| DB models | ~23 | ~33 |
| Celery workers | ~8 | ~14 |
| Frontend pages | ~30 | ~45 |
| Tests | 253 | TBD (target: 340+) |

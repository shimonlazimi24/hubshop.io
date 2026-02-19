# TikTok Marketing API - Comprehensive Overview

## What It Is

The **TikTok Marketing API** (also called TikTok for Business API) is TikTok's programmatic interface for managing advertising campaigns, creatives, audiences, reporting, and measurement across TikTok's advertising ecosystem. It enables developers and advertisers to automate ad management at scale.

## Base URL

```
https://business-api.tiktok.com/open_api/v1.3/
```

- **Current Version**: v1.3 (migrated from v1.2)
- **Documentation Portal**: https://business-api.tiktok.com/portal/docs
- **Alternative Portal**: https://ads.tiktok.com/marketing_api/docs

## Authentication

### OAuth 2.0 Flow

TikTok uses a custom OAuth 2.0 flow for authentication:

1. **Developer Registration**: Register at https://ads.tiktok.com/marketing_api/apps/
2. **Create Developer App**: Obtain `app_id` and `secret`
3. **Authorization**: Redirect advertisers to TikTok's authorization URL to grant permissions
4. **Token Exchange**: Exchange `auth_code` for a long-term `access_token`

### Token Types

| Token Type | Endpoint | Expiry | Notes |
|---|---|---|---|
| Long-term Access Token | `POST /v1.3/oauth2/access_token/` | Does not expire | Invalidated only when advertiser revokes or via API |
| Short-term Access Token | `POST /v1.3/oauth2/access_token_v2/` | Limited validity | Requires renewal |

### Authentication Endpoint

```bash
curl --location -request POST 'https://business-api.tiktok.com/open_api/v1.3/oauth2/access_token/' \
  --header 'Content-Type: application/json' \
  --data '{
    "app_id": "{{app_id}}",
    "secret": "{{secret}}",
    "auth_code": "{{auth_code}}"
  }'
```

### Response

```json
{
  "message": "OK",
  "code": 0,
  "data": {
    "access_token": "xxxxxxxxxxxxx",
    "scope": [4],
    "advertiser_ids": ["123456789", "123456781"]
  },
  "request_id": "2020042715295501023125104093250"
}
```

### Using Access Tokens

All API calls require the `Access-Token` header:

```
Access-Token: {your_access_token}
```

### Token Management Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/oauth2/access_token/` | POST | Generate long-term access token |
| `/v1.3/oauth2/access_token_v2/` | POST | Generate short-term access token |
| `/v1.3/oauth2/renew_token/` | POST | Renew short-term access token |
| `/v1.3/oauth2/revoke_token/` | POST | Revoke long-term access token |
| `/v1.3/oauth2/revoke_token_v2/` | POST | Revoke short-term access token |
| `/v1.3/oauth2/advertiser/get/` | GET | Get authorized advertiser accounts |

## Rate Limits

TikTok enforces per-app, per-endpoint rate limits. Rate limit details are provided in the response headers. Key points:

- Rate limits vary by endpoint category
- Higher-traffic endpoints (reporting, campaign management) have stricter limits
- Sandbox accounts have separate (typically lower) rate limits
- The `X-Tt-Ads-Throttle` response header warns of near-limit conditions
- Reporting endpoints have a 20,000 ad truncation limit for synchronous reports

## API Versioning

| Version | Status | Path Prefix |
|---|---|---|
| v1.3 | Current (recommended) | `/open_api/v1.3/` |
| v1.2 | Deprecated (migration required) | `/open_api/v1.2/` |

### Key v1.3 Changes from v1.2
- ID fields changed from `number` to `string` types
- `filters` parameter renamed to `filtering`
- `lifetime` replaced by `query_lifetime`
- New parameters: `bc_id`, `enable_total_metrics`, `advertiser_ids`
- New response header: `X-Tt-Ads-Throttle`

## Account Structure

TikTok's advertising hierarchy:

```
Business Center (BC)
  |-- Ad Accounts (Advertisers)
       |-- Campaigns
            |-- Ad Groups
                 |-- Ads (Creatives)
```

## Complete API Categories

The Marketing API spans the following major domains:

### 1. Campaign Management
- Campaign CRUD operations
- Ad Group CRUD operations
- Ad CRUD operations
- Status management (enable/disable/delete)
- Budget management
- Smart+ Campaigns (automated)
- Upgraded Smart+ Campaigns
- GMV Max Campaigns (e-commerce)
- Reach & Frequency campaigns
- Search Ads campaigns
- Dedicated Campaigns (iOS 14+/SKAN)
- Super Split Tests

### 2. Creative Management
- Video upload and management
- Image upload and management
- Music upload and management
- Instant Pages (landing pages)
- Playable Ads
- Creative Portfolios
- Smart Creative (AI-generated variations)
- Creative Tools (Smart Fix, Smart Text, CTA recommendations)
- Creative Fatigue Detection
- Creative Reports and Insights

### 3. Audience Management
- Custom Audiences (customer file upload)
- Rule-based Audiences
- Lookalike Audiences
- Saved Audiences
- Audience Segments (streaming API)
- Audience Insights (potential audience analysis, overlap)
- Audience sharing between ad accounts

### 4. Reporting
- Synchronous reports (up to 20,000 ads)
- Asynchronous reports (no truncation)
- Basic reports (campaign/ad group/ad level)
- Audience reports (demographic breakdowns)
- Playable ad reports
- DSA (Dynamic Showcase Ads) reports
- Business Center reports
- GMV Max ads reports
- Creative basic reports
- Video Insights reports

### 5. Ad Measurement (Events & Pixel)
- Events API 2.0 (Web, App, Offline, CRM)
- Events API 1.0 (legacy)
- TikTok Pixel management
- Custom Conversions
- Events API Gateway

### 6. Business Center Management
- BC creation and management
- Member management (invite, update, delete)
- Partner management
- Asset management (ad accounts, pixels, TikTok accounts)
- Asset Groups
- Billing Groups
- Payment Portfolios
- Invoices
- Finance (balance, transactions, budgets)

### 7. Catalog Management
- Catalog CRUD
- Product management (upload, update, delete)
- Product Sets
- Feeds (scheduled product imports)
- Catalog Videos
- Catalog Diagnostics
- Catalog Insights (trending products/categories)
- Event Source binding

### 8. Identity & Spark Ads
- Identity creation and management
- Spark Ads post authorization
- Spark Ads Recommendation API
- Post management under identities

### 9. Organic API
- Accounts API (profile insights, post management, comments)
- Mentions API (brand monitoring)
- Webhooks (post publishing events, comment events)
- URL property management

### 10. TikTok One API (Creator Marketplace)
- Creator discovery and insights
- Campaign creation and management
- Content linking
- Spark Ads authorization from creators
- Brand Profiles

### 11. Discovery API
- Popular hashtags and trends
- Trending videos
- Commercial Music Library
- Trending search keywords

### 12. Business Messaging API
- Direct messages
- Automatic messages
- Welcome messages
- Comment-to-Message functionality
- Webhooks for messaging events

### 13. Tools & Utilities
- Location/geography targeting
- Interest and behavior categories
- Device targeting (OS, models, carriers)
- Contextual targeting tags
- Brand safety settings
- Bid and budget recommendations
- URL verification
- Negative keywords

### 14. Automated Rules
- Rule creation and management
- Rule binding to campaigns/ad groups
- Rule execution results

### 15. Lead Generation
- Lead download and export
- Instant Form management
- Test leads
- CRM event postback

### 16. Media Mix Modeling
- MMM data requests
- Data download

## SDK Availability

- **Postman Collection**: Official Postman collection for API testing
- **API Playground**: Interactive endpoint testing in the documentation portal
- **Sandbox Accounts**: Testing environment without real ad spend
- **Events API Gateway**: Self-hosted gateway for event tracking
- **TikTok App Events SDK**: Native SDKs for Android, iOS, Unity
- **Instant Page Editor SDK**: For building custom landing pages

## Advertising Objectives

The API supports creating campaigns with these objectives:

| Objective | Description |
|---|---|
| Traffic | Drive visits to a destination |
| App Promotion | Drive app installs and engagement |
| Website Conversions | Drive specific website actions |
| Lead Generation | Collect leads via forms or messages |
| Community Interaction | Grow followers and engagement |
| Reach & Frequency | Guaranteed reach at fixed frequency |
| Sales / GMV Max | E-commerce driven sales |
| Video Shopping | Shoppable video ads |
| Catalog Ads | Dynamic product ads from catalog |

## Campaign Types

| Type | Description |
|---|---|
| Manual Campaign | Traditional campaign with full manual control |
| Smart+ Campaign | AI-optimized campaign (limited control) |
| Upgraded Smart+ Campaign | Next-gen AI campaign with ad groups and ads |
| GMV Max Campaign | E-commerce gross merchandise value optimization |
| Reach & Frequency | Reservation-based guaranteed delivery |
| Dedicated Campaign | iOS 14+ SKAN dedicated campaigns |
| Search Ads Campaign | TikTok search result advertising |

## Request/Response Format

- **Content-Type**: `application/json`
- **Method**: GET for read operations, POST for write operations
- **Response Format**: JSON with `code`, `message`, `request_id`, `data` fields
- **Pagination**: `page` and `page_size` parameters (max 1,000 per page)
- **Error Codes**: Documented in Appendix - Return Codes

## Getting Started Workflow

1. Create a TikTok for Business account
2. Register as a developer at the Marketing API portal
3. Create a developer app (obtain `app_id` and `secret`)
4. Configure authorization redirect URLs
5. Have advertisers authorize your app
6. Exchange auth code for access token
7. Make API calls with the access token
8. (Optional) Use sandbox accounts for testing

## Key Documentation Links

| Resource | URL |
|---|---|
| API Documentation | https://business-api.tiktok.com/portal/docs |
| API Playground | Available in documentation portal |
| Service Status | API Service Status Page in portal |
| Return Codes | Appendix in documentation |
| Enumerations | Appendix in documentation |
| Permission Scopes | Appendix in documentation |

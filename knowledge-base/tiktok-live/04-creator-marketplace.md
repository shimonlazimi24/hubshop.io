# TikTok Creator Marketplace (TTCM)

## Overview

The **TikTok Creator Marketplace (TTCM)** is TikTok's official platform for connecting brands and advertisers with TikTok creators for paid partnership campaigns. It serves as a matchmaking and campaign management platform where brands can discover creators, negotiate partnerships, manage campaigns, and track performance metrics.

**Portal URL:** `https://creatormarketplace.tiktok.com/`

**Also known as:** TTCM, TikTok Creator Marketplace

---

## Purpose

- Enable brands to discover and collaborate with TikTok creators
- Provide data-driven creator discovery based on audience demographics and performance metrics
- Streamline campaign management from invitation to payment
- Ensure transparency and compliance for branded content
- Provide campaign analytics and ROI measurement

---

## Key Features

### For Brands/Advertisers

| Feature | Description |
|---------|-------------|
| Creator Discovery | Search and filter creators by niche, audience demographics, engagement rate, location, follower count |
| Audience Insights | View creator audience demographics (age, gender, location, interests) |
| Campaign Management | Create, manage, and track branded content campaigns |
| Creator Invitation | Invite specific creators to participate in campaigns |
| Content Review | Review and approve creator content before publication |
| Performance Analytics | Track campaign metrics (views, engagement, reach, conversions) |
| Payment Management | Handle creator payments through the platform |
| Branded Content Toggle | Automatic disclosure of paid partnerships |
| Multi-market Campaigns | Run campaigns across multiple countries |

### For Creators

| Feature | Description |
|---------|-------------|
| Brand Partnerships | Receive invitations from brands for paid collaborations |
| Campaign Applications | Apply to open brand campaigns |
| Portfolio Showcase | Display content portfolio and audience metrics to brands |
| Payment Processing | Receive payments through the platform |
| Content Management | Submit content for brand review and approval |
| Performance Data | Share verified audience and engagement data with brands |

---

## TTCM API

### TikTok Creator Marketplace API

TikTok provides an API for the Creator Marketplace aimed at **brands, agencies, and marketing platforms** to programmatically interact with TTCM.

### Base URL

```
https://business-api.tiktok.com/open_api/
```

**Note:** The TTCM API is part of the **TikTok Marketing API** / **TikTok Business API** ecosystem, not the TikTok Developer Platform (`open.tiktokapis.com`).

### Authentication

| Aspect | Details |
|--------|---------|
| Auth method | OAuth 2.0 Bearer token |
| Token type | Business access token (via TikTok Marketing API auth) |
| Portal | TikTok For Business / TikTok Marketing API |
| Header | `Access-Token: {access_token}` |

### TTCM API Endpoints

#### Creator Discovery

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ttcm/creator/search/` | Search for creators with filters |
| GET | `/ttcm/creator/info/` | Get detailed creator profile and metrics |
| GET | `/ttcm/creator/audience/` | Get creator audience demographics |

#### Campaign Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ttcm/campaign/create/` | Create a new campaign |
| GET | `/ttcm/campaign/list/` | List campaigns |
| GET | `/ttcm/campaign/info/` | Get campaign details |
| PUT | `/ttcm/campaign/update/` | Update campaign settings |

#### Creator Invitation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ttcm/campaign/invite/creator/` | Invite creators to a campaign |
| GET | `/ttcm/campaign/invite/status/` | Check invitation status |
| GET | `/ttcm/campaign/creators/` | List creators in a campaign |

#### Content & Reporting

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ttcm/campaign/report/` | Get campaign performance report |
| GET | `/ttcm/creator/report/` | Get creator performance in campaign |
| GET | `/ttcm/content/info/` | Get branded content details |

### Request Format

```http
POST https://business-api.tiktok.com/open_api/v1.3/ttcm/creator/search/
Content-Type: application/json
Access-Token: {access_token}

{
  "advertiser_id": "1234567890",
  "filters": {
    "min_followers": 10000,
    "max_followers": 1000000,
    "creator_country": ["US", "UK"],
    "content_categories": ["beauty", "fashion"],
    "engagement_rate_min": 3.0
  },
  "page": 1,
  "page_size": 20
}
```

### Response Format

```json
{
  "code": 0,
  "message": "OK",
  "data": {
    "creators": [
      {
        "creator_id": "abc123",
        "nickname": "Creator Name",
        "avatar_url": "https://...",
        "follower_count": 150000,
        "engagement_rate": 5.2,
        "avg_views": 50000,
        "content_categories": ["beauty", "fashion"],
        "country": "US",
        "audience_demographics": {
          "gender": {"male": 30, "female": 65, "other": 5},
          "age": {"18-24": 40, "25-34": 35, "35-44": 15, "45+": 10},
          "top_countries": [{"country": "US", "percentage": 60}]
        }
      }
    ],
    "page_info": {
      "total": 500,
      "page": 1,
      "page_size": 20
    }
  }
}
```

---

## Creator Discovery Filters

| Filter | Type | Description |
|--------|------|-------------|
| `min_followers` | integer | Minimum follower count |
| `max_followers` | integer | Maximum follower count |
| `creator_country` | array[string] | Creator's country (ISO codes) |
| `audience_country` | array[string] | Audience country distribution |
| `content_categories` | array[string] | Content category/niche |
| `engagement_rate_min` | float | Minimum engagement rate (%) |
| `engagement_rate_max` | float | Maximum engagement rate (%) |
| `audience_gender` | string | Dominant audience gender |
| `audience_age` | array[string] | Target audience age ranges |
| `creator_gender` | string | Creator's gender |
| `has_ecommerce` | boolean | Creator has e-commerce features enabled |
| `creator_type` | string | Individual, brand, or media creator |

---

## Campaign Types

| Type | Description |
|------|-------------|
| Brand Awareness | Increase brand visibility through creator content |
| Product Launch | Promote new products via creator reviews/demos |
| Hashtag Challenge | Creator-led hashtag challenge campaigns |
| LIVE Shopping | Creators promote products during LIVE streams |
| App Install | Drive app downloads through creator content |
| Traffic | Drive website traffic through creator links |
| Engagement | Boost engagement metrics through creator content |

---

## Campaign Workflow

### Brand Workflow

```
1. Create campaign (set objectives, budget, timeline, requirements)
2. Search and discover creators matching criteria
3. Invite selected creators to the campaign
4. Negotiate terms (deliverables, pricing, timeline)
5. Creators accept and create content
6. Review and approve creator content
7. Creators publish approved content
8. Monitor campaign performance
9. Process creator payments
```

### Creator Workflow

```
1. Receive campaign invitation or browse open campaigns
2. Review campaign brief and requirements
3. Accept or decline invitation
4. Create content per campaign brief
5. Submit content for brand review
6. Publish approved content with branded content disclosure
7. Receive payment upon completion
```

---

## Branded Content Disclosure

TikTok requires disclosure for paid partnerships:

| Feature | Description |
|---------|-------------|
| `brand_content_toggle` | Flag content as branded/sponsored |
| `brand_organic_toggle` | Flag organic brand mentions |
| Automatic disclosure | "Paid partnership" label on video |
| Content Posting API integration | Set via `brand_content_toggle` field when posting via API |

This integrates with the TikTok Developer Platform's Content Posting API:

```json
{
  "post_info": {
    "brand_content_toggle": true,
    "brand_organic_toggle": false
  }
}
```

See `../tiktok-developer/04-content-posting-api.md` for details.

---

## TTCM + TikTok Shop Integration

TTCM integrates with TikTok Shop for commerce-driven campaigns:

| Integration | Description |
|-------------|-------------|
| Affiliate Campaigns | Brands can create affiliate campaigns through TTCM linked to TikTok Shop products |
| Product Samples | Send product samples to creators for review |
| Commission Tracking | Track sales attributed to TTCM campaigns |
| LIVE Shopping | TTCM creators can conduct LIVE shopping sessions |

---

## Developer Access Requirements

### To Access TTCM API

1. **TikTok For Business account**: Required (create at `ads.tiktok.com`)
2. **Marketing API access**: Apply for TikTok Marketing API at `business-api.tiktok.com`
3. **TTCM API whitelist**: Additional approval required for TTCM-specific endpoints
4. **Advertiser account**: Must have an active TikTok Ads advertiser account
5. **Agency/partner status**: Some endpoints require agency or marketing partner status

### Approval Process

```
1. Register at TikTok For Business (ads.tiktok.com)
2. Create a developer app on the Marketing API portal
3. Request TTCM API access (requires justification and use case)
4. Complete business verification
5. Receive API credentials upon approval
```

### Access Tiers

| Tier | Access Level | Requirements |
|------|-------------|--------------|
| Standard | Basic creator search and campaign management | TikTok For Business account |
| Advanced | Full API access including audience insights | Marketing API partnership |
| Enterprise | Custom integrations and bulk operations | Agency/enterprise partnership agreement |

---

## Rate Limits

| Endpoint Category | Rate Limit |
|-------------------|------------|
| Creator Search | 100 requests/minute |
| Campaign Management | 60 requests/minute |
| Reporting | 30 requests/minute |

**Note:** Rate limits may vary based on access tier and partnership level.

---

## SDK Availability

### Official SDKs

There is no standalone TTCM SDK. TTCM API access is through the **TikTok Marketing API SDK**:

| Language | Availability |
|----------|-------------|
| Python | TikTok Business API Python SDK |
| Java | TikTok Business API Java SDK |
| PHP | TikTok Business API PHP SDK |
| Go | Community-maintained |

### Marketing API SDK (includes TTCM)

```bash
pip install tiktok-business-api
```

```python
from tiktok_business_api import Client

client = Client(access_token="your_access_token")

# Search creators
creators = client.ttcm.creator_search(
    advertiser_id="1234567890",
    filters={
        "min_followers": 10000,
        "content_categories": ["beauty"]
    }
)
```

---

## Key Limitations

1. **Restricted API access**: TTCM API requires whitelist approval; not openly available
2. **Brand-side only**: API is primarily for brands/agencies; creators access TTCM through the web portal only
3. **No creator-side API**: Creators cannot programmatically manage their TTCM profiles or invitations
4. **Separate from TikTok Developer Platform**: Different auth system from `open.tiktokapis.com`
5. **Separate from TikTok Shop API**: Different auth system from `partner.tiktokshop.com`
6. **Limited markets**: TTCM availability varies by country
7. **Minimum requirements for creators**: Creators need minimum follower counts (typically 10,000+) to be listed on TTCM
8. **No real-time data**: Analytics data may have delays of 24-48 hours
9. **Campaign content ownership**: Content created through TTCM campaigns has specific usage rights governed by the agreement

## Related Documentation

- TikTok Developer Platform: `../tiktok-developer/01-platform-overview.md`
- Content Posting API (branded content toggle): `../tiktok-developer/04-content-posting-api.md`
- Commercial Content API: `../tiktok-developer/09-commercial-content-api.md`
- LIVE Commerce: `./02-live-commerce.md`
- Affiliate Seller API: `../api-reference/affiliate-seller-api.md`
- Cross-Platform Integration: `../tiktok-developer/16-cross-platform-integration.md`

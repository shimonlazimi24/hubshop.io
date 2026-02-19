# TikTok Spark Ads API

## Overview

Spark Ads is TikTok's native ad format that allows advertisers to boost existing organic TikTok posts as ads. Unlike standard in-feed ads that are created from scratch, Spark Ads use real TikTok videos from either the advertiser's own account or from authorized creators. This preserves the organic look and feel while gaining paid reach, and all engagement (likes, comments, shares) accrues to the original post.

## Key Benefits

- **Authentic engagement**: Interactions go to the original organic post
- **Social proof**: Maintains existing likes, comments, and shares
- **Creator partnerships**: Boost creator content with their authorization
- **Higher engagement rates**: Native format typically outperforms standard ads
- **Full-funnel support**: Works with all advertising objectives
- **Duet/Stitch enabled**: Users can interact with Spark Ads like organic content

## Base URL

```
https://business-api.tiktok.com/open_api/v1.3/
```

## Authentication

Standard Marketing API `Access-Token` header.

---

## How Spark Ads Work

### Two Authorization Methods

#### 1. Using Your Own TikTok Account

Link your business TikTok account to your ad account, then use your own organic posts as ads.

**Flow:**
1. Link TikTok account to ad account (via Business Center or API)
2. Create an identity with `identity_type: TT_USER`
3. Select posts from the linked account
4. Create ads using those posts

#### 2. Using Creator Authorization (Auth Code)

Creators generate an authorization code for their posts, which advertisers use to run those posts as ads.

**Flow:**
1. Creator goes to their TikTok post settings and generates an auth code
2. Creator shares the auth code with the advertiser
3. Advertiser applies the auth code via API
4. Advertiser creates Spark Ads using the authorized post

---

## Spark Ads Using Authorized Posts

### Core Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/tt_video/info/` | GET | Get info about a Spark Ad post |
| `/v1.3/tt_video/authorize/` | POST | Apply an authorization code |
| `/v1.3/tt_video/list/` | GET | Get list of Spark Ad posts |
| `/v1.3/tt_video/unbind/` | POST | Unbind a Spark Ad post |

### Applying an Authorization Code

```json
POST /v1.3/tt_video/authorize/

{
  "advertiser_id": "advertiser_id",
  "auth_code": "creator_authorization_code"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "OK",
  "data": {
    "item_id": "tiktok_post_id"
  }
}
```

### Getting Spark Ad Post Info

```
GET /v1.3/tt_video/info/?advertiser_id=xxx&item_id=xxx
```

Returns post details including:
- Post ID, video URL, thumbnail
- Creator info
- Authorization status and expiry
- Available actions (can use as ad, etc.)

### Auth Code Properties

| Property | Details |
|---|---|
| Validity | 30 days by default (can be extended) |
| Scope | Authorizes specific post(s) for ad use |
| Revocation | Creator can revoke at any time |
| Multiple use | Same code can be used by one advertiser |

---

## Spark Ads Recommendation API

TikTok provides an AI-powered recommendation engine that suggests high-performing organic posts suitable for Spark Ads.

### Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/spark_ads/recommendation/business_account/` | GET | Get recommendations for a Business Account |
| `/v1.3/spark_ads/recommendation/tto_account/` | GET | Get recommendations for a TTO (TikTok One) account |

### Rate Limits

The Spark Ads Recommendation API has its own rate limits, separate from the main Marketing API. Refer to the documentation for current limits.

### All-in-One Spark Ads Creation

Create a campaign, ad group, and Spark Ad in a single API call:

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/spark_ads/all_in_one/create/` | POST | Create campaign + ad group + Spark Ad in one step |

This endpoint simplifies the Spark Ads creation flow by combining three operations. It uses default settings for campaign and ad group parameters.

#### Default Settings for All-in-One

- Campaign objective: Configurable
- Bidding strategy: Lowest cost
- Placement: Automatic
- Targeting: Configurable or automatic
- Budget: Configurable

---

## Creating Spark Ads via Campaign Management API

### Step 1: Set Up Identity

The identity determines which TikTok account appears on the ad.

```json
POST /v1.3/identity/create/

{
  "advertiser_id": "advertiser_id",
  "display_name": "Brand Name",
  "profile_image_id": "image_id"
}
```

Or use an existing TikTok account identity:

```
GET /v1.3/identity/get/?advertiser_id=xxx&identity_type=TT_USER
```

### Step 2: Get Available Posts

```
GET /v1.3/identity/video/get/?advertiser_id=xxx&identity_id=xxx&identity_type=TT_USER
```

### Step 3: Create Campaign

```json
POST /v1.3/campaign/create/

{
  "advertiser_id": "advertiser_id",
  "campaign_name": "Spark Ads Campaign",
  "objective_type": "TRAFFIC",
  "budget_mode": "BUDGET_MODE_DAY",
  "budget": 100
}
```

### Step 4: Create Ad Group

```json
POST /v1.3/adgroup/create/

{
  "advertiser_id": "advertiser_id",
  "campaign_id": "campaign_id",
  "adgroup_name": "Spark Ads Group",
  "placement_type": "PLACEMENT_TYPE_AUTOMATIC",
  // ... targeting, bidding, schedule settings
}
```

### Step 5: Create Spark Ad

```json
POST /v1.3/ad/create/

{
  "advertiser_id": "advertiser_id",
  "adgroup_id": "adgroup_id",
  "ad_name": "Spark Ad",
  "ad_format": "SINGLE_VIDEO",
  "identity_id": "identity_id",
  "identity_type": "AUTH_CODE",       // or "TT_USER" for own posts
  "tiktok_item_id": "organic_post_id",
  "call_to_action": "LEARN_MORE",
  "landing_page_url": "https://example.com"
}
```

### Identity Types for Spark Ads

| Type | Description | Use Case |
|---|---|---|
| `TT_USER` | Own TikTok account linked to ad account | Boosting your own posts |
| `AUTH_CODE` | Creator-authorized via auth code | Boosting creator posts |
| `CUSTOMIZED_USER` | Custom identity (display name + image) | Standard ads (not Spark Ads) |

---

## Organic API for Ad Authorization

The Organic API provides endpoints for managing ad authorization on TikTok posts from the account owner's perspective.

### Ad Authorization Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `POST /v1.3/business/post/ad_auth/update/` | POST | Enable/disable ad authorization for a post |
| `POST /v1.3/business/post/ad_auth/extend/` | POST | Extend authorization validity period |
| `GET /v1.3/business/post/ad_auth/status/` | GET | Get authorization status of a post |
| `POST /v1.3/business/post/ad_auth/delete/` | POST | Delete authorization code of a post |

### Enabling Ad Authorization

```json
POST /v1.3/business/post/ad_auth/update/

{
  "business_id": "business_account_id",
  "item_id": "post_id",
  "ad_auth_enabled": true
}
```

---

## TikTok One (Creator Marketplace) Integration

For larger-scale creator partnerships, the TikTok One API (formerly TikTok Creator Marketplace / TCM) provides:

### Creator Discovery

| Endpoint | Purpose |
|---|---|
| `GET /v1.3/tto/creator/discover/` | Discover creators matching criteria |
| `GET /v1.3/tto/creator/ranking/` | Get top creator rankings |
| `GET /v1.3/tto/creator/insight/` | Get creator performance insights |

### Campaign Management (Creator Marketplace)

| Endpoint | Purpose |
|---|---|
| `POST /v1.3/tto/campaign/create/` | Create a TTO campaign |
| `POST /v1.3/tto/campaign/update/` | Update a TTO campaign |
| `GET /v1.3/tto/campaign/get/` | Get TTO campaigns |

### Content Linking

| Endpoint | Purpose |
|---|---|
| `POST /v1.3/tto/video/link/` | Send/revoke video linking request |
| `GET /v1.3/tto/video/link/brand/get/` | Get linking requests (brand side) |
| `GET /v1.3/tto/video/link/creator/get/` | Get linking requests (creator side) |

### Spark Ads Authorization via TTO

| Endpoint | Purpose |
|---|---|
| `POST /v1.3/tto/spark_ads/apply/` | Apply for Spark Ads authorization |
| `GET /v1.3/tto/spark_ads/status/` | Get authorization status |

---

## Spark Ads with Different Campaign Types

### Manual Campaigns
Full control over targeting, bidding, and creative. Standard Spark Ads creation flow.

### Smart+ Campaigns
AI-optimized campaigns that can use Spark Ads as creative input. The system automatically optimizes delivery.

### Upgraded Smart+ Campaigns
Next-generation AI campaigns supporting Spark Ads within the Ad Groups > Ads structure.

### GMV Max Campaigns
E-commerce campaigns that can boost organic shopping content as Spark Ads for TikTok Shop sellers.

---

## Spark Ads vs Standard Ads

| Feature | Spark Ads | Standard In-Feed Ads |
|---|---|---|
| Content source | Existing organic TikTok posts | Created specifically for advertising |
| Engagement | Accrues to original post | Only on ad instance |
| Social proof | Carries existing engagement | Starts from zero |
| Duet/Stitch | Users can Duet and Stitch | Not available |
| Profile link | Links to creator's profile | Links to custom identity |
| Music | Original post music (if licensed) | Commercial Music Library only |
| Creation | Requires authorization | Created from scratch |
| Format | Video only (original post format) | Video, image, carousel |

---

## Best Practices

### Content Selection
- Choose posts with high organic engagement (likes, comments, shares)
- Use the Spark Ads Recommendation API for AI-powered suggestions
- Select content that aligns with campaign objectives
- Ensure posts have commercial music rights (or original audio)

### Creator Partnerships
- Use TikTok One (Creator Marketplace) for discovery
- Negotiate clear authorization terms and duration
- Request extended auth periods for longer campaigns
- Monitor creator content for brand safety

### Campaign Optimization
- Test Spark Ads against standard ads in split tests
- Use multiple Spark Ads creatives for creative rotation
- Monitor engagement metrics on the original posts
- Leverage high-performing organic content quickly while it's trending

### Authorization Management
- Track authorization expiry dates
- Extend authorizations proactively before they expire
- Have backup creatives ready in case authorization is revoked
- Maintain clear communication with content creators

# TikTok Campaign Management API

## Overview

The Campaign Management API provides full programmatic control over TikTok's three-tier ad structure: **Campaigns > Ad Groups > Ads**. It supports manual campaigns, Smart+ campaigns, Upgraded Smart+ campaigns, GMV Max campaigns, Reach & Frequency campaigns, and Search Ads campaigns.

## Base URL

```
https://business-api.tiktok.com/open_api/v1.3/
```

## Ad Structure Hierarchy

```
Campaign (objective, budget, status)
  |-- Ad Group (targeting, bidding, placement, schedule)
       |-- Ad (creative, identity, landing page)
```

---

## Campaign Endpoints

### Core Campaign CRUD

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/campaign/get/` | GET | Get campaigns list with filtering |
| `/v1.3/campaign/create/` | POST | Create a new campaign |
| `/v1.3/campaign/update/` | POST | Update campaign settings |
| `/v1.3/campaign/status/update/` | POST | Enable/disable/delete campaigns |

### Campaign Copy

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/campaign/copy/` | POST | Create async campaign copy task |
| `/v1.3/campaign/copy/get/` | GET | Get copy task results |

### Campaign Parameters

Key parameters when creating a campaign:

| Parameter | Type | Description |
|---|---|---|
| `advertiser_id` | string | Required. Advertiser account ID |
| `campaign_name` | string | Required. Campaign name |
| `objective_type` | string | Required. Advertising objective |
| `budget_mode` | string | Budget type: `BUDGET_MODE_INFINITE`, `BUDGET_MODE_DAY`, `BUDGET_MODE_TOTAL` |
| `budget` | float | Budget amount (required if budget_mode is not infinite) |
| `operation_status` | string | `ENABLE` or `DISABLE` |
| `campaign_type` | string | Campaign type identifier |

### Advertising Objectives

| Objective | Enum Value | Description |
|---|---|---|
| Traffic | `TRAFFIC` | Drive website/app visits |
| App Promotion | `APP_PROMOTION` | App installs and events |
| Website Conversions | `CONVERSIONS` | Website conversion events |
| Lead Generation | `LEAD_GENERATION` | Collect leads |
| Community Interaction | `ENGAGEMENT` | Followers and engagement |
| Reach | `REACH` | Maximize reach |
| Video Views | `VIDEO_VIEWS` | Maximize video views |
| Sales | `PRODUCT_SALES` | E-commerce sales |
| App Pre-Registration | `PRE_REGISTER` | Android app pre-registration |

---

## Ad Group Endpoints

### Core Ad Group CRUD

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/adgroup/get/` | GET | Get ad groups with filtering |
| `/v1.3/adgroup/create/` | POST | Create an ad group |
| `/v1.3/adgroup/update/` | POST | Update ad group settings |
| `/v1.3/adgroup/status/update/` | POST | Enable/disable/delete ad groups |
| `/v1.3/adgroup/budget/update/` | POST | Update ad group budgets |

### Ad Group Quota

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/adgroup/quota/get/` | GET | Get dynamic quota on active ad groups |

### Audience Size Estimation

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/adgroup/estimate/` | POST | Estimate audience size for targeting |

### Ad Group Key Parameters

#### Placements

| Placement | Description |
|---|---|
| `PLACEMENT_TIKTOK` | TikTok feed |
| `PLACEMENT_PANGLE` | Pangle ad network |
| `PLACEMENT_GLOBAL_APP_BUNDLE` | Global App Bundle |
| Automatic Placement | TikTok determines optimal placement |
| Automatic Search Placement | Includes TikTok search results |

#### Targeting Options

| Category | Options |
|---|---|
| Demographics | Age, gender, language, location |
| Interests | Interest categories, additional interests |
| Behaviors | Action categories, hashtag interactions |
| Device | OS, OS version, device model, carrier, ISP, connection type |
| Custom Audiences | Include/exclude custom audience segments |
| Lookalike Audiences | Expand reach with similar users |
| Smart Targeting | AI-optimized targeting expansion |
| Contextual Targeting | Content-based targeting tags |

#### Bidding Strategies

| Strategy | Enum | Description |
|---|---|---|
| Cost Cap | `BID_TYPE_CUSTOM` | Target cost per result |
| Bid Cap | `BID_TYPE_MAX` | Maximum bid per result |
| Lowest Cost | `BID_TYPE_NO_BID` | Maximize results within budget |
| Maximum Delivery | `BID_TYPE_MAX_DELIVERY` | Spend budget as fast as possible |
| Value-Based Optimization | VBO-specific config | Optimize for ROAS |

#### Optimization Goals

| Goal | Description |
|---|---|
| Click | Optimize for clicks |
| Conversion | Optimize for conversion events |
| Reach | Optimize for unique reach |
| Impressions | Optimize for impressions |
| Video Views | Optimize for video views |
| Lead Generation | Optimize for form submissions |
| App Install | Optimize for app installs |
| App Events | Optimize for in-app events |
| Value | Optimize for conversion value (VBO) |

#### Attribution Windows

Configurable attribution windows for conversion tracking:
- Click-through: 1, 7, 14, 28 days
- View-through: 1, 7 days

---

## Ad Endpoints

### Core Ad CRUD

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/ad/get/` | GET | Get ads with filtering |
| `/v1.3/ad/create/` | POST | Create an ad |
| `/v1.3/ad/update/` | POST | Update ad settings |
| `/v1.3/ad/status/update/` | POST | Enable/disable/delete ads |

### Ad Review

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/ad/review/get/` | GET | Get review info for ads |
| `/v1.3/adgroup/review/get/` | GET | Get review info for ad groups |
| `/v1.3/ad/review/appeal/` | POST | Appeal a rejection |

### Ad Parameters

| Parameter | Type | Description |
|---|---|---|
| `adgroup_id` | string | Required. Parent ad group ID |
| `ad_name` | string | Ad name |
| `ad_format` | string | `SINGLE_VIDEO`, `SINGLE_IMAGE`, `CAROUSEL` |
| `ad_text` | string | Ad copy/text |
| `video_id` | string | Video creative ID |
| `image_ids` | string[] | Image creative IDs (carousel) |
| `call_to_action` | string | CTA button text |
| `landing_page_url` | string | Destination URL |
| `identity_id` | string | Identity for Spark Ads |
| `identity_type` | string | `CUSTOMIZED_USER`, `AUTH_CODE`, `TT_USER` |
| `deeplink` | string | Deep link URL for app promotion |

### Ad Formats

| Format | Description |
|---|---|
| Single Video | Standard video ad (5-60 seconds) |
| Single Image | Static image ad |
| Carousel | Multiple images in a swipeable format |
| Spark Ads | Boosted organic TikTok posts |
| Playable Ads | Interactive HTML5 ads |
| Collection Ads | Video + product cards (deprecated) |

---

## Smart+ Campaign Endpoints

Smart+ campaigns use AI to automate targeting, bidding, and creative optimization.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/smart_plus/campaign/create/` | POST | Create a Smart+ campaign |
| `/v1.3/smart_plus/campaign/update/` | POST | Update a Smart+ campaign |
| `/v1.3/smart_plus/campaign/get/` | GET | Get Smart+ campaigns |
| `/v1.3/smart_plus/campaign/quota/get/` | GET | Get dynamic quota |
| `/v1.3/smart_plus/campaign/creative/status/update/` | POST | Enable/disable creatives |
| `/v1.3/smart_plus/campaign/report/` | GET | Run Smart+ report |

### Smart+ Campaign Types
- Smart+ Web Campaigns
- Smart+ App Campaigns
- Smart+ Lead Generation Campaigns

---

## Upgraded Smart+ Campaign Endpoints

Upgraded Smart+ campaigns restore the Campaign > Ad Group > Ad structure while maintaining AI optimization.

### Campaigns

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/upgraded_smart_plus/campaign/get/` | GET | Get Upgraded Smart+ campaigns |
| `/v1.3/upgraded_smart_plus/campaign/create/` | POST | Create campaign |
| `/v1.3/upgraded_smart_plus/campaign/update/` | POST | Update campaign |
| `/v1.3/upgraded_smart_plus/campaign/status/update/` | POST | Update statuses |

### Ad Groups

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/upgraded_smart_plus/adgroup/get/` | GET | Get ad groups |
| `/v1.3/upgraded_smart_plus/adgroup/create/` | POST | Create ad group |
| `/v1.3/upgraded_smart_plus/adgroup/update/` | POST | Update ad group |
| `/v1.3/upgraded_smart_plus/adgroup/status/update/` | POST | Update statuses |
| `/v1.3/upgraded_smart_plus/adgroup/budget/update/` | POST | Update budgets |

### Ads

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/upgraded_smart_plus/ad/get/` | GET | Get ads |
| `/v1.3/upgraded_smart_plus/ad/create/` | POST | Create ad |
| `/v1.3/upgraded_smart_plus/ad/update/` | POST | Update ad |
| `/v1.3/upgraded_smart_plus/ad/status/update/` | POST | Update statuses |
| `/v1.3/upgraded_smart_plus/ad/creative/status/update/` | POST | Enable/disable creatives |
| `/v1.3/upgraded_smart_plus/ad/preview/` | GET | Preview ads |

### Upgraded Smart+ Reporting

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/upgraded_smart_plus/report/creative_overview/` | GET | Creative overview report |
| `/v1.3/upgraded_smart_plus/report/creative_breakdown/` | GET | Creative breakdown report |

### Campaign Automation Types

When querying reports, the `campaign_automation_type` metric distinguishes:
- `MANUAL`: Manual campaigns
- `SMART_PLUS`: Smart+ campaigns
- `UPGRADED_SMART_PLUS`: Upgraded Smart+ campaigns (ad level)
- `UPGRADED_SMART_PLUS_CREATIVE`: Upgraded Smart+ (creative level within an ad)

---

## GMV Max Campaign Endpoints

GMV Max campaigns optimize for e-commerce gross merchandise value, primarily for TikTok Shop sellers.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/gmv_max/campaign/get/` | GET | Get GMV Max campaigns |
| `/v1.3/gmv_max/campaign/detail/get/` | GET | Get campaign details |
| `/v1.3/gmv_max/campaign/create/` | POST | Create campaign |
| `/v1.3/gmv_max/campaign/update/` | POST | Update campaign |
| `/v1.3/gmv_max/recommendation/get/` | GET | Get recommended ROI target and budget |
| `/v1.3/gmv_max/session/create/` | POST | Create max delivery/creative boost session |
| `/v1.3/gmv_max/session/update/` | POST | Update session |
| `/v1.3/gmv_max/session/get/` | GET | Get sessions within campaign |
| `/v1.3/gmv_max/session/detail/get/` | GET | Get session details |
| `/v1.3/gmv_max/session/delete/` | POST | Delete session |
| `/v1.3/gmv_max/shop/get/` | GET | Get TikTok Shops for GMV Max |
| `/v1.3/gmv_max/shop/availability/` | GET | Check shop availability |
| `/v1.3/gmv_max/identity/get/` | GET | Get identities for GMV Max |
| `/v1.3/gmv_max/occupancy/check/` | GET | Check identity/product occupancy |
| `/v1.3/gmv_max/post/get/` | GET | Get posts for Product GMV Max |
| `/v1.3/gmv_max/video/detail/get/` | GET | Get video details in posts |
| `/v1.3/gmv_max/exclusive/status/` | GET | Get exclusive authorization status |
| `/v1.3/gmv_max/exclusive/grant/` | POST | Grant exclusive shop authorization |
| `/v1.3/gmv_max/report/` | GET | Run GMV Max report |

### GMV Max Campaign Types
- **Product GMV Max**: Product-based optimization
- **LIVE GMV Max**: Live shopping optimization

---

## Reach & Frequency Endpoints

Reservation-based campaigns with guaranteed reach and frequency.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/rf/estimate/` | GET | Get inventory estimates |
| `/v1.3/rf/adgroup/create/` | POST | Create R&F ad group |
| `/v1.3/rf/adgroup/update/` | POST | Update R&F ad group |
| `/v1.3/rf/order/cancel/` | POST | Cancel R&F ad order |
| `/v1.3/rf/adgroup/estimate/get/` | GET | Get estimated info |
| `/v1.3/rf/contract/query/` | GET | Query contracts |
| `/v1.3/rf/timezone/get/` | GET | Get R&F time zones |

---

## Super Split Test Endpoints

A/B testing for campaigns and ad groups.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/split_test/create/` | POST | Create a split test |
| `/v1.3/split_test/time/update/` | POST | Update test duration |
| `/v1.3/split_test/end/` | POST | End a split test |
| `/v1.3/split_test/result/get/` | GET | Get test results |
| `/v1.3/split_test/winner/run/` | POST | Run the winning variant |

---

## Automated Rules Endpoints

Create automated rules to manage campaigns based on performance conditions.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/auto_rule/create/` | POST | Create automation rules |
| `/v1.3/auto_rule/get/` | GET | Get rules by ID |
| `/v1.3/auto_rule/list/` | GET | Get rules by filters |
| `/v1.3/auto_rule/result/get/` | GET | Get rule execution results |
| `/v1.3/auto_rule/result/detail/` | GET | Get result details |
| `/v1.3/auto_rule/update/` | POST | Update rules |
| `/v1.3/auto_rule/status/update/` | POST | Update rule statuses |
| `/v1.3/auto_rule/bind/` | POST | Bind/unbind rules to campaigns |

---

## Reporting Endpoints

### Synchronous Reports

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/report/integrated/get/` | GET | Run synchronous report |

- Returns up to 20,000 ads per query
- Supports filtering by `campaign_ids`, `adgroup_ids`, `ad_ids` (up to 100 per filter)
- Time range: up to 365 days (30 days with daily breakdown)
- Page size: 1-1,000 results

### Asynchronous Reports

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/report/task/create/` | POST | Create async report task |
| `/v1.3/report/task/check/` | GET | Check task status |
| `/v1.3/report/task/download/` | GET | Download report output |
| `/v1.3/report/task/cancel/` | POST | Cancel report task |

### Report Types

| Type | Enum | Description |
|---|---|---|
| Basic | `BASIC` | Core performance metrics at campaign/adgroup/ad level |
| Audience | `AUDIENCE` | Demographic and audience breakdowns |
| Playable | `PLAYABLE_MATERIAL` | Playable ad performance |
| DSA/Catalog | `CATALOG` | Dynamic showcase ad performance |
| Business Center | `BC` | Cross-account BC-level reporting |
| GMV Max | `TT_SHOP` | TikTok Shop GMV Max reporting |

### Data Levels

| Level | Enum | Description |
|---|---|---|
| Advertiser | `AUCTION_ADVERTISER` | Advertiser account level |
| Campaign | `AUCTION_CAMPAIGN` | Campaign level |
| Ad Group | `AUCTION_ADGROUP` | Ad group level |
| Ad | `AUCTION_AD` | Ad level |

### Key Metrics Categories

- **Cost metrics**: spend, billed_cost, cpc, cpm, cpa
- **Delivery metrics**: impressions, reach, frequency, clicks, ctr
- **Video metrics**: video_views, video_watched_2s, video_watched_6s, average_video_play, video_play_actions
- **Conversion metrics**: conversions, conversion_rate, cost_per_conversion, total_complete_payment
- **Engagement metrics**: likes, comments, shares, follows, profile_visits
- **Attribution metrics**: click-through and view-through conversions by window

---

## Ad Comments Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/ad/comment/list/` | GET | Get comments on ads |
| `/v1.3/ad/comment/related/list/` | GET | Get related comments |
| `/v1.3/ad/comment/status/update/` | POST | Show/hide comments |
| `/v1.3/ad/comment/reply/` | POST | Reply to a comment |
| `/v1.3/ad/comment/delete/` | POST | Delete a comment |
| `/v1.3/ad/comment/export/create/` | POST | Create export task |
| `/v1.3/ad/comment/export/status/` | GET | Check export status |
| `/v1.3/ad/comment/export/download/` | GET | Download exported comments |

### Blocked Words for Comments

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/ad/comment/blocked_word/create/` | POST | Create blocked words |
| `/v1.3/ad/comment/blocked_word/update/` | POST | Update a blocked word |
| `/v1.3/ad/comment/blocked_word/status/` | GET | Check word statuses |
| `/v1.3/ad/comment/blocked_word/get/` | GET | Get blocked words |
| `/v1.3/ad/comment/blocked_word/delete/` | POST | Delete blocked words |

---

## Ad Diagnosis

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/ad/diagnosis/get/` | GET | Get diagnoses for underperforming ad groups |

---

## Budget Management

### Campaign Budget Optimization (CBO)
When CBO is enabled, budget is set at the campaign level and automatically distributed across ad groups.

### Budget Parameters

| Parameter | Description |
|---|---|
| `budget_mode` | `BUDGET_MODE_INFINITE` (no limit), `BUDGET_MODE_DAY` (daily), `BUDGET_MODE_TOTAL` (lifetime) |
| `budget` | Budget amount in advertiser's currency |

Budget minimums vary by currency and are documented in the budget verification ratio appendix.

### Recommended Budget/Bid Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/adgroup/budget/suggest/` | GET | Get recommended budgets |
| `/v1.3/adgroup/bid/suggest/` | GET | Get recommended bids |
| `/v1.3/tool/bid/suggest/` | GET | Get a suggested bid |

---

## Identity Management

Identities determine which TikTok account appears on ads.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/identity/create/` | POST | Create a custom identity |
| `/v1.3/identity/delete/` | POST | Delete an identity |
| `/v1.3/identity/get/` | GET | Get identity list |
| `/v1.3/identity/info/` | GET | Get identity info |
| `/v1.3/identity/video/get/` | GET | Get posts under identity |
| `/v1.3/identity/live/get/` | GET | Get live videos under identity |
| `/v1.3/identity/music/status/` | GET | Get music authorization for video |
| `/v1.3/identity/post/info/` | GET | Get TikTok post info |

### Identity Types
- `CUSTOMIZED_USER`: Custom identity created via API
- `AUTH_CODE`: Authorized TikTok account (Spark Ads)
- `TT_USER`: Linked TikTok account

---

## Negative Keywords (Search Ads)

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/negative_keyword/get/` | GET | Get negative keywords |
| `/v1.3/negative_keyword/create/` | POST | Create negative keywords |
| `/v1.3/negative_keyword/update/` | POST | Update a negative keyword |
| `/v1.3/negative_keyword/delete/` | POST | Delete negative keywords |
| `/v1.3/negative_keyword/download/` | GET | Download negative keywords |

---

## Welcome Messages

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/welcome_message/create/` | POST | Create a welcome message |
| `/v1.3/welcome_message/get/` | GET | Get welcome messages |

---

## Tools and Targeting Utilities

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/tool/location/search/` | GET | Search location targeting tags |
| `/v1.3/tool/location/detail/` | GET | Get location details by ID |
| `/v1.3/tool/region/` | GET | Get available locations |
| `/v1.3/tool/language/` | GET | Get languages |
| `/v1.3/tool/interest_category/` | GET | Get interest categories |
| `/v1.3/tool/action_category/` | GET | Get action categories |
| `/v1.3/tool/hashtag/search/` | GET | Search targeting hashtags |
| `/v1.3/tool/hashtag/get/` | GET | Get hashtags by ID |
| `/v1.3/tool/interest_keyword/recommend/` | GET | Get recommended interests/actions |
| `/v1.3/tool/keyword/recommend/` | GET | Get recommended search keywords |
| `/v1.3/tool/keyword/discover/` | GET | Discover new keywords |
| `/v1.3/tool/os/version/` | GET | Get OS versions |
| `/v1.3/tool/device_model/` | GET | Get device models |
| `/v1.3/tool/carrier/` | GET | Get carriers |
| `/v1.3/tool/isp/` | GET | Get internet service providers |
| `/v1.3/tool/contextual_tag/` | GET | Get contextual tags |
| `/v1.3/tool/content_exclusion/` | GET | Get content exclusion categories |
| `/v1.3/tool/vbo/eligibility/` | GET | Check VBO eligibility |
| `/v1.3/tool/brand_safety/partner/status/` | GET | Get Brand Safety partner status |
| `/v1.3/tool/url/verify/` | GET | Verify a URL |
| `/v1.3/tool/phone_region/` | GET | Get phone region codes |
| `/v1.3/tool/timezone/` | GET | Get time zones |
| `/v1.3/tool/tiktok_link/` | GET | Get TikTok in-app link |
| `/v1.3/tool/campaign_label/` | GET | Get campaign labels |
| `/v1.3/tool/mini/` | GET | Get TikTok Minis |

---

## Brand Safety

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/brand_safety/get/` | GET | Get Brand Safety Hub settings |
| `/v1.3/brand_safety/update/` | POST | Set/update Brand Safety settings |

---

## Terms of Service

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/terms/get/` | GET | Get terms |
| `/v1.3/terms/sign/` | POST | Sign terms |
| `/v1.3/terms/status/` | GET | Check terms status |

---

## Change Log

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/change_log/task/create/` | POST | Create download task |
| `/v1.3/change_log/task/status/` | GET | Check task status |
| `/v1.3/change_log/download/` | GET | Download change log |

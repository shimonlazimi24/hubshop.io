# TikTok Audience Network & Audience Management

## Overview

TikTok's audience capabilities span two related but distinct areas:

1. **TikTok Audience Network** - The extended placement network (powered by Pangle) that delivers TikTok ads across third-party apps and publishers
2. **Audience Management API** - The programmatic interface for creating, managing, and targeting custom audience segments within TikTok's advertising platform

This document covers both areas comprehensively.

---

## TikTok Audience Network

### What It Is

The TikTok Audience Network (also referred to as the Global App Bundle or Pangle placement) extends TikTok ad delivery beyond the TikTok app into a network of partner applications. This is TikTok's equivalent of Meta's Audience Network or Google's Display Network.

### Placement Options

| Placement ID | Name | Description |
|---|---|---|
| `PLACEMENT_TIKTOK` | TikTok | Ads within the TikTok app |
| `PLACEMENT_PANGLE` | Pangle | Ads across Pangle's third-party app network |
| `PLACEMENT_GLOBAL_APP_BUNDLE` | Global App Bundle | Extended TikTok family of apps |

### How It Works

1. Advertiser creates campaign with automatic or manual placement selection
2. TikTok's algorithm distributes ads across selected placements
3. Ads are served in partner apps via Pangle SDK integration
4. Performance is tracked and reported back to TikTok's reporting system
5. Attribution follows the same model as TikTok in-app ads

### Reporting by Placement

Use the `placement` dimension in reports to break down performance:

```
GET /v1.3/report/integrated/get/?
  advertiser_id=xxx&
  report_type=BASIC&
  dimensions=["placement"]&
  metrics=["spend","impressions","clicks","ctr","cpm","cpc"]&
  data_level=AUCTION_CAMPAIGN&
  start_date=2025-01-01&
  end_date=2025-01-31
```

### Audience Network Controls

See [06-pangle.md](./06-pangle.md) for detailed Pangle/Audience Network controls including block lists and brand safety.

---

## Audience Management API

### Purpose

The Audience Management API allows advertisers to create, manage, and apply custom audience segments for ad targeting. These audiences can be used for:

- **Targeting**: Reach specific user segments
- **Exclusion**: Exclude users who already converted
- **Lookalike expansion**: Find users similar to existing audiences
- **Retargeting**: Re-engage users who interacted with your content

### Base URL

```
https://business-api.tiktok.com/open_api/v1.3/
```

### Authentication

Standard Marketing API `Access-Token` header.

---

## Audience Types

### 1. Customer File Audience

Upload first-party customer data (emails, phone numbers, advertising IDs) to create audiences.

#### Upload Flow

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/dmp/custom_audience/file/upload/` | POST | Upload an audience file |
| `/v1.3/dmp/custom_audience/create_by_file/` | POST | Create audience from uploaded file |

#### Supported Identifiers

| Identifier | Description | Hashing |
|---|---|---|
| `IDFA` | iOS Identifier for Advertisers | SHA-256 |
| `GAID` | Google Advertising ID | SHA-256 |
| `EMAIL` | Email addresses | SHA-256 |
| `PHONE` | Phone numbers | SHA-256 |

#### File Upload

```json
POST /v1.3/dmp/custom_audience/file/upload/

// Multipart form upload with:
// - advertiser_id
// - file (CSV with identifiers)
// - file_signature (MD5 hash of file)
```

#### Create Audience from File

```json
POST /v1.3/dmp/custom_audience/create_by_file/

{
  "advertiser_id": "advertiser_id",
  "custom_audience_name": "Email Customer List",
  "file_id": "uploaded_file_id",
  "calculate_type": "EMAIL_SHA256",
  "audience_sub_type": "CUSTOMER_FILE"
}
```

### 2. Rule-Based Audience

Create audiences based on user behavior rules (e.g., website visitors, app users).

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/dmp/custom_audience/rule/create/` | POST | Create audience by rule |

#### Rule Types

| Rule | Description |
|---|---|
| Website Traffic | Users who visited specific URLs |
| App Activity | Users who performed specific in-app events |
| Engagement | Users who engaged with TikTok content |
| Lead Form | Users who interacted with lead forms |

#### Example: Website Visitors Rule

```json
POST /v1.3/dmp/custom_audience/rule/create/

{
  "advertiser_id": "advertiser_id",
  "custom_audience_name": "Cart Abandoners - Last 30 Days",
  "rule": {
    "inclusions": {
      "operator": "OR",
      "rules": [
        {
          "event_source_id": "pixel_id",
          "retention_days": 30,
          "filter_set": {
            "operator": "AND",
            "filters": [
              {
                "field": "event",
                "operator": "eq",
                "value": "AddToCart"
              }
            ]
          }
        }
      ]
    },
    "exclusions": {
      "operator": "OR",
      "rules": [
        {
          "event_source_id": "pixel_id",
          "retention_days": 30,
          "filter_set": {
            "operator": "AND",
            "filters": [
              {
                "field": "event",
                "operator": "eq",
                "value": "CompletePayment"
              }
            ]
          }
        }
      ]
    }
  }
}
```

### 3. Lookalike Audience

Create audiences of users similar to an existing source audience.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/dmp/custom_audience/lookalike/create/` | POST | Create a lookalike audience |
| `/v1.3/dmp/custom_audience/lookalike/refresh/` | POST | Refresh a lookalike audience |

#### Creating a Lookalike

```json
POST /v1.3/dmp/custom_audience/lookalike/create/

{
  "advertiser_id": "advertiser_id",
  "custom_audience_name": "Lookalike - Top Purchasers",
  "source_audience_id": "source_audience_id",
  "lookalike_spec": {
    "location_ids": ["6252001"],
    "lookalike_type": "SIMILAR",
    "audience_size": "MEDIUM"
  }
}
```

#### Lookalike Sizes

| Size | Description |
|---|---|
| `NARROW` | Most similar to source (smaller reach) |
| `BALANCED` | Balanced similarity and reach |
| `BROAD` | Larger reach (less similarity) |

### 4. Saved Audience

Save a combination of targeting settings for reuse across ad groups.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/dmp/saved_audience/create/` | POST | Create a Saved Audience |
| `/v1.3/dmp/saved_audience/get/` | GET | Get Saved Audience details |
| `/v1.3/dmp/saved_audience/delete/` | POST | Delete Saved Audiences |

---

## Audience Management Endpoints

### Core Audience CRUD

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/dmp/custom_audience/get/` | GET | Get all audiences |
| `/v1.3/dmp/custom_audience/detail/` | GET | Get audience details |
| `/v1.3/dmp/custom_audience/update/` | POST | Update an audience |
| `/v1.3/dmp/custom_audience/delete/` | POST | Delete audiences |

### Audience Sharing

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/dmp/custom_audience/share/` | POST | Share audiences with other ad accounts |
| `/v1.3/dmp/custom_audience/share/cancel/` | POST | Cancel sharing |
| `/v1.3/dmp/custom_audience/share/log/` | GET | Get sharing log |

### Audience Application

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/dmp/custom_audience/apply/` | POST | Apply audiences to ad groups |
| `/v1.3/dmp/custom_audience/apply/log/` | GET | Get application log |

### Audience Segments (Streaming API)

For real-time audience updates, TikTok provides a streaming API for audience segments:

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/dmp/audience_segment/create/` | POST | Create/delete an audience segment |
| `/v1.3/dmp/audience_segment/mapping/` | POST | Add/delete segment mappings |

The Streaming API allows you to add or remove users from audiences in near real-time, rather than uploading batch files.

---

## Audience Insights

Analyze potential audience sizes and overlaps.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/dmp/audience/insights/` | GET | Get potential audience details |
| `/v1.3/dmp/audience/overlap/` | GET | Get audience overlap analysis |

### Potential Audience Analysis

```
GET /v1.3/dmp/audience/insights/?
  advertiser_id=xxx&
  audience_ids=["audience_1","audience_2"]
```

Returns demographic and interest breakdowns of the combined audience.

### Audience Overlap

```
GET /v1.3/dmp/audience/overlap/?
  advertiser_id=xxx&
  audience_ids=["audience_1","audience_2"]
```

Returns the overlap percentage and size between audiences.

---

## Identifier Normalization Guidelines

When uploading customer files, identifiers must be normalized before hashing:

| Identifier | Normalization Rules |
|---|---|
| Email | Lowercase, trim whitespace, remove dots from username (Gmail) |
| Phone | E.164 format (e.g., +12025551234), remove spaces/dashes |
| IDFA | Lowercase, with hyphens |
| GAID | Lowercase, with hyphens |

All identifiers must be SHA-256 hashed before upload.

---

## Targeting Options in Ad Groups

When creating ad groups, audiences are combined with demographic and behavioral targeting:

### Demographic Targeting

| Parameter | Description |
|---|---|
| `gender` | `GENDER_MALE`, `GENDER_FEMALE`, `GENDER_UNLIMITED` |
| `age_groups` | Age ranges: `AGE_13_17`, `AGE_18_24`, `AGE_25_34`, `AGE_35_44`, `AGE_45_54`, `AGE_55_100` |
| `languages` | Language codes |
| `location_ids` | Location IDs (countries, states, cities, DMAs) |

### Interest & Behavior Targeting

| Parameter | Description |
|---|---|
| `interest_category_ids` | Interest category IDs |
| `interest_keyword_ids` | Interest keyword/hashtag IDs |
| `action_category_ids` | Action/behavior category IDs |
| `action_days` | Lookback window for behaviors (7, 15, 30 days) |

### Device Targeting

| Parameter | Description |
|---|---|
| `operating_systems` | `ANDROID`, `IOS` |
| `os_versions` | Minimum OS version |
| `device_model_ids` | Specific device models |
| `carrier_ids` | Network carriers |
| `connection_type` | `WIFI`, `2G`, `3G`, `4G`, `5G` |
| `device_price` | Device price ranges |

### Custom Audience Targeting

| Parameter | Description |
|---|---|
| `audience_ids` | Include users in these audiences |
| `excluded_audience_ids` | Exclude users in these audiences |

### Smart Targeting

AI-powered targeting that automatically expands beyond specified targeting:

| Endpoint | Method | Purpose |
|---|---|---|
| (within adgroup create/update) | | Enable `smart_targeting` flag |

### Contextual Targeting

Target users based on the content they are currently viewing:

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/tool/contextual_tag/get/` | GET | Get available contextual tags |
| `/v1.3/tool/contextual_tag/detail/` | GET | Get tag details |

---

## Audience Estimation

Before creating ad groups, estimate the audience size:

```json
POST /v1.3/adgroup/estimate/

{
  "advertiser_id": "advertiser_id",
  "placements": ["PLACEMENT_TIKTOK"],
  "location_ids": ["6252001"],
  "age_groups": ["AGE_18_24", "AGE_25_34"],
  "gender": "GENDER_UNLIMITED",
  "interest_category_ids": [12345],
  "audience_ids": ["custom_audience_id"]
}
```

Response includes estimated daily reach and impressions.

---

## Best Practices

### Audience Strategy
1. **Start broad, then narrow**: Begin with larger audiences and refine based on performance
2. **Layer targeting carefully**: Don't over-restrict; each layer reduces reach
3. **Use exclusions**: Exclude converted users to avoid wasting budget
4. **Refresh lookalikes**: Regularly refresh lookalike audiences for freshness
5. **Test audience sizes**: Compare narrow vs. broad lookalikes

### Customer Data
1. **Normalize before hashing**: Follow TikTok's exact normalization rules
2. **Use multiple identifiers**: Upload emails AND phone numbers for better match rates
3. **Minimum audience size**: Need at least 1,000 matched users for targeting
4. **Update regularly**: Refresh customer file audiences with fresh data
5. **Comply with privacy laws**: Only upload data you have consent to use

### Retargeting
1. **Segment by recency**: Create audiences with different lookback windows
2. **Segment by intent**: Separate ViewContent, AddToCart, and Purchase audiences
3. **Exclude converters**: Don't retarget users who already completed the desired action
4. **Frequency cap**: Use frequency settings to avoid ad fatigue

### Audience Network
1. **Start with automatic placement**: Let TikTok optimize across placements
2. **Monitor by placement**: Review Pangle vs. TikTok performance separately
3. **Use block lists**: Maintain block lists for brand safety on Pangle
4. **Test incrementality**: Measure whether Pangle delivers incremental conversions

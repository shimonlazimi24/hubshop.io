# TikTok Developer - Commercial Content API

## Overview

The Commercial Content API (part of the Research API family) provides access to TikTok's ad library and commercial content data. It enables querying ads, advertisers, ad details, ad reports, and branded/commercial content. All endpoints use the `research.adlib.basic` scope and require a **client access token**.

## Base URL

```
https://open.tiktokapis.com/v2/research/adlib/
```

## Authentication

- **Token type**: Client access token (Bearer)
- **Required scope**: `research.adlib.basic`
- **Header**: `Authorization: Bearer {client_access_token}`

---

## Endpoints

### 1. Query Ads

```
POST https://open.tiktokapis.com/v2/research/adlib/ad/query/
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fields` | string | Yes | Comma-separated fields: `ad.id`, `ad.first_shown_date`, `ad.last_shown_date`, `ad.status`, `ad.videos`, `ad.image_urls`, `ad.reach`, `advertiser.business_id`, `advertiser.business_name` |

**Request Body:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filters` | RequestFilters | Yes | Query filter criteria |
| `search_term` | string | No | Keywords (max 50 chars); overrides `advertiser_business_ids` |
| `search_type` | string | No | `exact_phrase` (default) or `fuzzy_phrase` |
| `max_count` | integer | No | Results per page (default 10, max 50) |
| `search_id` | string | No | Resume cached search results |

**RequestFilters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ad_published_date_range` | DateRange | Yes | Min date must be after 2022-10-01 (format: YYYYMMDD) |
| `country_code` | string | No | Target country (default: "ALL") |
| `advertiser_business_ids` | array | No | List of advertiser business IDs |
| `unique_users_seen_size_range` | SizeRange | No | Reach filter using K/M/B notation |

**SizeRange format:** integers followed by K (thousands), M (millions), or B (billions). Valid: `"0K"`, `"120K"`, `"2M"`, `"1B"`. Invalid: `"2000K"`, `"1.1M"`.

**Response:**

```json
{
  "data": {
    "ads": [
      {
        "ad": {
          "id": 1923845247192304,
          "first_shown_date": "20210101",
          "last_shown_date": "20210101",
          "status": "active",
          "videos": [{"url": "https://..."}],
          "image_urls": ["https://..."],
          "reach": {"unique_user_seen": "11K"}
        },
        "advertiser": {
          "business_id": 3847236290405,
          "business_name": "Company Name",
          "paid_by": "Funding Source"
        }
      }
    ],
    "has_more": true,
    "search_id": "2837438294054038"
  },
  "error": {
    "code": "ok",
    "http_status_code": 200,
    "log_id": "string",
    "message": ""
  }
}
```

**Ad Status Values:** `active` (currently running), `inactive` (no longer displayed)

---

### 2. Query Advertisers

```
POST https://open.tiktokapis.com/v2/research/adlib/advertiser/query/
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fields` | string | Yes | `business_name`, `business_id`, `country_code` |

**Request Body:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search_term` | string | Yes | Search string (max 50 chars) |
| `max_count` | integer | No | 1-50, default 10 |

**Response:**

```json
{
  "data": {
    "advertisers": [
      {
        "business_id": 12345,
        "business_name": "Company",
        "country_code": "US"
      }
    ]
  }
}
```

---

### 3. Get Ad Details

```
POST https://open.tiktokapis.com/v2/research/adlib/ad/detail/
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fields` | string | Yes | `ad.id`, `ad.first_shown_date`, `ad.last_shown_date`, etc. |

**Request Body:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ad_id` | i64 | No | Numeric ad identifier |

**Response includes:**
- `data.ad`: Ad metadata (ID, dates, status, videos, images, reach with country breakdown)
- `data.advertiser`: Business info, TikTok account (profile_url, avatar_url, follower_count)
- `data.ad_group`: Targeting info (countries, age/gender maps, interests, audience_targeting, video_interactions, creator_interactions, number_of_users_targeted)

---

### 4. Get Ad Report

```
POST https://open.tiktokapis.com/v2/research/adlib/ad/report/
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fields` | string | Yes | Must include `count_time_series_by_country` |

**Request Body:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filters.ad_published_date_range` | DateRange | Yes | Min date after 2022-10-01 |
| `filters.country_code` | string | No | Default "ALL" |
| `filters.advertiser_business_ids` | array | No | Business IDs to filter |

**Response:**

```json
{
  "data": {
    "count_time_series_by_country": {
      "IT": [{"date": "20210109", "count": 45}],
      "ES": [{"date": "20210109", "count": 48}]
    }
  }
}
```

---

### 5. Query Commercial Content

```
POST https://open.tiktokapis.com/v2/research/adlib/commercial_content/query/
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fields` | string | Yes | `id`, `create_timestamp`, `create_date`, `label`, `brand_names`, `creator`, `videos` |

**Request Body:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filters.content_published_date_range` | DateRange | Yes | Min date after 2022-10-01 |
| `filters.creator_country_code` | string | No | EEA country code (default: ALL) |
| `filters.creator_usernames` | array | No | List of creator handles |
| `max_count` | integer | No | Default 10, max 50 |
| `search_id` | string | No | Resume previous search |

**Response:**

```json
{
  "data": {
    "commercial_contents": [
      {
        "id": "string",
        "create_date": "YYYYMMDD",
        "create_timestamp": 1234567890,
        "label": "string",
        "brand_names": ["Brand A"],
        "creator": "username",
        "videos": [{"cover_image_url": "...", "url": "...", "id": "...", "status": "..."}]
      }
    ],
    "has_more": true,
    "search_id": "string"
  }
}
```

---

## Supported Countries

The Commercial Content API covers **31 countries**:

**EU Member States (27):** Austria, Belgium, Bulgaria, Croatia, Cyprus, Czech Republic, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Ireland, Italy, Latvia, Lithuania, Luxembourg, Malta, Netherlands, Poland, Portugal, Romania, Slovakia, Slovenia, Spain, Sweden

**Additional EEA:** Iceland, Liechtenstein, Norway

**Other:** United Kingdom, Switzerland

## Key Constraints

- All date ranges must have a minimum date after **October 1, 2022**
- Pagination via `search_id` for continuing cached searches
- Max 50 results per request
- UK and Switzerland are technically outside EEA but supported

# TikTok Developer - Research API

## Purpose

Query public TikTok video and account data for research purposes. Requires an approved research project.

## Authentication

Uses **client access token** (not user access token). Generated from client key and client secret.

## Endpoints

### Video Query

```
POST https://open.tiktokapis.com/v2/research/video/query/
```

**Filter Fields:**

| Field | Description |
|-------|-------------|
| `keyword` | Search by keyword |
| `create_date` | Filter by creation date |
| `username` | Filter by username |
| `region_code` | Filter by region |
| `video_id` | Filter by specific video ID |
| `hashtag_name` | Filter by hashtag |
| `music_id` | Filter by music |
| `effect_id` | Filter by effect |
| `video_length` | Filter by video duration |

**Comparison Operators:** `EQ`, `IN`, `GT`, `GTE`, `LT`, `LTE`

**Boolean Logic:** `AND`, `OR`, `NOT`

**Pagination:**

| Parameter | Description |
|-----------|-------------|
| `max_count` | Results per page (default 10, max 100) |
| `cursor` | Pagination cursor |
| `search_id` | Search session identifier |
| `has_more` | More results available |

### User Info Query

```
POST https://open.tiktokapis.com/v2/research/user/info/
```

**Parameter:** `username`

**Available Fields:**
- `display_name`
- `bio_description`
- `avatar_url`
- `is_verified`
- `follower_count`
- `following_count`
- `likes_count`
- `video_count`

## Notes

- Requires approved research project application
- Client access token authentication (no user authorization needed)
- Supports complex boolean filter combinations
- Results limited by rate limits and query complexity

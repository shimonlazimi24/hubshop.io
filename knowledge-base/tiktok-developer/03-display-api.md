# TikTok Developer - Display API

## Purpose

Authorize users and display their TikTok profiles and videos on external platforms.

## Required Scopes

- `user.info.basic`
- `video.list`

## Endpoints

### Get User Info

```
GET https://open.tiktokapis.com/v2/user/info/?fields=open_id,union_id,avatar_url,display_name
Authorization: Bearer {access_token}
```

**Response Fields:** `avatar_url`, `display_name`, `open_id`, `union_id`

### List Videos

```
POST https://open.tiktokapis.com/v2/video/list/?fields=id,title,video_description,duration,cover_image_url,embed_link
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "max_count": 20
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `id` | Video ID |
| `embed_link` | Embeddable URL |
| `cover_image_url` | Thumbnail (expires over time) |
| `duration` | Video length |
| `cursor` | Pagination cursor |
| `has_more` | More results available |

### Query Videos (by ID)

```
POST https://open.tiktokapis.com/v2/video/query/?fields=id,cover_image_url,embed_link
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "filters": {
        "video_ids": ["7077642457847994444", "7080217258529732386"]
    }
}
```

## Notes

- Cover image URLs expire over time; refresh periodically via `/video/query/`
- Rate limit: 600 requests per minute per endpoint

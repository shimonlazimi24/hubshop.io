# TikTok Developer - Content Posting API

## Purpose

Post video and photo content directly to TikTok creator accounts.

## Required Scope

- `video.publish`

## Important

All content posted by **unaudited clients** is restricted to **private viewing mode** until API audit completion.

## Endpoints

### Query Creator Info

```
POST https://open.tiktokapis.com/v2/post/publish/creator_info/query/
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Response:**

| Field | Description |
|-------|-------------|
| `creator_avatar_url` | Creator's avatar |
| `creator_username` | Username |
| `creator_nickname` | Display name |
| `privacy_level_options` | Available privacy levels |
| `comment_disabled` | Comments disabled flag |
| `duet_disabled` | Duet disabled flag |
| `stitch_disabled` | Stitch disabled flag |
| `max_video_post_duration_sec` | Max video duration |

### Direct Post Video

```
POST https://open.tiktokapis.com/v2/post/publish/video/init/
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "post_info": {
        "title": "My Video Title",
        "privacy_level": "PUBLIC_TO_EVERYONE",
        "disable_duet": false,
        "disable_comment": false,
        "disable_stitch": false,
        "video_cover_timestamp_ms": 1000
    },
    "source_info": {
        "source": "FILE_UPLOAD",
        "video_size": 50000000,
        "chunk_size": 10000000,
        "total_chunk_count": 5
    }
}
```

**Privacy Levels:** `MUTUAL_FOLLOW_FRIENDS`, `PUBLIC_TO_EVERYONE`, `SELF_ONLY`

**Source Types:** `FILE_UPLOAD`, `PULL_FROM_URL`

**Response:** `publish_id`, `upload_url` (for FILE_UPLOAD)

### Video Upload (chunked)

```
PUT https://open-upload.tiktokapis.com/upload/?upload_id={id}&upload_token={token}
Content-Range: bytes {start}-{end}/{total}
Content-Type: video/mp4
```

### Post Photo

```
POST https://open.tiktokapis.com/v2/post/publish/content/init/
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "post_info": {
        "title": "My Photo Post",
        "description": "Description here",
        "disable_comment": false,
        "privacy_level": "PUBLIC_TO_EVERYONE",
        "auto_add_music": true
    },
    "source_info": {
        "source": "PULL_FROM_URL",
        "photo_cover_index": 0,
        "photo_images": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"]
    },
    "post_mode": "DIRECT_POST",
    "media_type": "PHOTO"
}
```

### Check Post Status

```
POST https://open.tiktokapis.com/v2/post/publish/status/fetch/
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "publish_id": "publish_id_from_init"
}
```

## Requirements

- **Video:** MP4 + H.264 format
- **Photo:** WebP supported, URL from verified domain only
- **Domain verification:** Required for URL-based uploads (both video and photo)
- **Multiple images:** Supported for photo posts

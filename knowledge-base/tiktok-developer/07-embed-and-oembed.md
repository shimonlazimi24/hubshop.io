# TikTok Developer - Embed & oEmbed

## Manual Embed

On desktop TikTok.com: Click Share > Embed > Copy code

## oEmbed API

```
GET https://www.tiktok.com/oembed?url={video_url}
```

### Example

```
GET https://www.tiktok.com/oembed?url=https://www.tiktok.com/@scout2015/video/6718335390845095173
```

### Response (JSON, oEmbed standard)

```json
{
    "title": "Video title",
    "author_name": "Author Name",
    "author_url": "https://www.tiktok.com/@author",
    "html": "<blockquote class=\"tiktok-embed\">...</blockquote><script async src=\"https://www.tiktok.com/embed.js\"></script>",
    "thumbnail_url": "https://...",
    "thumbnail_width": 720,
    "thumbnail_height": 1280,
    "provider_name": "TikTok",
    "provider_url": "https://www.tiktok.com",
    "type": "video",
    "version": "1.0"
}
```

### Features

- Volume control on embedded player
- Recommended videos shown at playback end
- All interactive elements link back to TikTok.com
- No authentication required for oEmbed endpoint

### Integration

Simply include the returned `html` field in your page. The script tag loads TikTok's embed.js which renders the video player.

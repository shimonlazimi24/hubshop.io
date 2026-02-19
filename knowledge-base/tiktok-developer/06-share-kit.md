# TikTok Developer - Share Kit

## Purpose

Share videos and images from third-party apps directly to TikTok.

## Platforms

- iOS (via TikTokOpenShareSDK)
- Android (via ShareApi or Android Intents)

## iOS Implementation

```swift
import TikTokOpenShareSDK

let shareRequest = TikTokShareRequest(
    localIdentifiers: [...],
    mediaType: .video,
    redirectURI: "https://www.example.com/path"
)

shareRequest.send { response in
    let shareResponse = response as? TikTokShareResponse
    if shareResponse?.errorCode == .noError {
        // Handle success
    }
}
```

## Android Implementation

1. Create `ShareApi` instance with activity context
2. Build `MediaContent` with media type and file paths
3. Configure `ShareRequest` with client key, media content, share format
4. Execute `share()` method
5. Handle `ShareResponse` via callback

## Share Formats

| Format | iOS | Android | Description |
|--------|-----|---------|-------------|
| Normal | `.normal` | `DEFAULT` | Share content as-is |
| Green Screen | `.greenScreen` | `GREEN_SCREEN` | Green screen effect mode |

## Content Constraints

| Constraint | iOS | Android |
|------------|-----|---------|
| Max images | 35 | 35 |
| Max videos | 12 | 35 |
| Video duration | Up to 10 min | 1-360 seconds |
| Video format | - | MP4 only |
| Image aspect ratio | 1/2.2 to 2.2 | - |
| Max frame size | - | 1100 pixels |
| Green screen | Single image/video | Single image/video |

## Error Codes

| Code | iOS Meaning | Android Meaning |
|------|-------------|-----------------|
| 0 | Success | Success |
| -1 | Network/common error | Unknown error |
| -2 | User cancelled | User cancelled |
| -3 | Publication failed | Parameter parsing error |
| -4 | Share denied | Permission denied |
| -5 | Unsupported operation | N/A |

## Android Alternative (Intents)

Standard Android Intents work as an alternative:
- `Intent.ACTION_SEND` / `Intent.ACTION_SEND_MULTIPLE`
- MIME types: `video/*` and `image/*`

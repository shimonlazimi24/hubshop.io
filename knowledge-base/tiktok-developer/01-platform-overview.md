# TikTok Developer Platform - Overview

## Base URL

```
https://open.tiktokapis.com
```

## API Products

| Product | Description | Auth Type |
|---------|-------------|-----------|
| Display API | Retrieve user info and video data | User access token |
| Content Posting API | Post videos and photos to TikTok | User access token |
| Research API | Query public video/user data | Client access token |
| Data Portability API | Export user data | User access token |
| Commercial Content API | Ads and advertiser info | User access token |
| Webhooks | Event-based notifications | N/A |

## Development Kits

| Kit | Platforms | Description |
|-----|-----------|-------------|
| Login Kit | Web, Desktop, iOS, Android | OAuth 2.0 user authentication |
| Share Kit | iOS, Android | Share content from apps to TikTok |
| Green Screen Kit | iOS, Android | Green screen camera effects |
| Mobile SDK | iOS, Android | Native TikTok integration |

## Getting Started

1. Create TikTok developer account at `developers.tiktok.com`
2. Create or join an organization (recommended for production)
3. Register an app via "Connect an app"
4. Provide app details:
   - App icon: 1024x1024 px, JPEG/PNG, max 5 MB
   - App name, category, description
5. Configure platform credentials:
   - **Web/Desktop**: Official website URL
   - **Android**: Package name, Play Store URL, app signature, signing certificate
   - **iOS**: App Store URL, Bundle ID
6. Add desired products (Login Kit, Display API, etc.)
7. Complete URL verification
8. Submit for review with demonstration videos (1-5 videos, max 50 MB each)

## TikTok API v2 Key Changes (from v1)

- Bearer token authentication (no more `open_id` in requests)
- GET requests: query parameters only, no request body
- POST requests: `fields` as query parameter, other params in JSON body
- Standard HTTP status codes (4xx/5xx) with error details in response body
- Legacy URL `https://www.tiktok.com/auth/authorize/` deprecated; use `/v2/auth/authorize/`

## Additional Features

- **Embed/oEmbed**: Embed TikTok videos in websites
- **TikTok Minis**: Mini app framework
- **Monetization**: In-app ads and purchases
- **Mini Games SDK**: Game integration
- **TikTok GO**: Dining integrations

## Important Restrictions

1. Content posted through unaudited clients is private-only
2. Domain/URL verification required for URL-based uploads
3. App review required before going live
4. Apps created after Sept 9, 2024 require URL verification for ToS, Privacy Policy, and Web URLs
5. Must be authorized to use TikTok brand logos/watermarks
6. Cover image URLs expire over time

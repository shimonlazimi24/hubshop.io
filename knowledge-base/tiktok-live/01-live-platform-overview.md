# TikTok LIVE - Platform Overview

## What Is TikTok LIVE

TikTok LIVE is TikTok's real-time livestreaming platform that allows creators to broadcast live video to their followers and the broader TikTok community. It supports interactive features such as real-time comments, virtual gifts, co-hosting (multi-guest streams), and live events. TikTok LIVE is a core part of TikTok's creator monetization strategy through the virtual gifting economy.

## LIVE API

### Base URL

```
https://open.tiktokapis.com/v2/
```

TikTok does not expose a standalone "LIVE API" as a separate product on the Developer Platform in the same way as the Display API or Content Posting API. However, LIVE-related functionality is accessible through several mechanisms:

### Available LIVE Capabilities via TikTok Developer Platform

| Capability | Access Method | Description |
|------------|--------------|-------------|
| LIVE status detection | Display API (`video.list` scope) | Check if a user is currently live |
| LIVE event webhooks | Webhooks (Developer Portal) | Receive notifications for LIVE events |
| LIVE stream embedding | Embed/oEmbed API | Embed live streams in websites |

### TikTok LIVE Events (WebSocket / Server-Sent)

TikTok offers a **LIVE Events API** (sometimes referred to as TikTok Interactive LIVE) that allows developers to receive real-time events from a LIVE stream. This is primarily used for:

- **Interactive overlays** and game integrations
- **Chatbot** and moderation tools
- **Gift tracking** and acknowledgment systems
- **Viewer analytics** in real-time

### LIVE Events API (Interactive LIVE SDK)

TikTok provides an **Interactive LIVE SDK** / **LIVE Events API** for approved partners. Key details:

**Protocol:** WebSocket-based real-time event streaming

**Event Types Available:**

| Event | Description |
|-------|-------------|
| `LiveChatMessage` | Real-time chat/comment messages from viewers |
| `LiveGiftMessage` | Gift sent by a viewer (includes gift ID, value, sender info) |
| `LiveLikeMessage` | Like/heart reactions during the stream |
| `LiveMemberMessage` | User join/leave events for the stream |
| `LiveRoomStatsMessage` | Viewer count and room statistics updates |
| `LiveShareMessage` | When a viewer shares the LIVE stream |
| `LiveFollowMessage` | When a viewer follows the host during the stream |
| `LiveSubMessage` | Subscription events |
| `LiveEmoteMessage` | Emote/sticker reactions |

**Authentication:** OAuth 2.0 Bearer token with LIVE-specific scopes

---

## Virtual Gifts System

### How Gifts Work

1. **Coins**: Users purchase TikTok Coins with real money
2. **Gifts**: Viewers send virtual gifts to creators during LIVE streams, spending coins
3. **Diamonds**: Creators receive Diamonds based on gifts received
4. **Cash Out**: Creators can convert Diamonds to real money (subject to TikTok's revenue share)

### Gift Hierarchy

| Gift Tier | Examples | Approximate Coin Value |
|-----------|----------|----------------------|
| Low-value | Rose, Ice Cream, Heart | 1-49 coins |
| Mid-value | Drama Queen, Hand Heart, Doughnut | 50-499 coins |
| High-value | Concert, Lion, Universe | 500-4,999 coins |
| Premium | TikTok Universe, Galaxy, Lion's Mane | 5,000+ coins |

### Coin Pricing (approximate, varies by region)

| Amount | Price (USD, approximate) |
|--------|--------------------------|
| 65 coins | ~$0.99 |
| 330 coins | ~$4.99 |
| 660 coins | ~$9.99 |
| 1,321 coins | ~$19.99 |
| 3,303 coins | ~$49.99 |
| 6,607 coins | ~$99.99 |

**Revenue Share:** TikTok retains approximately 50% of gift revenue; creators receive the remainder converted to Diamonds.

---

## LIVE Moderation

### Built-in Moderation Features

| Feature | Description |
|---------|-------------|
| Keyword filtering | Block specific words/phrases in chat |
| Comment filter | Filter comments with links, spam, or offensive content |
| Moderator roles | Assign moderators who can mute/block users in chat |
| Auto-moderation | AI-based content filtering for comments |
| Block/report users | Host and moderators can block viewers |
| Restricted mode | Limit chat to followers only or to accounts of a certain age |

### API Moderation Capabilities

For approved LIVE API partners:

- **Read chat messages** in real-time to apply custom moderation rules
- **Filter/flag messages** based on custom logic
- **Track user behavior** patterns across LIVE sessions
- **Ban/mute users** through partner moderation tools

---

## LIVE Streaming Technical Requirements

### Host Requirements

- **Minimum followers**: 1,000 followers (may vary by region; some regions require fewer)
- **Minimum age**: 18 years old to go LIVE; 18+ to send/receive gifts
- **Account standing**: Account must be in good standing (no active violations)
- **App version**: Latest version of TikTok app recommended

### Streaming Protocols

| Protocol | Use Case |
|----------|----------|
| RTMP | Standard ingest for streaming software (OBS, Streamlabs) |
| WebRTC | Low-latency streaming from mobile devices |
| HTTP-FLV / HLS | Playback delivery to viewers |

### RTMP Streaming (via OBS/Streaming Software)

Approved creators can obtain an RTMP **Server URL** and **Stream Key** from TikTok LIVE Studio or the TikTok app's LIVE settings. This enables:

- Desktop streaming via OBS Studio, Streamlabs, or similar tools
- Multi-camera setups
- Custom overlays and scenes
- Screen sharing

### TikTok LIVE Studio

TikTok provides a **desktop streaming application** called **TikTok LIVE Studio** (available for Windows and macOS) with features:

- Scene management and transitions
- Webcam, screen capture, and window capture sources
- Chat overlay
- Gift alerts
- Audio mixing
- Green screen support
- Portrait and landscape modes

---

## Multi-Guest LIVE (Co-hosting)

### Features

- **Go LIVE Together**: Host can invite up to 5 guests simultaneously
- **LIVE Battles**: Two hosts compete for gifts in a timed battle
- **LIVE Events**: Scheduled LIVE events with RSVPs and notifications
- **Subscription LIVE**: Subscriber-only streams for monetizing loyal followers

---

## Developer Access Requirements

### To Access LIVE Events API

1. Register as a TikTok developer at `developers.tiktok.com`
2. Create an app and request LIVE-related scopes
3. LIVE Events API access is **restricted** -- requires partnership or whitelist approval
4. Submit a use case description and request access through TikTok's developer support
5. Approved apps receive WebSocket credentials for LIVE event streaming

### Available Scopes (LIVE-related)

| Scope | Description |
|-------|-------------|
| `user.info.basic` | Basic user info (required) |
| `user.info.stats` | Follower count and engagement metrics |
| `video.list` | Access to video list (can detect LIVE status) |

**Note:** Dedicated LIVE scopes (e.g., `live.room.info`, `live.room.manage`) are available to approved partners but are not listed in the public developer documentation as generally available.

---

## Third-Party LIVE Integration Libraries

Several open-source community projects exist for TikTok LIVE integration:

| Library | Language | Description |
|---------|----------|-------------|
| `TikTokLive` | Python | Connect to TikTok LIVE rooms and receive real-time events |
| `TikTok-Live-Connector` | Node.js | WebSocket-based LIVE event listener |
| `TikTokLiveSharp` | C# | .NET library for TikTok LIVE events |
| `tiktoklive` | Go | Go client for TikTok LIVE WebSocket |

**Important:** These are **unofficial** libraries that reverse-engineer TikTok's internal WebSocket protocol. They are not endorsed by TikTok and may break with API changes. For production use, the official LIVE Events API (partner access) is recommended.

---

## Key Limitations

1. **No public LIVE API**: The full LIVE Events API is not publicly documented; it requires partner-level access
2. **Gift economy is opaque**: Exact conversion rates and revenue share percentages are not exposed via API
3. **Region restrictions**: LIVE features vary by market (gifts, shopping, minimum followers)
4. **Rate limits**: Real-time event streams are subject to connection limits per application
5. **Content restrictions**: LIVE content must comply with TikTok Community Guidelines and LIVE-specific policies
6. **No LIVE video recording API**: There is no API to download or record LIVE stream content

## Related Documentation

- TikTok Developer Platform Overview: `../tiktok-developer/01-platform-overview.md`
- OAuth and Tokens: `../tiktok-developer/02-oauth-and-tokens.md`
- Webhooks: `../tiktok-developer/10-webhooks.md`
- LIVE Commerce: `./02-live-commerce.md`

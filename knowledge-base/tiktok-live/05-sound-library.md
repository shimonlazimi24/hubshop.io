# TikTok Sound Library & Music Licensing

## Overview

The **TikTok Sound Library** (also called the TikTok Commercial Music Library or TikTok Audio Library) is TikTok's collection of licensed music and sound effects available for use in TikTok content. It includes both licensed commercial tracks and royalty-free music specifically cleared for use on the platform. TikTok also provides a **Commercial Music Library** for businesses and advertisers with additional licensing for commercial use.

---

## Sound Library Types

### 1. TikTok General Sound Library (In-App)

| Aspect | Details |
|--------|---------|
| Access | Built into TikTok app (Add Sound feature) |
| Content | Licensed music tracks, viral sounds, user-created sounds |
| Usage | Personal and creator content on TikTok |
| Licensing | Covered by TikTok's platform-wide music licensing deals |
| Restrictions | Not cleared for commercial/advertising use |
| API Access | No public API |

### 2. TikTok Commercial Music Library (CML)

| Aspect | Details |
|--------|---------|
| Access | TikTok Ads Manager / TikTok For Business |
| Content | Pre-cleared royalty-free music for commercial use |
| Usage | TikTok ads, branded content, business accounts |
| Licensing | Cleared for commercial and advertising purposes |
| Restrictions | May not be used off-platform without additional licensing |
| URL | `https://ads.tiktok.com/business/creativecenter/music/` |
| API Access | Available through TikTok Marketing API (limited) |

### 3. SoundOn (TikTok's Music Distribution Platform)

| Aspect | Details |
|--------|---------|
| Access | `https://www.soundon.global/` |
| Content | Independent artist music distribution |
| Usage | Artists distribute music to TikTok and other streaming platforms |
| Features | Music distribution, analytics, royalty collection |
| API Access | No public developer API |

---

## Commercial Music Library (CML) Details

### Purpose

The CML provides brands, advertisers, and business accounts with music that is **pre-cleared for commercial use** on TikTok, eliminating copyright concerns for business content.

### Content Categories

| Category | Description |
|----------|-------------|
| Pop | Popular music genre tracks |
| Hip Hop | Hip hop and rap genre tracks |
| Electronic | EDM, house, and electronic genres |
| Rock | Rock and alternative genres |
| R&B | R&B and soul genres |
| Country | Country music tracks |
| Jazz | Jazz and blues tracks |
| Classical | Classical and orchestral pieces |
| Ambient | Background and ambient music |
| Sound Effects | Non-music sound effects and transitions |
| Holiday/Seasonal | Holiday and seasonal themed tracks |

### Filtering Options

| Filter | Description |
|--------|-------------|
| Genre | Musical genre category |
| Mood | Happy, sad, energetic, calm, dramatic, etc. |
| Theme | Travel, food, fitness, beauty, tech, etc. |
| Duration | Track length filtering |
| Tempo | BPM-based filtering (slow, medium, fast) |
| Vocals | Vocal or instrumental only |
| Region | Music popular in specific markets |

---

## Music on TikTok - Platform Licensing

### How TikTok Music Licensing Works

TikTok maintains licensing agreements with major music labels and publishers:

| Label/Publisher | Relationship |
|-----------------|-------------|
| Universal Music Group (UMG) | Licensing deal (renegotiated periodically) |
| Sony Music | Licensing deal |
| Warner Music Group | Licensing deal |
| Merlin (independent labels) | Licensing deal |
| Various publishers (NMPA, etc.) | Publishing rights deals |

### Licensing Tiers

| Tier | Usage | License Coverage |
|------|-------|-----------------|
| Personal | User-generated content (non-commercial) | Covered by platform license |
| Creator | Creator content (monetized via gifts, etc.) | Covered by platform license |
| Business | Business account content | Limited; use CML for cleared music |
| Advertising | Paid ads and promotions | Requires CML or separate license |

### Music Restrictions for Business Accounts

- **Business accounts** have access to a **reduced music library** compared to personal/creator accounts
- Business accounts can only use tracks from the **Commercial Music Library**
- Using non-CML music in business content may result in the video being muted or taken down
- This is due to different licensing terms for commercial vs. personal use

---

## Sound-Related APIs

### TikTok Developer Platform

The TikTok Developer Platform does **not** provide a dedicated Sound Library API. However, sound information appears in several existing APIs:

#### Display API - Video Sound Info

When querying videos through the Display API, sound/music metadata is included:

| Field | Description |
|-------|-------------|
| `music_id` | Unique identifier for the sound |
| `music_title` | Name of the track |
| `music_author` | Artist/creator name |
| `music_url` | URL to the sound (if available) |
| `music_duration` | Duration of the track in seconds |

#### Content Posting API - Sound Usage

When posting content via the Content Posting API:

| Capability | Status |
|------------|--------|
| Post video with original sound | Supported |
| Post video with no sound | Supported |
| Attach licensed music to video | **Not supported** via API |
| Use sound from another video | **Not supported** via API |

**Note:** The Content Posting API does not support programmatically attaching licensed music tracks to videos. Music must be added through the TikTok app.

#### Research API - Sound Data

The Research API can return sound information associated with videos:

| Field | Description |
|-------|-------------|
| `music_id` | Sound identifier |
| `music_title` | Track name |
| Sound usage count | Number of videos using the sound |

### TikTok Marketing API

The TikTok Marketing API provides limited sound/music access for advertising:

| Endpoint | Description |
|----------|-------------|
| `GET /creative/music/search/` | Search the Commercial Music Library |
| `GET /creative/music/info/` | Get details about a CML track |
| `GET /creative/music/recommend/` | Get recommended music for ad creative |

**Base URL:** `https://business-api.tiktok.com/open_api/`

**Authentication:** TikTok Marketing API access token

---

## SoundOn Platform

### What Is SoundOn

SoundOn is TikTok's music distribution platform that allows independent artists to:

- Upload and distribute music to TikTok directly
- Distribute to other streaming platforms (Spotify, Apple Music, etc.)
- Track music analytics and performance on TikTok
- Collect royalties from streams and usage

### SoundOn for Developers

| Aspect | Details |
|--------|---------|
| Public API | No public developer API available |
| Analytics | Available through SoundOn web dashboard only |
| Distribution | Upload through SoundOn website |
| Royalties | Managed through SoundOn payment system |

---

## Sound Usage in LIVE Streams

### Music in LIVE

| Feature | Description |
|---------|-------------|
| Background music | Hosts can play music during LIVE streams |
| Sound effects | Triggered effects and sounds during LIVE |
| Music licensing in LIVE | Subject to same platform licensing; some music may be restricted |
| LIVE audio detection | TikTok may detect and flag copyrighted music during LIVE |

### LIVE Audio Restrictions

- Playing copyrighted music during LIVE may result in the stream being muted or ended
- The Commercial Music Library can be used for business-related LIVE streams
- Original music and sounds are always allowed

---

## Sound Effects and Custom Sounds

### User-Created Sounds

| Feature | Description |
|---------|-------------|
| Original sounds | Users can create and name original sounds from their videos |
| Sound pages | Each sound has a page showing all videos using it |
| Viral sounds | Popular sounds can go viral and be used by millions |
| Sound attribution | Original creator is credited on the sound page |

### Sound Effects in Effect House

Effect House effects can include custom audio:

| Capability | Description |
|------------|-------------|
| Sound triggers | Effects that play sounds on user interaction |
| Audio-reactive effects | Visual effects that respond to audio input |
| Custom sound effects | Embed short sound effects in AR effects |

---

## Developer Access Summary

| Resource | API Available | Access Method |
|----------|--------------|---------------|
| General Sound Library | No | TikTok app only |
| Commercial Music Library | Limited | TikTok Marketing API |
| Sound metadata (from videos) | Yes | Display API, Research API |
| Add music to posted videos | No | TikTok app only |
| SoundOn distribution | No | SoundOn website only |
| Sound search | Limited | Marketing API for CML |
| Sound analytics | No | SoundOn dashboard / Ads Manager |

---

## Key Limitations

1. **No public Sound Library API**: No dedicated API to browse, search, or play TikTok's sound library
2. **Cannot programmatically attach music**: Content Posting API does not support adding licensed music to videos
3. **Business account restrictions**: Reduced music library for business/commercial content
4. **No off-platform licensing**: TikTok music licenses cover on-platform use only
5. **CML access requires ads account**: Commercial Music Library access requires TikTok For Business account
6. **No SoundOn API**: No programmatic access to SoundOn music distribution features
7. **Music licensing instability**: Platform-wide licensing deals can change (e.g., temporary music removals during renegotiations)
8. **Region-specific availability**: Some tracks are only available in certain markets due to regional licensing

## Related Documentation

- TikTok Developer Platform: `../tiktok-developer/01-platform-overview.md`
- Content Posting API: `../tiktok-developer/04-content-posting-api.md`
- Display API: `../tiktok-developer/03-display-api.md`
- Research API: `../tiktok-developer/05-research-api.md`
- LIVE Platform: `./01-live-platform-overview.md`
- Effect House: `./03-effect-house.md`

# TikTok Branded Mission

## Overview

TikTok Branded Mission is an advertising product that enables brands to crowdsource authentic content from TikTok creators. Brands set a "mission" brief, creators participate by making content that aligns with the brief, and the brand selects the best submissions to boost as paid ads. This bridges the gap between organic creator content and paid advertising.

## How It Works

### For Brands/Advertisers
1. **Create a Mission Brief**: Define the campaign theme, requirements, hashtag, and goals
2. **Set Budget**: Allocate budget for boosting selected creator videos
3. **Review Submissions**: Creators who opt in submit videos aligned with the brief
4. **Select Winners**: Choose the best-performing or most on-brand creator videos
5. **Boost Content**: Selected videos are amplified as Spark Ads across TikTok

### For Creators
1. **Discover Missions**: Browse available Branded Missions in the TikTok app
2. **Create Content**: Produce videos that align with the mission brief
3. **Submit**: Post the video with required hashtag/music
4. **Earn Rewards**: Selected creators receive payments and boosted visibility

## Key Features

- **Crowdsourced creativity**: Leverages creator diversity for authentic content
- **Performance-based selection**: Brands can choose content based on organic performance
- **Spark Ads integration**: Selected content runs as Spark Ads (native format)
- **Creator incentives**: Revenue sharing and exposure for participating creators
- **Brand safety**: Content review before boosting
- **Hashtag challenges**: Often combined with branded hashtag challenges

## Relationship to Other Products

| Product | Relationship |
|---|---|
| Spark Ads | Winning Branded Mission content runs as Spark Ads |
| TikTok One / Creator Marketplace | Creator discovery and campaign management |
| Branded Hashtag Challenge | Often used in conjunction with Branded Mission |
| TopView | Premium placement option for winning content |

## API Access

Branded Mission does not have a dedicated public API. However, related functionality is available through:

### TikTok One API
- Campaign creation and management (includes creator collaboration workflows)
- Content linking and Spark Ads authorization
- Creator discovery and insights

### Marketing API - Reach & Frequency
- Branded Mission campaigns may use Reach & Frequency buying
- `service_type: RESERVATION` in reporting (now deprecated in favor of new buying type filters)
- `buying_type` filter `RESERVATION_TOP_VIEW` for TopView reporting

## Availability

- Available in select markets (varies by region)
- Requires managed advertiser account or agency relationship
- Not available as self-serve in all regions
- Creator eligibility based on follower count and account standing

## Branded Mission vs. Creator Marketplace

| Feature | Branded Mission | Creator Marketplace |
|---|---|---|
| Content Flow | Crowdsourced (open call) | Direct commissioning |
| Creator Selection | Post-creation (performance-based) | Pre-creation (profile-based) |
| Scale | Many creators, one brief | Targeted creator partnerships |
| Content Ownership | Creator posts organically, brand boosts | Negotiated content rights |
| Budget Model | Pay-per-boost | Negotiated creator fees |

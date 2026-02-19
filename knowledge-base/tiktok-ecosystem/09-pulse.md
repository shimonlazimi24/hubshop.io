# TikTok Pulse

## Overview

TikTok Pulse is a contextual advertising solution that places brand ads next to the top-performing content on TikTok. It ensures ads appear adjacent to premium, culturally relevant content in the platform's most engaging feeds, providing brand safety and premium placement.

## Key Concept

Pulse places ads next to the **top 4% of trending content** across TikTok. By running alongside content that has already proven to be engaging and culturally resonant, brands benefit from a premium content adjacency environment.

## How It Works

1. **Content Scoring**: TikTok identifies the top-performing content across the platform based on engagement signals
2. **Category Filtering**: Content is organized into Pulse "lineups" based on content categories
3. **Brand Safety Verification**: All adjacent content is verified by TikTok's brand safety tools and third-party partners
4. **Ad Placement**: Brand ads are inserted in the feed immediately after top-performing content
5. **Revenue Sharing**: Creators whose content qualifies for Pulse placements receive a share of ad revenue

## Pulse Lineups

TikTok Pulse offers category-specific lineups for contextual targeting:

- **For You Feed**: Ads next to trending content across the entire platform
- **Beauty & Personal Care**: Premium beauty content adjacency
- **Entertainment**: Movies, TV, celebrity content
- **Fashion & Style**: Trending fashion content
- **Food & Cooking**: Popular food and recipe content
- **Sports**: Trending sports content
- **Gaming**: Popular gaming content
- **Automotive**: Trending automotive content
- Custom lineups may be available for major advertisers

## Pulse Premiere

**Pulse Premiere** extends the Pulse concept to premium publisher content:
- Places ads next to content from verified premium publishers
- Categories include news, sports, entertainment publishers
- Higher brand safety guarantees with publisher-verified content

## Buying Model

- **Reservation/Premium buy**: Not a standard auction format
- **CPM-based pricing**: Premium CPM rates for guaranteed adjacency
- Typically purchased through managed service or TikTok sales teams
- May require minimum spend commitments

## Marketing API Integration

Pulse campaigns are managed as **Reservation** campaigns in the Marketing API:

### Reporting
- `service_type: RESERVATION` was used for Pulse reporting (now being deprecated)
- New approach: Use `buying_type` filter with values like `RESERVATION_TOP_VIEW` in basic/audience reports
- Reservation ad reports available for performance analysis

### Reach & Frequency
- Pulse campaigns may use Reach & Frequency buying
- `POST /reach/estimate/` - Get inventory estimates
- `POST /reach/adgroup/create/` - Create R&F ad group
- R&F time zone and scheduling support

## Brand Safety

- **Third-party verification**: Partnership with IAS (Integral Ad Science), DoubleVerify, and other brand safety vendors
- **Content adjacency controls**: Pre-bid filtering of content categories
- **Post-campaign reporting**: Brand safety reports on content adjacency
- **Brand Safety Hub**: Settings available via Marketing API:
  - `GET /brand_safety/setting/` - Get Brand Safety Hub settings
  - `POST /brand_safety/setting/update/` - Update Brand Safety Hub settings

## Creator Revenue Sharing

- Creators whose content appears in Pulse placements earn a portion of the ad revenue
- Part of TikTok's Creator Fund / Creator Rewards program
- Incentivizes high-quality content production

## Comparison with Other Premium Products

| Feature | TikTok Pulse | TopView | Branded Mission |
|---|---|---|---|
| Placement | Next to top content | First ad on app open | Crowdsourced creator content |
| Buying | Reservation (CPM) | Reservation | Managed service |
| Content | Platform content (contextual) | Brand creative | Creator-made |
| Targeting | Category lineups | Broad reach | Theme-based |
| Brand Safety | Verified adjacency | Standalone placement | Content reviewed |

## Availability

- Available in major advertising markets
- Requires managed advertiser relationship for Pulse buys
- Pulse Premiere available in select markets with premium publisher partnerships
- Self-serve access limited; primarily sold through TikTok sales teams

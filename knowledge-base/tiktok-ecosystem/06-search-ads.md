# TikTok Search Ads

## Overview

TikTok Search Ads allow advertisers to place ads within TikTok's search results, capturing users with high purchase or action intent at the moment they are actively searching for content, products, or information. Search Ads complement in-feed ads by targeting users based on search queries and keywords.

## Types of Search Ads

### 1. Search Ads Toggle (Automatic Search Placement)
- **Simplest form**: A toggle within Ads Manager that extends existing in-feed ad campaigns to appear in search results
- **No additional keyword setup**: TikTok automatically matches ads to relevant search queries based on ad content and targeting
- **Integrated with existing campaigns**: Works with Traffic, Conversions, App Install, and other objectives
- Available as an automatic placement option at the ad group level

### 2. Search Ads Campaigns (Dedicated)
- **Dedicated search campaigns**: Purpose-built campaigns optimized specifically for search placement
- **Keyword-based targeting**: Advertisers select and bid on specific search keywords
- **Search-specific creative optimization**: Ad creatives optimized for search context
- Full control over keyword strategy, bids, and budgets

## Marketing API Support

### Creating Search Ads Campaigns
The Marketing API includes dedicated support for Search Ads:

- **Create Search Ads Campaigns**: Documented use case in the Marketing API
- **Keyword Management**:
  - `GET /negative_keywords/` - Get negative keywords
  - `POST /negative_keywords/create/` - Create negative keywords
  - `POST /negative_keywords/update/` - Update a negative keyword
  - `DELETE /negative_keywords/delete/` - Delete negative keywords
  - `GET /negative_keywords/download/` - Download negative keywords

### Keyword Research Tools
- `GET /tool/keyword/recommend/` - Get recommended search keywords
- `GET /tool/keyword/discover/` - Discover new keywords
- `GET /tool/search_ads/health/` - Get Search Ads Campaign Health diagnoses

### Automatic Search Placement
- At the ad group level, the `placement` configuration includes automatic search placement
- `automatic_search_placement` setting in ad group creation/update

### Reporting
- Search-specific metrics available in reporting API
- Search placement dimension for performance breakdowns

## Campaign Structure

```
Campaign (Search Ads)
  |
  +-- Ad Group (Keywords + Targeting)
  |     |
  |     +-- Ad (Creative)
  |     +-- Ad (Creative)
  |
  +-- Ad Group (Keywords + Targeting)
        |
        +-- Ad (Creative)
```

## Key Features

- **Keyword bidding**: CPC/CPM bidding on search terms
- **Negative keywords**: Exclude irrelevant search terms
- **Broad/Phrase/Exact match types**: Control keyword matching precision
- **Search term reports**: See actual queries triggering ads
- **Quality score**: Relevance scoring for keyword-ad combinations
- **Campaign health diagnostics**: API-powered health checks for search campaigns

## Search Ads in Smart+ Campaigns

Search placement is also available within Smart+ (automated) campaigns:
- Smart+ automatically optimizes across placements including search
- No manual keyword management needed in Smart+ mode
- AI determines optimal search query matching

## Availability

- Available in major TikTok Ads Manager markets
- Search volume varies significantly by region
- Keyword tools support multiple languages
- Available for most advertising objectives

## Integration with TikTok Shop

Search Ads are particularly relevant for TikTok Shop sellers:
- Product Shopping Ads appear in search results
- TikTok Shop Ads support search placement (feed, search, and shopping centre)
- GMV Max campaigns can optimize across search placements

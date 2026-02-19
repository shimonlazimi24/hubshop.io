# TikTok Local Services / TikTok GO

## Overview

TikTok has been expanding into local services and location-based commerce, though this area remains less formalized than other platforms. The effort connects local businesses with nearby consumers through TikTok's content and advertising ecosystem.

## TikTok Local Services

### Current State
- TikTok has tested local services features in select markets (notably Southeast Asia and China via Douyin)
- Local business profiles allow businesses to showcase services, locations, and offers
- Location-based content discovery helps users find nearby businesses
- Integration with TikTok Shop for local inventory and services

### Douyin (China) - Local Life Services
TikTok's sister app Douyin has a mature local services platform in China:
- Restaurant ordering and delivery
- Hotel and travel bookings
- Local service provider discovery
- Group buying deals
- Store-visit campaigns with geofencing

### TikTok GO (Limited Markets)
- Explored as a local discovery feature in some Southeast Asian markets
- Helps users discover local restaurants, attractions, and services
- Content-driven local recommendations
- Not widely available globally as of early 2026

## Advertising for Local Businesses

### Location-Based Targeting (Marketing API)
The Marketing API provides robust location targeting for local businesses:

- `GET /tool/location/search/` - Search for location targeting tags
- `GET /tool/location/detail/` - Get details about location targeting tags by ID
- `GET /tool/location/list/` - Get available locations by different settings
- `GET /tool/location/advertiser/` - Get available locations by advertiser ID

### Store Visit Campaigns
- Available in select markets
- Measure foot traffic to physical locations
- Integration with location data providers

### Lead Generation for Local
- Instant Forms for capturing local customer information
- Click-to-call ad objectives
- Direct messaging for service inquiries

## API Support

There is no dedicated "Local Services API." Local business functionality is supported through:

1. **Marketing API**: Location targeting, lead generation, store visit campaigns
2. **TikTok Shop API**: For local inventory/product listings (where available)
3. **Business Messaging API**: For customer communication
4. **Events API (Offline)**: For tracking offline conversions at physical locations

### Offline Events API
- `POST /offline/event_set/create/` - Create an Offline Event set
- `POST /offline/event/report/` - Report an Offline Event
- `POST /offline/event/bulk_report/` - Report Offline Events in bulk
- Connects online ad exposure to in-store visits/purchases

## Availability

- Local services features vary significantly by market
- Most mature in China (Douyin), expanding in Southeast Asia
- Western markets primarily served through standard advertising + location targeting
- TikTok GO not widely available as a standalone product

## Future Direction

TikTok's local services strategy appears to be evolving toward:
- Deeper TikTok Shop integration with local inventory
- Content-driven local discovery (short video reviews, location tags)
- Creator partnerships with local businesses
- In-app booking and ordering capabilities (market-dependent)

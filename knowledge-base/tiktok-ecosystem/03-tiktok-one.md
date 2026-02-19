# TikTok One

## Overview

TikTok One is TikTok's unified, all-in-one creative platform that consolidates creative tools, creator collaboration, inspiration/insights, and AI-powered content generation into a single destination for advertisers and brands. It is the successor to and evolution of TikTok Creative Center, and serves as the central hub where all creative capabilities converge.

**Access URL:** `https://ads.tiktok.com/creative/` (requires TikTok for Business login)

**Login page references:** "Log in to your TikTok for Business account to access TikTok Ads Manager, Business Center and TikTok One."

## Core Pillars

### 1. Inspiration
- Upgraded Top Ads with AI-powered analysis
- **Selling Point Insights**: AI-powered selling point analysis of top-performing ads by industry
- **Creative Approach Analysis**: AI-powered insights on video views, CTR, 6s view rates, and engagement metrics
- Top-performing creative strategy identification
- Industry-specific ad examples and patterns

### 2. Creator Collaboration
- **Creator Discovery**: Find and connect with TikTok creators
- **Creator Highlights**: Curated lists of trend-setting, high-engagement creators
- **Creator Marketplace Integration**: Direct connection to TikTok Creator Marketplace (TTCM)
- **Content Linking**: Link creator content to advertising campaigns
- **Spark Ads Authorization**: Get permission to use creator content as ads

### 3. AI Creative Tools (Symphony)
- Symphony Creative Studio integration
- AI-powered video generation
- Script writing and optimization
- See [02-symphony-ai.md](./02-symphony-ai.md) for details

### 4. Top Content
- High-performance organic content analysis
- Filterable by time periods and organic traffic metrics
- Creative pattern identification

## TikTok One API

The TikTok One API (formerly TikTok Creator Marketplace API) provides programmatic access to creator collaboration features:

### Authentication
- `POST /tto/oauth/token/` - Get, renew, or revoke a Creator access token
- `GET /tto/oauth/scopes/` - Obtain the authorized Creator permissions

### Account Management
- `GET /tto/account/authorized/` - Get authorized TTO Creator Marketplace accounts
- `GET /tto/account/status/` - Check TTO Creator Status
- `GET /tto/account/detail/` - Get details of a TTO Creator Marketplace account

### Creator Insights
- `GET /tto/insights/public/account/` - Get TTO Public Account Insights
- `GET /tto/insights/public/media/` - Get TTO Public Media Insights
- `GET /tto/insights/authorized/account/` - Get Authorized TTO Creator Insights
- `GET /tto/insights/authorized/media/` - Get Authorized TTO Media Insights

### Creator Discovery
- `GET /tto/creator/ranking/labels/` - Get TTO creator ranking or search labels
- `GET /tto/creator/ranking/top/` - Get top TTO creator rankings
- `GET /tto/creator/discover/` - Discover TTO creators

### Brand Profiles
- `POST /tto/brand_profile/create/` - Create a Brand Profile for your TTO account
- `GET /tto/brand_profile/list/` - Get the Brand Profiles for your TTO account

### Campaign Management
- `POST /tto/campaign/create/` - Create or update a TTO Creator Marketplace campaign
- `POST /tto/campaign/update/` - Update a TTO Creator Marketplace campaign
- `GET /tto/campaign/list/` - Get TTO Creator Marketplace campaigns

### Content Linking
- `POST /tto/video/link/` - Send or revoke a TTO video linking request
- `GET /tto/video/link/brand/` - Get TTO video linking requests as a brand
- `GET /tto/video/report/` - Report on TTO Creator Marketplace videos

### Spark Ads Integration
- `POST /tto/spark_ads/authorize/` - Apply for Spark Ads authorization
- `GET /tto/spark_ads/status/` - Get the authorization status

### Webpage Anchors
- `POST /tto/anchor/create/` - Create a webpage anchor
- `GET /tto/anchor/list/` - Get webpage anchors
- `DELETE /tto/anchor/delete/` - Delete a draft anchor

### Creator-Side Endpoints
- `POST /tto/creator/campaign/join/` - Join a TTO Creator Marketplace campaign as a creator
- `POST /tto/creator/video/link/` - Link a video to a TTO Creator Marketplace campaign as a creator
- `GET /tto/creator/video/link/` - Get TTO video linking requests as a creator
- `POST /tto/creator/video/link/review/` - Approve or reject a TTO video linking request as a creator

## Spark Ads Recommendation API

Separate from the TTO API, this provides AI-powered recommendations:

- `GET /spark_ads/recommend/business/` - Get Spark Ads video recommendations for a Business Account
- `GET /spark_ads/recommend/tto/` - Get Spark Ads video recommendations for a TTO account
- `POST /spark_ads/all_in_one/create/` - Create a campaign, ad group, and Spark Ad in one step

## Migration from Creative Center

TikTok One is absorbing and replacing TikTok Creative Center:
- Top Ads data and analysis migrating to TikTok One Inspiration
- Creator connection features consolidated into TikTok One
- Creative Center Top Ads will no longer receive updates
- Symphony tools accessible through TikTok One interface

## Relationship to Other Platforms

| Platform | Relationship |
|---|---|
| Creative Center | Being absorbed into TikTok One |
| Symphony | AI engine powering TikTok One creative tools |
| Creator Marketplace (TTCM) | Creator collaboration features within TikTok One |
| Ads Manager | Campaign creation destination from TikTok One |
| Business Center | Account management for TikTok One access |

## Availability

- Requires TikTok for Business account
- Available in all TikTok Ads Manager regions
- API access requires Marketing API developer app registration and appropriate permissions

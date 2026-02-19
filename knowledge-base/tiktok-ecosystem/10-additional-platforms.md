# Additional TikTok Ecosystem Platforms & APIs

## Overview

This document covers all remaining TikTok platforms, APIs, ad products, and ecosystem components not detailed in other files or covered by other agents.

---

## 1. Business Messaging API

### Overview
The Business Messaging API enables programmatic management of direct messages between businesses and users on TikTok. This is separate from TikTok Shop Customer Service.

### Key Capabilities
- **Direct Messaging**: Send and receive messages with users who interact with your business
- **Automatic Messages**: Configure automated responses (welcome messages, suggested questions, chat prompts)
- **Comment-to-Message**: Convert ad/post comments into DM conversations
- **Media Support**: Send and receive images and videos within conversations
- **Webhook Events**: Real-time notifications for new messages

### API Endpoints
- `POST /business_messaging/message/send/` - Send a message to a conversation
- `GET /business_messaging/conversation/list/` - Get a list of conversations
- `GET /business_messaging/message/list/` - Get a list of messages
- `POST /business_messaging/image/upload/` - Upload an image
- `GET /business_messaging/media/download/` - Download image/video from a message
- `GET /business_messaging/capability/check/` - Check messaging capability
- `POST /business_messaging/comment_to_message/toggle/` - Enable/disable Comment-to-Message
- `GET /business_messaging/comment_to_message/setting/` - Get Comment-to-Message setting

### Automatic Messages
- `POST /business_messaging/auto_message/create/` - Create automatic message
- `POST /business_messaging/auto_message/update/` - Update automatic message
- `POST /business_messaging/auto_message/toggle/` - Enable/disable automatic message
- `GET /business_messaging/auto_message/list/` - Get automatic messages
- `DELETE /business_messaging/auto_message/delete/` - Delete automatic message
- `POST /business_messaging/auto_message/sort/` - Sort automatic messages

### Webhooks
- `POST /business_messaging/webhook/create/` - Create webhook configuration
- `GET /business_messaging/webhook/get/` - Get webhook configuration
- `DELETE /business_messaging/webhook/delete/` - Delete webhook configuration

### Data Security
- US data security review required for API access
- Privacy review process for Business Messaging API applicants

---

## 2. Organic API (Accounts & Mentions)

### Accounts API
Manage TikTok Business Accounts organically (not ad-related):

**Insights:**
- `GET /accounts/profile/` - Get profile data of a TikTok account
- `GET /accounts/posts/` - Get post data of a TikTok account
- `GET /accounts/benchmarks/` - Get benchmarks for a business category
- `GET /accounts/privacy/` - Get post privacy settings

**Comments Management:**
- `GET /accounts/comments/` - Get comments on owned videos
- `GET /accounts/comments/replies/` - Get all replies to a comment
- `POST /accounts/comments/create/` - Create a new comment
- `POST /accounts/comments/reply/` - Reply to a comment
- `POST /accounts/comments/like/` - Like/unlike a comment
- `POST /accounts/comments/hide/` - Hide/unhide a comment
- `DELETE /accounts/comments/delete/` - Delete a comment
- `POST /accounts/comments/image/upload/` - Upload a comment image

**Content Publishing:**
- `POST /accounts/posts/video/publish/` - Publish a public video post
- `POST /accounts/posts/photo/publish/` - Publish a photo post
- `GET /accounts/posts/status/` - Get publishing status
- `GET /accounts/posts/hashtags/recommend/` - Get recommended hashtags

**Ad Authorization:**
- `POST /accounts/posts/ad_auth/toggle/` - Enable/disable ad authorization for a post
- `POST /accounts/posts/ad_auth/extend/` - Extend authorization validity period
- `GET /accounts/posts/ad_auth/status/` - Get authorization status
- `DELETE /accounts/posts/ad_auth/delete/` - Delete authorization code

**URL Properties:**
- `POST /accounts/url_property/add/` - Add a URL property to an ad account
- `GET /accounts/url_property/verify/` - Check verification result
- `DELETE /accounts/url_property/delete/` - Delete URL property
- `GET /accounts/url_property/list/` - Get list of URL properties

### Mentions API
Track and respond to brand mentions:

- `GET /mentions/posts/top/` - Get top 1000 mentioned posts
- `GET /mentions/posts/detail/` - Get details of a mentioned post
- `GET /mentions/keywords/frequent/` - Get frequent keywords in mentions
- `GET /mentions/hashtags/frequent/` - Get frequent hashtags in mentions
- `GET /mentions/brand_hashtag/content/` - Get mention content for brand hashtag posts
- `POST /mentions/brand_hashtag/enable/` - Enable brand hashtags
- `GET /mentions/brand_hashtag/enabled/` - Get enabled hashtags
- `DELETE /mentions/brand_hashtag/delete/` - Delete enabled brand hashtag
- `GET /mentions/comments/top/` - Get top 1000 comment mentions
- `POST /mentions/comments/reply/` - Reply to a mention in comments
- Webhook support for real-time mention notifications

---

## 3. TopView Ads

### Overview
TopView is TikTok's premium, full-screen takeover ad format that appears when users first open the TikTok app. It is the highest-impact ad format on the platform.

### Characteristics
- First ad seen on app open (pre-feed)
- Full-screen, immersive video (up to 60 seconds)
- Auto-plays with sound
- Guaranteed 100% share of voice for the time slot
- Reservation-based buying only

### API Access
- TopView campaigns are managed via Reservation campaign APIs
- Reporting: Use `buying_type` filter `RESERVATION_TOP_VIEW` in reporting API
- Reach & Frequency APIs for planning and inventory estimation

---

## 4. Smart+ Campaigns (Automated Advertising)

### Overview
Smart+ is TikTok's fully automated campaign type that uses AI to optimize targeting, bidding, creative, and placements.

### Types
- **Smart+ Web Campaigns**: Website conversion optimization
- **Smart+ App Campaigns**: App install optimization
- **Smart+ Lead Generation**: Lead form optimization
- **Smart+ Catalog Ads**: Automated product catalog advertising
- **Smart+ Automotive Ads**: Vehicle inventory/model advertising
- **Smart+ Travel Ads**: Travel-specific automated campaigns
- **Smart+ Streaming Ads**: Streaming service campaigns
- **Smart+ Mini Series Catalog Ads**: Entertainment catalog campaigns
- **Smart+ E-commerce Catalog Ads**: E-commerce product ads

### Upgraded Smart+ (Latest Generation)
A newer evolution with enhanced campaign structure:
- Separate campaign, ad group, and ad-level APIs
- `campaign_automation_type: UPGRADED_SMART_PLUS` in reporting
- Creative combination management
- Full API support for creation, management, and reporting

### API Endpoints
- `GET /smart_plus/quota/` - Get dynamic quota on Smart+ Campaigns
- `POST /smart_plus/campaign/create/` - Create Smart+ Campaign
- `POST /smart_plus/campaign/update/` - Update Smart+ Campaign
- `GET /smart_plus/campaign/list/` - Get Smart+ Campaigns
- `POST /smart_plus/creative/toggle/` - Disable/enable creatives
- `GET /smart_plus/report/` - Run Smart+ Campaign report

---

## 5. GMV Max Campaigns (TikTok Shop Advertising)

### Overview
GMV Max (Gross Merchandise Value Maximization) is TikTok's automated advertising solution specifically for TikTok Shop sellers to maximize total sales.

### Types
- **Product GMV Max**: Optimize sales for specific products
- **LIVE GMV Max**: Optimize sales during live shopping sessions

### API Endpoints
- `GET /gmv_max/campaign/list/` - Get GMV Max Campaigns
- `GET /gmv_max/campaign/detail/` - Get campaign details
- `POST /gmv_max/campaign/create/` - Create a GMV Max Campaign
- `POST /gmv_max/campaign/update/` - Update a GMV Max Campaign
- `GET /gmv_max/campaign/recommend/` - Get recommended ROI target and budget
- Session management for max delivery and creative boost
- TikTok Shop and identity management
- Dedicated GMV Max reporting metrics

---

## 6. Showcase / TikTok Store

### Overview
TikTok Store (formerly Showcase) allows advertisers to create product showcases linked to their TikTok identity for use in Video Shopping Ads without requiring a full TikTok Shop.

### API Endpoints
- `GET /showcase/identity/list/` - Get identities with Showcase permission
- `GET /showcase/region/list/` - Get available regions for a Showcase
- `GET /showcase/product/list/` - Get available products in a Showcase

### TikTok Store API
- `GET /tiktok_store/list/` - Get available stores under an ad account
- `GET /tiktok_store/product/list/` - Get products within a TikTok Shop

---

## 7. Subscription / Webhook API

### Overview
The Subscription API allows developers to subscribe to real-time event notifications across the TikTok ecosystem.

### Supported Event Types
- **TikTok Account Events**: Post publishing, comment updates
- **Business Messaging Events**: New messages, conversation updates
- **Ad Account Events**: Campaign status changes, delivery events
- **Mentions Events**: Brand mentions in posts and comments

### API Endpoints
- `POST /subscription/create/` - Create a subscription
- `GET /subscription/detail/` - Get subscription details
- `DELETE /subscription/cancel/` - Cancel a subscription

---

## 8. Automated Rules

### Overview
Automated Rules allow advertisers to create rule-based automation for campaign management (e.g., pause campaigns when cost exceeds threshold).

### API Endpoints
- `POST /automated_rules/create/` - Create rules
- `GET /automated_rules/get/` - Get rules by ID or filters
- `GET /automated_rules/results/` - Get rule execution results
- `POST /automated_rules/update/` - Update rules
- `POST /automated_rules/status/update/` - Update rule statuses
- `POST /automated_rules/bind/` - Bind/unbind rules to campaigns

---

## 9. Media Mix Modeling (MMM)

### Overview
Media Mix Modeling data allows advertisers to measure TikTok's contribution to their overall marketing mix alongside other channels.

### API Endpoints
- `POST /mmm/request/create/` - Create an MMM data request
- `GET /mmm/request/status/` - Check request status
- `GET /mmm/request/download/` - Obtain download URL for MMM data
- `GET /mmm/request/history/` - Get request history

---

## 10. Tokopedia Integration (Indonesia)

### Overview
TikTok acquired a majority stake in GoTo's e-commerce unit Tokopedia in late 2023 (completed January 2024) to continue TikTok Shop operations in Indonesia after initial regulatory issues. Tokopedia is now integrated with TikTok Shop Indonesia.

### Key Points
- TikTok Shop Indonesia operates through the Tokopedia infrastructure
- Sellers manage inventory through Tokopedia seller center
- TikTok Shop API supports Indonesia as a region
- Same API endpoints work for Indonesian sellers (region-specific behavior)
- Fulfillment by TikTok (FBT) operates through Tokopedia's logistics network in Indonesia

---

## 11. Playable Ads

### Overview
Playable Ads are interactive ad experiences (mini-games, demos) within TikTok ads.

### API Endpoints
- `POST /playable/upload/` - Upload a playable creative
- `GET /playable/status/` - Check the status of a playable creative
- `POST /playable/save/` - Save a playable creative
- `GET /playable/list/` - Get playable creatives
- `DELETE /playable/delete/` - Delete a playable creative
- Dedicated playable ad reporting with specific dimensions and metrics

---

## 12. Events API Gateway (Self-Hosted)

### Overview
The Events API Gateway is a self-hosted solution for routing TikTok Pixel and Events API data through your own infrastructure, providing enhanced data privacy and control.

### Features
- Self-hosted server-side event processing
- Tenant management for multi-account setups
- User management and access control
- Pixel integration with Gateway
- Enhanced data security and privacy compliance

---

## 13. Super Split Test

### Overview
Advanced A/B testing capabilities for comparing campaign strategies at scale.

### API Endpoints
- `POST /split_test/create/` - Create a split test
- `POST /split_test/time/update/` - Update test timing
- `POST /split_test/end/` - End a split test
- `GET /split_test/results/` - Get test results
- `POST /split_test/winner/apply/` - Run the winning ad group

### Testable Variables
- Targeting, Placement, Bidding & Optimization, Budget Strategy
- Creative Assets, Catalog, Creative
- Custom combinations (campaign level)
- Smart+ configurations

---

## 14. Lead Generation System

### Overview
Comprehensive lead capture and management system integrated with TikTok Ads.

### Features
- **Instant Forms**: In-app lead capture forms
- **Website Forms**: External website lead forms
- **Direct Message Leads**: Lead capture through DMs
- **Instant Messaging App Leads**: Lead capture via third-party messaging apps
- **Phone Call Leads**: Click-to-call lead generation

### API Endpoints
- `POST /leads/test/create/` - Create a test lead
- `GET /leads/test/get/` - Get a test lead
- `POST /leads/download/create/` - Create lead download task
- `GET /leads/download/` - Download leads
- `GET /leads/form/libraries/` - Get form libraries
- `GET /leads/form/fields/` - Get fields of an Instant Form
- `GET /leads/get/` - Get lead data

---

## 15. Change Log API

### Overview
Track changes made to ad accounts, campaigns, and other objects.

### API Endpoints
- `POST /change_log/download/create/` - Create a change log download task
- `GET /change_log/download/status/` - Check task status
- `GET /change_log/download/file/` - Get the downloaded file

---

## 16. Ad Comments Management

### Overview
Manage comments on ads programmatically.

### API Endpoints
- `GET /ad/comments/list/` - Get comments
- `GET /ad/comments/related/` - Get related comments
- `POST /ad/comments/status/update/` - Update comment statuses (hide/show)
- `POST /ad/comments/reply/` - Reply to a comment
- `DELETE /ad/comments/delete/` - Delete a comment
- `POST /ad/comments/export/create/` - Create export task
- `GET /ad/comments/export/status/` - Get export task status
- `GET /ad/comments/export/download/` - Download exported comments

### Blocked Words
- `POST /ad/comments/blocked_words/create/` - Create blocked words
- `POST /ad/comments/blocked_words/update/` - Update blocked word
- `GET /ad/comments/blocked_words/check/` - Check word statuses
- `GET /ad/comments/blocked_words/list/` - Get blocked words
- `DELETE /ad/comments/blocked_words/delete/` - Delete blocked words

---

## 17. Identity Management

### Overview
Manage identities (TikTok accounts, custom identities) used for ad delivery.

### API Endpoints
- `POST /identity/create/` - Create an identity
- `DELETE /identity/delete/` - Delete an identity
- `GET /identity/list/` - Get identity list
- `GET /identity/detail/` - Get identity info
- `GET /identity/posts/` - Get posts under an identity
- `GET /identity/live/` - Get live videos under an identity
- `GET /identity/music_auth/` - Get music authorization info
- `GET /identity/tiktok_posts/` - Get info about TikTok posts

---

## 18. Custom Conversions

### Overview
Define custom conversion events beyond standard event types.

### API Endpoints
- `GET /custom_conversion/list/` - Get Custom Conversions for an event source
- `GET /custom_conversion/detail/` - Get details
- `POST /custom_conversion/create/` - Create a Custom Conversion
- `POST /custom_conversion/update/` - Update a Custom Conversion
- `DELETE /custom_conversion/delete/` - Delete a Custom Conversion

---

## 19. Welcome Messages

### Overview
Manage automated welcome messages for ad-driven messaging conversations.

### API Endpoints
- `POST /welcome_message/create/` - Create a welcome message
- `GET /welcome_message/list/` - Get welcome messages within an ad account

---

## 20. Instant Page Editor SDK

### Overview
SDK for building custom interactive landing pages (TikTok Instant Pages) within the TikTok app experience.

### API Endpoints
- `GET /page/id/` - Get the Page ID
- `POST /page/token/create/` - Create TIP Editor SDK access token
- `GET /page/token/validate/` - Validate TIP Editor SDK access token
- `POST /page/token/renew/` - Renew TIP Editor SDK access token

---

## Summary: Complete TikTok Ecosystem Map

### Consumer Platforms
- TikTok (main app)
- TikTok LIVE
- TikTok Shop (in-app)
- CapCut (video editing)

### Business Platforms
- TikTok Ads Manager
- TikTok Business Center
- TikTok One (creative hub)
- TikTok Creative Center (being absorbed into One)
- TikTok Seller Center (Shop management)

### Developer APIs
- TikTok Developer Platform (Login, Display, Content Posting, Research, etc.)
- TikTok Marketing API (Ads, Audiences, Reporting, Events, etc.)
- TikTok Shop Open API (Seller, Products, Orders, etc.)
- TikTok One API (Creator Marketplace)
- Business Messaging API
- Organic API (Accounts, Mentions)
- Discovery API
- Spark Ads Recommendation API

### Ad Products
- In-Feed Ads (auction)
- TopView (reservation)
- Spark Ads (organic boosting)
- TikTok Pulse (contextual premium)
- Search Ads (keyword)
- Branded Mission (crowdsourced)
- Shopping Ads (commerce)
- GMV Max (Shop optimization)
- Smart+ (fully automated)
- Playable Ads (interactive)
- Branded Hashtag Challenge
- Branded Effects

### Creative Tools
- Symphony (AI suite)
- Creative Center
- CapCut
- Effect House (AR effects)

### Measurement & Analytics
- TikTok Pixel
- Events API (Web, App, Offline, CRM)
- Reporting API
- Media Mix Modeling
- Attribution (SAN integration with MMPs)

# Frodo Data Models Codemap

> Freshness: 2026-02-24 | Auto-generated

## Model Files (18 files, 120+ classes)

### Foundation

**base.py** - `Base`, `UUIDMixin` (UUID pk), `TimestampMixin` (created_at, updated_at)

**user.py** - `User`
- id, email, full_name, hashed_password, is_active, is_superuser

**organization.py** - `Organization`, `Workspace`, `Membership`
- Org -> Workspace -> User (multi-tenant hierarchy)
- `Role` enum: VIEWER, MEMBER, MANAGER, ADMIN, OWNER

**platform.py** - `ConnectedAccount`, `TokenVault`, `PlatformAppCredential`
- `Platform` enum: shop, developer, marketing, research
- `AccountStatus` enum: active, error, disconnected
- TokenVault: AES-256-GCM encrypted access/refresh tokens

**social_identity.py** - `SocialIdentity`
- `SocialProvider` enum: google, tiktok
- Links social OAuth to User by provider_user_id

**webhook.py** - `WebhookEvent`
- `WebhookStatus` enum: received, processing, processed, failed
- platform, event_type, payload (JSON), signature_valid

### Commerce Domain

**commerce.py** (10 models)
- `Shop` - platform_shop_id, shop_name, region, status
- `Product` - platform_product_id, title, status, main_image_url, price
- `ProductSku` - sku_id, price, stock, attributes (JSON)
- `Order` - platform_order_id, status, total_amount, currency, item_count, rts_sla
- `OrderLineItem` - product_id, sku_id, quantity, unit_price
- `Package` - tracking_number, shipping_provider, status
- `OrderStatusEvent` - old_status, new_status, changed_at
- `ReturnRequest` - return_type, reason, refund_amount, status
- `Promotion` - promotion_type, title, discount_type, discount_value, start/end_time
- `SyncCursor` - entity_type, cursor_value, last_synced_at

**affiliate.py** (4 models)
- `AffiliateProduct` - product_id, commission_rate, status
- `OpenCollaboration` - product_id, commission_rate, status
- `TargetCollaboration` - product_id, creator_id, commission_rate
- `CreatorApplication` - collaboration_id, creator_id, status

**finance.py** (3 models)
- `Settlement` - platform_settlement_id, amount, currency, status
- `Transaction` - platform_transaction_id, amount, currency, status
- `Payment` - platform_payment_id, amount, currency, status

### Advertising Domain

**advertising.py** (9 models)
- `AdAccount` - advertiser_id, advertiser_name, status, currency, timezone
- `Campaign` - campaign_name, objective_type, budget, budget_mode, operation_status
- `AdGroup` - adgroup_name, bid_amount, bid_type, budget, optimization_goal, operation_status
- `Ad` - ad_name, ad_format, ad_text, call_to_action, landing_page_url, operation_status
- `AdSyncCursor` - ad_account_id, entity_type, cursor_value, last_synced_at
- `Audience` - name, audience_type, size, status
- `Pixel` - name, pixel_code
- `Catalog` - name, product_count, status
- `ReportCache` - report_type, data_level, date_range, data (JSON)

### Content Domain

**content.py** (5 models)
- `Video` - platform_video_id, title, description, cover_url, duration, status
- `VideoMetrics` - views, likes, comments, shares, watch_time, avg_watch_time
- `ContentPublishJob` - video_url, title, privacy_level, publish_id, status
- `ContentSyncCursor` - entity_type, cursor_value
- `Comment` - platform_comment_id, text, author_name, like_count

### Creator Domain

**creators.py** (4 models)
- `CreatorProfile` - platform_creator_id, display_name, follower_count, engagement_rate, tier
- `CreatorCampaign` - name, objective, budget, commission_rate, status
- `CreatorInvitation` - campaign_id, creator_id, message, status
- `ContentAuthorization` - video_id, creator_id, authorization_code, status

### Analytics Domain

**analytics.py** (5 models)
- `UnifiedKpiSnapshot` - date, metric_type, value, source_module
- `ScheduledReport` - name, frequency, format, recipients, query_config (JSON)
- `Notification` - title, message, type, channel, read
- `NotificationPreference` - notification_type, channel, enabled
- `ApiKey` - name, key_hash, permissions (JSON), last_used_at

### Intelligence Domain

**intelligence.py** (4 models)
- `TrendSnapshot` - category, trend_type, data (JSON), collected_at
- `CompetitorTracker` - name, platform_user_id, tracking_enabled
- `CompetitorContent` - tracker_id, platform_content_id, metrics (JSON)
- `ResearchQuery` - query_type, parameters (JSON), results (JSON)

### LIVE Domain

**live.py** (3 models)
- `LiveSession` - stream_id, title, status, started_at, ended_at, viewer_count
- `LiveEvent` - session_id, event_type, data (JSON)
- `LiveAnalytics` - session_id, peak_viewers, total_likes, total_gifts, revenue

### Messaging Domain

**messaging.py** (3 models)
- `Conversation` - platform_conversation_id, buyer_id, status, last_message_at
- `Message` - conversation_id, content, direction, sent_at
- `AutoMessage` - trigger_type, template, enabled

### Organic Domain

**organic.py** (3 models)
- `BrandMention` - platform_content_id, author, mention_type, sentiment
- `MentionKeyword` - keyword, enabled, last_checked_at
- `OrganicComment` - platform_comment_id, content, author, sentiment

## Schema/DTO Files (6)

Located in `backend/modules/{module}/schemas.py`:
- analytics, advertising, commerce, content, creators, live

Notable DTO fields not in DB models:
- `source_platform` on `CampaignSummaryResponse`/`CampaignDetailResponse` (default: `"marketing"`)
- `source_platform` on `OrderSummaryResponse`/`OrderDetailResponse` (default: `"shop"`)
- `source_platform` on `ProductSummaryResponse` (default: `"shop"`)

## Relationship Map

```
Organization -1:N-> Workspace -N:M-> User (via Membership)
User -1:N-> SocialIdentity
Workspace -1:N-> ConnectedAccount -1:1-> TokenVault
ConnectedAccount -1:N-> Shop -1:N-> Product -1:N-> ProductSku
Shop -1:N-> Order -1:N-> OrderLineItem
Order -1:N-> Package, OrderStatusEvent, ReturnRequest
ConnectedAccount -1:N-> AdAccount -1:N-> Campaign -1:N-> AdGroup -1:N-> Ad
AdAccount -1:N-> Audience, Pixel, Catalog, AdSyncCursor
Workspace -1:N-> Video -1:N-> VideoMetrics, Comment
Workspace -1:N-> ContentPublishJob
Workspace -1:N-> CreatorProfile
Workspace -1:N-> CreatorCampaign -1:N-> CreatorInvitation
Workspace -1:N-> LiveSession -1:N-> LiveEvent
LiveSession -1:1-> LiveAnalytics
Workspace -1:N-> Conversation -1:N-> Message
Workspace -1:N-> BrandMention, MentionKeyword
```

## Enum Reference

| Model File | Enums |
|-----------|-------|
| organization.py | Role (5 levels) |
| platform.py | Platform (4), AccountStatus (3) |
| social_identity.py | SocialProvider (2) |
| commerce.py | ProductStatus, OrderStatus, PackageStatus, ReturnType, ReturnStatus |
| advertising.py | CampaignObjective, BudgetMode, OperationStatus, AdFormat, AudienceType |
| content.py | VideoStatus, PublishStatus |
| creators.py | CreatorTier, CampaignStatus, InvitationStatus, AuthorizationStatus |
| analytics.py | ReportFrequency, ReportFormat, NotificationType, NotificationChannel |
| intelligence.py | TrendType |
| live.py | SessionStatus, LiveEventType |
| messaging.py | MessageDirection, ConversationStatus, AutoMessageType |
| organic.py | MentionType |
| affiliate.py | CollaborationType, CollaborationStatus, InviteStatus, ApplicationStatus |
| webhook.py | WebhookStatus |

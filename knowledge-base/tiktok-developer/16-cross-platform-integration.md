# TikTok Developer - Cross-Platform Integration Analysis

## TikTok Developer Platform vs. TikTok Shop: Relationship

### Separate Platforms

TikTok Developer Platform and TikTok Shop are **separate ecosystems** with distinct:
- Developer portals (`developers.tiktok.com` vs. `partner.tiktokshop.com`)
- Authentication systems
- API endpoints and base URLs
- Account types and registration processes

### Account Relationship

- **TikTok user accounts** and **TikTok Shop seller accounts** are separate entities
- A TikTok user can become a Shop seller, but the seller account is managed through TikTok Shop's separate portal
- TikTok Developer Platform uses `open_id` to identify users; TikTok Shop uses shop/seller IDs
- No documented API to link a TikTok `open_id` to a TikTok Shop seller ID

### Login Kit and TikTok Shop

- **TikTok Login Kit** (from the Developer Platform) is designed for authenticating TikTok social accounts
- **TikTok Shop authentication** uses its own OAuth flow through `auth.tiktok-shops.com`
- There is **no documented cross-authentication** between Login Kit and TikTok Shop APIs
- Each platform requires separate app registration and approval

### Key Differences

| Aspect | TikTok Developer Platform | TikTok Shop |
|--------|--------------------------|-------------|
| Portal | `developers.tiktok.com` | `partner.tiktokshop.com` |
| Auth URL | `open.tiktokapis.com` | `auth.tiktok-shops.com` |
| API Base | `open.tiktokapis.com/v2/` | `open-api.tiktokglobalshop.com` |
| Token type | User access token / Client access token | Shop access token |
| User ID | `open_id` | Shop ID / Seller ID |
| Scopes | `user.info.basic`, `video.list`, etc. | Product, order, fulfillment scopes |

## Integration Patterns

### Pattern 1: Parallel Integration

Build separate integrations for each platform:
- TikTok Developer: Social features (login, video, sharing)
- TikTok Shop: Commerce features (products, orders, fulfillment)
- Link accounts on your application layer using your own user ID

### Pattern 2: Creator-Commerce Bridge

- Use TikTok Developer Display API to access creator content data
- Use TikTok Shop Affiliate APIs for commerce operations
- Match creators by username/profile (no direct API linking)

### Pattern 3: Content + Commerce

- Use Content Posting API to post product showcase videos
- Use `brand_content_toggle` / `brand_organic_toggle` fields in direct post for commercial disclosure
- Monitor video performance via Display API
- Track sales via TikTok Shop Orders API

## Shared Concepts

While the platforms are separate, they share some concepts:

1. **OAuth 2.0**: Both use OAuth flows, but with different authorization servers
2. **Webhooks**: Both support webhook notifications, but with different event types and endpoints
3. **Rate Limits**: Both enforce rate limits, but with different tiers and calculations
4. **Content Moderation**: Both enforce TikTok's community guidelines

## Local Service Scopes (Potential Bridge)

The TikTok Developer Platform includes `local.*` scopes:
- `local.product.manage` - Create and manage product listings
- `local.shop.manage` - Create and manage local shops
- `local.voucher.manage` - Validate and redeem vouchers

These scopes suggest some commerce capabilities exist within the Developer Platform, potentially for TikTok GO (dining) integrations, but documentation on their relationship to TikTok Shop is limited.

## Recommendations for Cross-Platform Builds

1. **Maintain separate auth flows** for each platform
2. **Use your own user table** to link TikTok social identity with Shop seller identity
3. **Do not assume token portability** between platforms
4. **Register separate apps** on each developer portal
5. **Handle webhooks separately** for each platform's events

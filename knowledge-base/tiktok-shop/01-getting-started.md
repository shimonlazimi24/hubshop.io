# TikTok Shop - Getting Started

## Developer Types

There are three types of TikTok Shop developers:

### 1. eCommerce Platform Plugin/Connector Developers
- Create plugins for platforms like Shopify, WooCommerce, Adobe Magento
- Typically do not need to store seller OAuth credentials or data
- Build connectors that sync data between platforms

### 2. eCommerce System Integrators / SaaS Developers
- Create eCommerce systems for advertising, product promotion, marketing
- Require direct access to seller data
- Trusted to store/generate OAuth credentials (bearer and refresh tokens)
- May store, aggregate, and analyze seller data

### 3. TikTok Shop Seller Developers
- Sellers with an active TikTok Shop
- Develop integrations for their own shop needs
- Have access to their own OAuth credentials and data only

## Onboarding Flow

1. **Register** at Partner Center (partner.tiktokshop.com)
2. **Create App** - specify type (public vs custom), category, target market
3. **Configure** - obtain app_key and app_secret, set up APIs and webhooks
4. **Develop** - integrate using API/SDK/Widgets
5. **Test** - use Sandbox environment with test accounts
6. **Launch** - submit for review (public apps) or publish (custom apps)

## App Types

### Public Apps
- Listed on TikTok Shop App Store
- Must pass app review, language listing reviews, compliance review
- Available to all TikTok Shop sellers

### Custom Apps
- Privately distributed via Authorize link
- No app review required
- Suitable for single-seller integrations

## Development Shops (Sandbox)

- Simulate seller workflows without impacting real data
- Create seller/buyer test accounts
- Only test seller accounts can be used for unpublished apps
- Access via Seller Center > Development Shops

## Partner Center URLs

| Resource | URL |
|----------|-----|
| Documentation | https://partner.tiktokshop.com/docv2/page/tts-developer-guide |
| API Reference | https://partner.tiktokshop.com/docv2/ (API Reference tab) |
| Changelog | https://partner.tiktokshop.com/docv2/changelog |
| API Testing Tool | Available in Partner Center |

# TikTok Shop - Use Case Guides

## Overview

TikTok Shop provides detailed integration guides for common app categories. Each guide specifies required and optional use cases, API call flows, and best practices.

---

## 1. Connecting and Managing TikTok Shops

**Source:** [Connecting Shops Guide](https://partner.tiktokshop.com/docv2/page/connecting-shops)

### Integration Pattern

1. Customer authorizes app via OAuth flow
2. Callback with `code` -> exchange for access/refresh tokens
3. Store tokens securely indexed to customer ID
4. Call Get Authorized Shops API to obtain `shop_cipher`

### Call Flows

- **Single Shop Connect:** Get token -> Get Authorized Shops -> store shop data
- **Multi-Shop Connect:** Same flow, iterate over multiple shops in response
- **Reauthorize:** Listen for Type 7 webhook (Upcoming Authorization Expiration)
- **Disconnect:** Handle Type 6 webhook (Seller Deauthorization) + provide UI disconnect

### Required Storage

- `access_token`, `access_token_expire_in`
- `refresh_token`, `refresh_token_expire_in`
- `shop_cipher` (for cross-border/multi-shop sellers)

---

## 2. Order Management System (OMS)

**Source:** [OMS Guide](https://partner.tiktokshop.com/docv2/page/order-management-system-oms)

### Required Use Cases (16 of 27 total)

**Shop Connections (6 required):**
- Single connect, disconnect, multi-management
- Authorization expiration webhook handling
- Carrier mapping

**Product Management (3 required):**
- Product search
- Inventory update via Open API
- Price update via Open API

**Order Sync (6 required):**
- Import orders (webhook + polling fallback)
- Detect order status changes
- Handle ON_HOLD status (1-hour hold period)
- Sync free samples and gift/giveaway products

**Fulfillment (4 required):**
- 3PL order fulfill/ship
- 3PL tracking update
- Order split via Mark Package As Shipped API

### Critical Pattern

Always implement **polling as a fallback alongside webhooks** to ensure no orders are missed.

---

## 3. Connector / Multi-Channel / Dropshipping / Print on Demand

**Source:** [Connector Guide](https://partner.tiktokshop.com/docv2/page/connector-multi-channel-dropshipping-and-print-on-demand)

### App Categories

| Type | Description |
|------|-------------|
| **Connector** | One-to-one platform bridge (e.g., Shopify <-> TikTok Shop) |
| **Multi-Channel** | One-to-many platform connections |
| **Dropshipping** | Source from third-party suppliers, no inventory held |
| **Print on Demand** | Custom products printed when ordered |

### Required Use Cases (55+ total)

All OMS use cases plus:
- Category mapping between platforms
- Listing prerequisite checks (certifications, brands, size charts, hazmat labels, warehouses)
- Product listing with SEO optimization
- White background image optimization
- Post-listing management (search, inventory, price updates)
- Virtual bundle and Gift-with-Purchase order handling

---

## 4. Affiliate Integration

**Source:** [Affiliate Guide](https://partner.tiktokshop.com/docv2/page/affiliate-integration)

### Key Concepts

- Separate authorization flows for Sellers (via Seller Center) and Creators (via TikTok account)
- Two distinct access tokens required

### Use Cases

1. **Generate Affiliate Product Promotion Link** - POST to `/affiliate_seller/202405/products/{product_id}/promotion_link/generate`
2. **Create Open Collaboration** - Any creator can join; one product per collab; configurable commission
3. **Create Targeted Collaboration** - Invite specific creators (up to 50 per call); requires `creator_user_id`
4. **Search Collaborations** - Both seller and creator perspectives
5. **Showcase Management** - Add/remove products from creator showcases
6. **Free Samples** - Enable in Affiliate Center; creators request via promotion link; fulfilled like regular orders
7. **Affiliate Orders** - Track via Search Seller/Creator Affiliate Orders APIs

---

## 5. Customer Engagement

**Source:** [Customer Engagement Guide](https://partner.tiktokshop.com/docv2/page/customer-engagement)

### Integration Options

1. **Shopify Marketing App** - Integrate into Shopify dashboard
2. **Direct TikTok Shop Integration** - Use TTS Customer Engagement APIs directly

### Use Case Groups

- **Customer Management:** Get feature permissions, retrieve customer identifiers (anonymized buyer email from Order Details API), segment by order behavior
- **Content Management:** Retrieve message templates, insert product/coupon cards, preview messages
- **Engagement Tasks:** Create tasks (one-time or automated), send messages to segments
- **Performance Monitoring:** Track sent/read/order/GMV/coupon metrics (T+2 data delay)

### Key Constraints

- Max 1 message/week per shop per customer
- Max 3 messages/week total per customer from TikTok Shop
- US local sellers only
- Recipients must have placed at least 1 order in past 365 days

---

## 6. Additional Solution Guides

| Guide | URL |
|-------|-----|
| Seller Developer Onboarding | [Link](https://partner.tiktokshop.com/docv2/page/seller-developer-onboarding-onepager) |
| App Development Process | [Link](https://partner.tiktokshop.com/docv2/page/app-development-process-overview) |
| Accounting and Finance | [Link](https://partner.tiktokshop.com/docv2/page/accounting-and-finance) |
| Enterprise Resource Planning | [Link](https://partner.tiktokshop.com/docv2/page/enterprise-resource-planning-erp) |
| Customer Service Overview | [Link](https://partner.tiktokshop.com/docv2/page/customer-service-api-overview) |
| Large File Uploads | [Link](https://partner.tiktokshop.com/docv2/page/wfi3nz36) |

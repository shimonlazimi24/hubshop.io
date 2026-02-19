# TikTok LIVE Commerce / LIVE Shopping

## Overview

TikTok LIVE Commerce (also called LIVE Shopping or TikTok Shop LIVE) is the integration of e-commerce functionality directly into TikTok LIVE streams. It allows creators and sellers to showcase, demonstrate, and sell products in real-time during livestreams. Viewers can browse products, add items to cart, and complete purchases without leaving the LIVE stream.

LIVE Commerce is a feature of **TikTok Shop** and is managed through the TikTok Shop ecosystem, not the TikTok Developer Platform.

---

## Platform Architecture

```
TikTok LIVE (streaming) + TikTok Shop (commerce) = LIVE Commerce
```

| Component | Platform | Portal |
|-----------|----------|--------|
| LIVE streaming | TikTok App / TikTok LIVE Studio | TikTok app |
| Product catalog | TikTok Shop | partner.tiktokshop.com / Seller Center |
| Order management | TikTok Shop | partner.tiktokshop.com / Seller Center |
| Affiliate commissions | TikTok Shop Affiliate | partner.tiktokshop.com |

---

## Key Features

### For Sellers/Creators

| Feature | Description |
|---------|-------------|
| Product pinning | Pin products to the LIVE stream for viewers to see and purchase |
| Product showcase | Display a scrollable product list during LIVE |
| Flash sales | Time-limited discounts during LIVE streams |
| Product demos | Real-time product demonstrations with purchase links |
| Cart integration | Viewers can add items to cart and checkout in-stream |
| Co-host selling | Multiple hosts can showcase products together |
| LIVE-exclusive deals | Discounts available only during the LIVE session |

### For Viewers/Buyers

| Feature | Description |
|---------|-------------|
| Product cards | Tap to see product details, pricing, and reviews |
| In-stream checkout | Complete purchase without leaving the LIVE |
| Add to cart | Queue items for later purchase |
| Product Q&A | Ask questions about products in real-time chat |
| Coupon claiming | Claim LIVE-exclusive coupons |
| Product comparison | Browse multiple products during the stream |

---

## LIVE Shopping API (via TikTok Shop API)

LIVE Commerce is managed through the **TikTok Shop API**, not a separate LIVE Shopping API. Relevant endpoints are distributed across several TikTok Shop API domains.

### Base URL

```
https://open-api.tiktokglobalshop.com
```

### Authentication

- **Method**: HMAC-SHA256 signature + `x-tts-access-token` header
- **Token type**: TikTok Shop access token (obtained via TikTok Shop OAuth)
- **Portal**: `partner.tiktokshop.com`

### Relevant API Endpoints for LIVE Commerce

#### Products API (Product Management for LIVE)

| Endpoint | Description |
|----------|-------------|
| `POST /products` | Create products to showcase during LIVE |
| `GET /products` | List products available for LIVE showcase |
| `PUT /products/{product_id}` | Update product details (price, stock, description) |
| `POST /products/inventory` | Manage stock levels during LIVE sales |

#### Orders API (LIVE-Generated Orders)

| Endpoint | Description |
|----------|-------------|
| `GET /orders` | Retrieve orders (filter by source for LIVE orders) |
| `GET /orders/{order_id}` | Get order details from LIVE purchases |
| `POST /orders/{order_id}/ship` | Fulfill LIVE-generated orders |

#### Promotion API (LIVE Deals)

| Endpoint | Description |
|----------|-------------|
| `POST /promotions/flash-deals` | Create flash deals for LIVE sessions |
| `POST /promotions/discounts` | Set LIVE-exclusive discounts |
| `POST /promotions/coupons` | Create LIVE-exclusive coupons |

#### Affiliate API (Creator LIVE Selling)

| Endpoint | Description |
|----------|-------------|
| `POST /affiliate/open-collaborations` | Create open collaboration plans for LIVE sellers |
| `POST /affiliate/target-collaborations` | Invite specific creators for LIVE selling |
| `GET /affiliate/creator/showcase` | Get creator's product showcase for LIVE |

See `../api-reference/` for complete endpoint documentation.

---

## LIVE Shopping Flow

### Seller Workflow

```
1. List products on TikTok Shop (via Seller Center or Products API)
2. Set up LIVE-exclusive promotions/discounts (optional)
3. Start LIVE stream via TikTok app or LIVE Studio
4. Pin products during the stream (product spotlight)
5. Demonstrate products and answer questions
6. Monitor orders in real-time
7. Fulfill orders after LIVE ends
```

### Creator/Affiliate Workflow

```
1. Accept collaboration from seller (open or target)
2. Add seller's products to showcase
3. Start LIVE stream
4. Pin and promote products during stream
5. Earn commission on sales generated
6. Track earnings via Affiliate Creator API
```

### Buyer Workflow

```
1. Join LIVE stream
2. Browse pinned/showcased products
3. Tap product card for details
4. Add to cart or buy now
5. Complete checkout (in-stream or cart page)
6. Receive order confirmation and tracking
```

---

## Product Pinning

Product pinning is the core LIVE Commerce interaction. During a LIVE stream, the host can "pin" a product which:

1. Displays a **product card overlay** on the LIVE video
2. Shows **product name, price, and thumbnail**
3. Includes a **"Buy" or "Add to Cart" button**
4. Can include **flash sale countdown timers**
5. Rotates through products as the host pins different items

**Product pinning is done through the TikTok app UI** during the LIVE stream. There is no documented public API endpoint for programmatic product pinning during a LIVE session.

---

## LIVE Shopping Analytics

### Available via TikTok Shop Seller Center

| Metric | Description |
|--------|-------------|
| LIVE GMV | Gross merchandise value from LIVE sales |
| LIVE orders | Total orders placed during LIVE |
| LIVE viewers | Peak and average concurrent viewers |
| Product click-through rate | % of viewers who tapped product cards |
| Conversion rate | % of product views that resulted in purchase |
| Average order value | Mean order value from LIVE |
| LIVE duration | Total stream length |
| Engagement rate | Comments, likes, shares per viewer |

### Via API

LIVE-specific analytics are not directly available through a dedicated API endpoint. Order data can be filtered by time range corresponding to LIVE sessions to approximate LIVE commerce metrics.

---

## Supported Markets

LIVE Shopping availability varies by region:

| Market | LIVE Shopping Status | Notes |
|--------|---------------------|-------|
| United States | Available | Full feature set |
| United Kingdom | Available | Full feature set |
| Indonesia | Available | Largest LIVE commerce market |
| Thailand | Available | Strong LIVE commerce adoption |
| Vietnam | Available | Growing market |
| Malaysia | Available | Growing market |
| Philippines | Available | Growing market |
| Singapore | Available | Growing market |

**Note:** LIVE Shopping availability is subject to change as TikTok expands/modifies its e-commerce features in different markets.

---

## LIVE Commerce Webhooks

LIVE Commerce events are delivered through TikTok Shop webhooks, not TikTok Developer Platform webhooks.

### Relevant Webhook Events (via TikTok Shop)

| Event | Description |
|-------|-------------|
| `ORDER_STATUS_CHANGE` | Order placed or status updated (includes LIVE-sourced orders) |
| `PRODUCT_STATUS_CHANGE` | Product listing status changes |
| `RETURN_STATUS_CHANGE` | Return/refund initiated for LIVE purchase |
| `PACKAGE_UPDATE` | Shipping updates for LIVE orders |

See `../tiktok-shop/08-webhook-events.md` for complete webhook event documentation.

---

## TikTok Shop Affiliate + LIVE Commerce

The **Affiliate program** is a critical component of LIVE Commerce, enabling creators who don't have their own inventory to sell products on behalf of sellers during LIVE streams.

### Collaboration Types

| Type | Description |
|------|-------------|
| Open Collaboration | Seller sets commission rate; any creator can promote |
| Target Collaboration | Seller invites specific creators with custom commission |
| Shop Plan | Seller sets shop-wide commission rates |

### Commission Structure

- Commission rates are set by sellers (typically 5-30%)
- Higher-value LIVE sellers may negotiate custom rates
- Commissions are tracked per-order and attributed to the creator
- Payouts follow TikTok Shop's settlement cycle

See `../api-reference/affiliate-seller-api.md` and `../api-reference/affiliate-creator-api.md` for API details.

---

## SDK and Integration Tools

### For LIVE Commerce Development

| Tool | Description | Access |
|------|-------------|--------|
| TikTok Shop API SDK | Java, Go, Node.js SDKs for shop operations | `partner.tiktokshop.com` |
| TikTok Shop Widgets | Pre-built UI components for product management | Widget SDK |
| Seller Center | Web dashboard for managing LIVE commerce | `seller.tiktokglobalshop.com` |
| TikTok LIVE Studio | Desktop streaming app with product showcase | Desktop download |

### No Dedicated LIVE Commerce SDK

There is no standalone SDK specifically for LIVE Commerce. The functionality is accessed through:
1. **TikTok Shop API** for product/order/affiliate management
2. **TikTok App** for the LIVE streaming and product pinning UX
3. **TikTok LIVE Studio** for desktop streaming with commerce features

---

## Key Limitations

1. **Product pinning is app-only**: No public API to programmatically pin products during LIVE
2. **LIVE analytics gap**: No dedicated LIVE commerce analytics API; must infer from order timestamps
3. **No real-time sales feed API**: Cannot programmatically subscribe to real-time LIVE sales events
4. **Market restrictions**: LIVE Shopping not available in all markets
5. **Separate auth**: Requires TikTok Shop authentication, not TikTok Developer Platform auth
6. **Content requirements**: LIVE commerce streams must comply with TikTok Shop policies and advertising regulations
7. **Minimum requirements**: Sellers must have an approved TikTok Shop to enable LIVE Shopping

## Related Documentation

- TikTok LIVE Platform: `./01-live-platform-overview.md`
- TikTok Shop Getting Started: `../tiktok-shop/01-getting-started.md`
- TikTok Shop Authentication: `../tiktok-shop/02-authentication.md`
- Affiliate Seller API: `../api-reference/affiliate-seller-api.md`
- Affiliate Creator API: `../api-reference/affiliate-creator-api.md`
- Promotion API: `../api-reference/promotion-api.md`
- Cross-Platform Integration: `../tiktok-developer/16-cross-platform-integration.md`

# TikTok Shop - API Concepts

## Base URL

| Environment | URL |
|-------------|-----|
| Production | `https://open-api.tiktokglobalshop.com` |

HTTPS only. No HTTP support.

## Endpoint Pattern

```
https://{domain}/{category}/{version}/{resource}
```

Example:
```
https://open-api.tiktokglobalshop.com/authorization/202309/shops
https://open-api.tiktokglobalshop.com/product/202309/products/1729435271479265816
```

## HTTP Methods

| Method | Usage |
|--------|-------|
| GET | Access/retrieve resources |
| POST | Create resources or complex queries |
| PUT | Update existing resources |
| DELETE | Remove resources |

## API Categories (12 Domains)

| # | Domain | Description |
|---|--------|-------------|
| 1 | **Product** | Categories, images/videos/certs, CRUD products, inventory/prices, Global Products |
| 2 | **Order** | Order info, fulfillment, cancellation, returns |
| 3 | **Fulfillment** | 3PL status sync, 4PL shipping labels, FBT |
| 4 | **Return & Refund** | Return/refund info, approve/reject requests |
| 5 | **Logistics** | Warehouses, delivery options, shipping providers |
| 6 | **Promotion** | Promotions, discounts, offers |
| 7 | **Finance** | Payment and settlement info |
| 8 | **Seller** | Cross-border shop status, Global Product eligibility |
| 9 | **Authorization** | Token exchange, authorized shop info |
| 10 | **Events** | Webhook subscribe/unsubscribe |
| 11 | **Data Reconciliation** | External data for Quality Engine |
| 12 | **Supply Chain** | Certified warehouse partner fulfillment |

Plus additional domains:
- **Customer Service** - Buyer messaging integration
- **Customer Engagement** - Marketing messages to past buyers
- **Affiliate Seller** - Creator collaboration management
- **Affiliate Creator** - Showcase and video posting
- **Affiliate Partner** - Campaign matchmaking
- **Analytics** - Shop performance metrics
- **Fulfilled by TikTok (FBT)** - FBT warehouse management

## Rate Limits

**Default:** 50 QPS (Queries Per Second) per API per app

**Scoping:** Based on `app + shop` combination
- Calls from one app don't affect another app's limits
- Calls to one shop don't affect another shop's limits
- Each request counts equally regardless of data returned

**Throttling Response:**

| HTTP Status | Description |
|-------------|-------------|
| 429 | Too Many Requests - platform rate limiting |
| 503 | Service Unavailable - server overload protection |

**Best Practices:**
- Stagger API requests in a queue
- Only fetch necessary data
- Cache frequently accessed data
- Implement random exponential backoff for retries
- Include error-catching code

## API Versioning

**Format:** Year + Month (e.g., `202309` = September 2023)

**Release Schedule:** Monthly (not all APIs updated every month)

**Version in URL:**
```
/product/202309/products/{product_id}
```

**Key Policies:**
- Versions assigned at the API level (different APIs may have different latest versions)
- Different API versions can be mixed (but test thoroughly)
- Prior versions available for minimum 2 months after new release
- Retirement announced via changelog at least 2 months in advance

**Retired version error:**
```json
{
    "code": 36009014,
    "message": "The version name is invalid, please check and retry."
}
```

## Common Error Codes

### Success
Response code `0` = success

### General Errors

| Code | Message | Solution |
|------|---------|----------|
| 36009002 | Too many requests | Respect rate limits |
| 36009007 | Request timeout | Retry or split into smaller requests |
| 36009009 | Invalid path | Check API docs |
| 36009010 | Invalid method | Check API docs |
| 36009021 | Invalid file size | File exceeds max limit |
| 36009022 | Invalid request format | Use `application/json` or `multipart/form-data` |

### Parameter Errors

| Code | Message | Solution |
|------|---------|----------|
| 106013 | Missing shop_cipher | Get from Get Authorized Shops |
| 36009004 | Unexpected shop_cipher | Remove if not required |
| 36009004 | Invalid shop_id | Get from Get Authorized Shops |
| 36009004 | Invalid API version | Check API docs |
| 36004004 | Invalid auth code | Code used, expired, or invalid |

## Content Types

- `application/json` - for most API calls
- `multipart/form-data` - for file uploads (images, videos, documents)

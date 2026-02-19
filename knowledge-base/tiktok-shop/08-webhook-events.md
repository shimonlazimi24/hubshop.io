# TikTok Shop - Complete Webhook Event Catalog

## Overview

TikTok Shop webhooks deliver real-time HTTPS POST notifications for platform events. 32 event types across 10 categories.

## Common Payload Structure

| Field | Type | Description |
|-------|------|-------------|
| `type` | int | Numeric ID identifying the webhook topic |
| `tts_notification_id` | string | Unique notification ID |
| `shop_id` | string | TikTok Shop identifier |
| `timestamp` | int | Unix timestamp (seconds) |
| `data` | object | Event-specific business parameters |

## Signature Verification

HMAC-SHA256 signature sent in `Authorization` header:
```
HMAC-SHA256(app_secret, app_key + payload_body)
```

## Retry Policy

| Retry | Timing |
|-------|--------|
| 1st | 2 minutes after failure |
| 2nd | 30 minutes after 1st retry |
| 3rd | 3 hours after 2nd retry |
| 4th (final) | 12 hours after 3rd retry |

## Configuration Methods

1. **Partner Center UI**: Add HTTPS URL in "Developing" tab, select webhook topics
2. **Event API**: `Update Shop Webhook`, `Get Shop Webhooks`, `Delete Shop Webhook`

**Requirements:** HTTPS only, TLS v1.2+, domain name only (no IP/port), respond within 3 seconds with HTTP 200.

---

## Event Catalog

### ORDER (2 events)

| Type | Event | Trigger |
|------|-------|---------|
| 1 | Order Status Change | `order_status` changes: `UNPAID`, `ON_HOLD`, `AWAITING_SHIPMENT`, `AWAITING_COLLECTION`, `CANCEL`, `IN_TRANSIT`, `DELIVERED`, `COMPLETED` |
| 11 | Cancellation Status Change | `cancel_status` changes. Roles: `BUYER`, `SELLER`, `SYSTEM` |

### LOGISTICS (2 events)

| Type | Event | Trigger |
|------|-------|---------|
| 3 | Recipient Address Update | Order recipient address is updated |
| 4 | Package Update | Package combine, split, cancel operations |

### PRODUCT (12 events)

| Type | Event | Trigger |
|------|-------|---------|
| 5 | Product Status Change | Product audit status changes |
| 15 | Product Information Change | Live product properties change. Source: `SELLER_CENTER` or `OPEN_API` |
| 16 | Product Creation | New product created |
| 18 | Product Category Change | Product category changed |
| 19 | Size Chart Change | Size chart modified |
| 25 | Opportunity Matching Status Change | Opportunity matching status changes |
| 27 | Inventory Status Change | Inventory status changes |
| 37 | Product Audit Status Change | Audit status changes (without Get Product API call) |
| 38 | Strikethrough Price Expired | Strikethrough pricing verification expires (90 days) |
| 42 | Combined Listing Change | Combined listing created/updated/deleted |
| 46 | Image Translation Completed | Image translation completes/fails (EU cross-border only) |
| 51 | Global Replication Status Change | Global product replication status changes |
| 52 | Global Listing Method Change | Global listing method changes |

### RETURN AND REFUND (1 event)

| Type | Event | Trigger |
|------|-------|---------|
| 12 | Return Status Change | `return_status` changes. Types: `REFUND`, `REPLACEMENT`, `RETURN_AND_REFUND`. Roles: `BUYER`, `SELLER`, `SYSTEM` |

### SELLER (3 events)

| Type | Event | Trigger |
|------|-------|---------|
| 6 | Seller Deauthorization | Seller deauthorizes app |
| 7 | Upcoming Authorization Expiration | 30 days before authorization expires |
| 35 | Tokopedia Mirror Status Change | TikTok Shop to Tokopedia mirroring status |

### FULFILLMENT (1 event)

| Type | Event | Trigger |
|------|-------|---------|
| 36 | Invoice Status Change | Invoice upload status changes |

### FULFILLED BY TIKTOK (4 events)

| Type | Event | Trigger |
|------|-------|---------|
| 21 | Inbound FBT Order Status Change | FBT order status changes |
| 22 | FBT Merchant Onboarding | Seller onboards FBT platform |
| 23 | Goods Match | Seller matches/unmatches product to FBT Goods |
| 24 | FBT Inventory Update | FBT inventory changes |

### CUSTOMER SERVICE (2 events)

| Type | Event | Trigger |
|------|-------|---------|
| 13 | New Conversation | CS agent joins/leaves conversation |
| 14 | New Message | New message in CS conversation |

### AFFILIATE CREATOR (4 events)

| Type | Event | Trigger |
|------|-------|---------|
| 17 | Shoppable Content Posting | Creator adds/updates/removes product link in video/livestream |
| 20 | Creator Deauthorization | Creator deauthorizes app |
| 55 | Video Precheck Result | Video precheck result available |
| 59 | Shoppable Video Precheck Tasks Result | Shoppable video precheck tasks complete |

### AFFILIATE SELLER (2 events)

| Type | Event | Trigger |
|------|-------|---------|
| 33 | New Message Listener | New message in seller-creator IM |
| 56 | Sample Application Status Change | Creator sample application status changes |

### PROMOTION (1 event)

| Type | Event | Trigger |
|------|-------|---------|
| 39 | Activity Status Change | Promotion activity status changes |

# TikTok Shop - Webhooks

## Overview

Real-time HTTP POST notifications over HTTPS to subscribed endpoints when business events occur.

## How It Works

1. App subscribes to a topic (e.g., "Order Status Update") for a shop
2. App specifies an HTTPS endpoint to receive events
3. An event occurs (e.g., order created or status changed)
4. Event published to the topic
5. TikTok Shop sends webhook with payload to registered endpoint

## Common Webhook Events

- Order status updates
- Order recipient address updates
- Return status updates
- Product status updates
- New customer service conversation
- New customer service message
- FBT order status change
- FBT inventory update
- Goods match updates

## Webhook URL Requirements

- Must use `https://` scheme
- Must use TLS v1.2+
- Must be a domain name (not IP address)
- No port number allowed
- Return 200 for success, 401 for auth failure
- Respond within 3 seconds

## Webhook Payload

### Header
- Signature placed in `Authorization` HTTP header
- Signature = HMAC-SHA256(key=app_secret, message=`{app_key}{webhook_payload}`)

### Body Parameters

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `type` | int | `1` | Notification type identifier |
| `shop_id` | string | `123455` | TikTok Shop identification |
| `timestamp` | int | `1627587506` | Push timestamp |
| `data` | object | `{"order_id": "1X2X3X4X5", "order_status": "CANCEL", "update_time": 1627587505}` | Business data |

## Configuration Methods

### Method 1: Partner Center UI

1. Navigate to "Developing" tab > "Basic information"
2. Add HTTP Server URL
3. Auto-subscribed to default webhooks
4. Manage subscriptions in "Developing" tab

### Method 2: Event API

| Operation | Description |
|-----------|-------------|
| Update Shop Webhook | Create/update webhook for a shop event |
| Get Shop Webhooks | Get all shop webhook configurations |
| Delete Shop Webhook | Cancel a webhook for a shop event |

## Retry Policy

| Retry | Timing |
|-------|--------|
| Initial push | Immediate |
| 1st retry | 2 minutes after failure |
| 2nd retry | 30 minutes after 1st retry |
| 3rd retry | 3 hours after 2nd retry |
| 4th retry (final) | 12 hours after 3rd retry |

After 4th retry failure, the notification is discarded.

## Webhook Signature Verification (Python)

```python
import hmac
import hashlib
import json

def verify_webhook(app_key: str, app_secret: str, authorization_header: str, body: str) -> bool:
    """Verify TikTok Shop webhook signature."""
    message = f"{app_key}{body}"
    expected_signature = hmac.new(
        app_secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, authorization_header)
```

## Important Notes

- Cannot completely rely on webhooks due to network issues
- Must implement fallback polling (e.g., scheduled tasks to pull orders)
- Webhook history available at Partner Console > Development Kits > Webhook Log
- SDK does NOT support webhook processing (webhooks are separate)

# TikTok Developer - Webhooks

## Overview

TikTok Webhooks deliver event-driven HTTPS POST notifications in JSON format, eliminating the need for continuous API polling. They enable real-time notification when specific events occur within the TikTok platform.

## Configuration

- Callback URL must be **HTTPS only**
- Configured through the Developer Portal during app creation or updates
- Must immediately respond with **HTTP 200** to acknowledge receipt

## Delivery & Reliability

- **Delivery guarantee**: At least once delivery
- **Retry policy**: Exponential backoff retries for up to **72 hours** if non-200 responses occur
- **After 72 hours**: Undelivered notifications are discarded
- **Idempotency required**: Endpoints may receive the same event more than once; guard against duplicated event processing

---

## Webhook Event Types

### 1. `authorization.removed`

**Trigger:** User deauthorizes your application or account status changes.

**Payload:**

```json
{
  "client_key": "string",
  "event": "authorization.removed",
  "create_time": 1615338610,
  "user_openid": "string",
  "content": "{\"reason\": 1}"
}
```

**Reason Codes:**

| Code | Description |
|------|-------------|
| 0 | Unknown |
| 1 | User disconnects from TikTok app |
| 2 | Account deletion |
| 3 | Age change |
| 4 | Account ban |
| 5 | Developer revocation |

### 2. `video.upload.failed`

**Trigger:** Video uploaded via Video Kit fails to upload to TikTok.

**Payload:**

```json
{
  "client_key": "bwo2m45353a6k85",
  "event": "video.upload.failed",
  "create_time": 1615338610,
  "user_openid": "act.example12345Example12345Example",
  "content": "{\"share_id\":\"video.6974245311675353080.VDCxrcMJ\"}"
}
```

### 3. `video.publish.completed`

**Trigger:** Video uploaded via Video Kit is published by user on TikTok.

**Payload:**

```json
{
  "client_key": "bwo2m45353a6k85",
  "event": "video.publish.completed",
  "create_time": 1615338610,
  "user_openid": "act.example12345Example12345Example",
  "content": "{\"share_id\":\"video.6974245311675353080.VDCxrcMJ\"}"
}
```

### 4. `portability.download.ready`

**Trigger:** Data portability request enters the downloading state (data is ready for download).

**Payload:**

```json
{
  "client_key": "developer_client_key",
  "event": "portability.download.ready",
  "create_time": 1615338610,
  "content": "{\"request_id\":123123123123123}"
}
```

**Content field:** `request_id` (int64) - unique identifier tracking the download request.

---

## Common Webhook Payload Structure

All webhook events follow the same base format:

| Field | Type | Description |
|-------|------|-------------|
| `client_key` | string | Your application's client key |
| `event` | string | Event type identifier |
| `create_time` | integer | Unix timestamp of event creation |
| `user_openid` | string | User's open ID (not present in all events) |
| `content` | string | Serialized JSON string with event-specific data |

---

## Webhook Signature Verification

TikTok includes a `TikTok-Signature` header with each webhook delivery for security verification.

### Signature Header Format

```
TikTok-Signature: t=1633174587,s=18494715036ac4416a1d0a673871a2edbcfc94d94bd88ccd2c5ec9b3425afe66
```

- `t` = Unix timestamp
- `s` = HMAC-SHA256 signature value

### Verification Steps

**Step 1: Parse the header**
Split by commas, then by equals signs to extract timestamp (`t`) and signature (`s`).

**Step 2: Construct signed payload**
Concatenate: `{timestamp}.{raw_json_request_body}`

Example:
```
1633174587.{"event":"user.login.mobile","timestamp":1633174587}
```

**Step 3: Generate HMAC**
Create HMAC-SHA256 using:
- **Key**: Your `client_secret`
- **Message**: The signed payload from Step 2

**Step 4: Compare and validate**
- Compare your generated signature against the header's `s` value
- Verify the timestamp is not excessively old (replay attack prevention)

### Security Recommendations

- Always validate signatures before processing webhook data
- The timestamp inclusion in the signed payload prevents replay attacks
- Reject webhooks with timestamps older than a reasonable threshold (e.g., 5 minutes)

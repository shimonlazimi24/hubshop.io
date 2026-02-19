# TikTok Shop - Authentication & Authorization

## Overview

TikTok Shop uses a two-layer authentication:
1. **API Signature** (HMAC-SHA256) - validates every request
2. **Access Token** - authorizes access to seller data

## Mandatory Query Parameters

Every API call requires:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `app_key` | string | Unique key assigned to your app | `29a39d` |
| `sign` | string | HMAC-SHA256 hash for request verification | `bc721f0e01829...` |
| `timestamp` | Unix timestamp | 10-digit Unix epoch. Valid: [now - 5min, now + 30sec] | `1623812664` |

## Access Token

- Passed as `x-tts-access-token` HTTP header
- Format: `TTP_pwSm2AAAA...`
- Obtained via OAuth authorization flow (Get Access Token API)
- Must be refreshed before expiry using Get Refresh Token endpoint

## Signing Algorithm (HMAC-SHA256)

### Step-by-Step

1. Extract all query parameters **excluding** `sign` and `access_token`
2. Sort parameter keys **alphabetically**
3. Concatenate as `{key}{value}` pairs (e.g., `app_key29a39dtimestamp1623812664`)
4. Prepend the API request path: `/authorization/202309/shops` + concatenated params
5. If Content-Type is NOT `multipart/form-data`, append the request body
6. Wrap with app_secret: `{app_secret}{string}{app_secret}`
7. Compute HMAC-SHA256 of the wrapped string using app_secret as key

### Python Example

```python
import hmac
import hashlib
import time

def generate_sign(app_secret: str, path: str, params: dict, body: str = "") -> str:
    """Generate HMAC-SHA256 signature for TikTok Shop API."""
    # Step 1-2: Sort and exclude sign/access_token
    sorted_params = sorted(
        [(k, v) for k, v in params.items() if k not in ("sign", "access_token")]
    )

    # Step 3: Concatenate key-value pairs
    param_str = "".join(f"{k}{v}" for k, v in sorted_params)

    # Step 4: Prepend path
    base_string = f"{path}{param_str}"

    # Step 5: Append body (if not multipart)
    base_string += body

    # Step 6: Wrap with app_secret
    sign_string = f"{app_secret}{base_string}{app_secret}"

    # Step 7: HMAC-SHA256
    signature = hmac.new(
        app_secret.encode("utf-8"),
        sign_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return signature
```

### Go Example

```go
func CalSign(appSecret, path string, params map[string]string, body string) string {
    keys := make([]string, 0, len(params))
    for k := range params {
        if k != "sign" && k != "access_token" {
            keys = append(keys, k)
        }
    }
    sort.Strings(keys)

    var builder strings.Builder
    builder.WriteString(path)
    for _, k := range keys {
        builder.WriteString(k)
        builder.WriteString(params[k])
    }
    builder.WriteString(body)

    signStr := appSecret + builder.String() + appSecret
    h := hmac.New(sha256.New, []byte(appSecret))
    h.Write([]byte(signStr))
    return hex.EncodeToString(h.Sum(nil))
}
```

### Node.js Example

```typescript
import crypto from "crypto";

function generateSign(
  appSecret: string,
  path: string,
  params: Record<string, string>,
  body: string = ""
): string {
  const sortedKeys = Object.keys(params)
    .filter((k) => k !== "sign" && k !== "access_token")
    .sort();

  const paramStr = sortedKeys.map((k) => `${k}${params[k]}`).join("");
  const baseString = `${path}${paramStr}${body}`;
  const signString = `${appSecret}${baseString}${appSecret}`;

  return crypto
    .createHmac("sha256", appSecret)
    .update(signString)
    .digest("hex");
}
```

## Common Signature Mistakes

- Using incorrect app keys/secrets
- Including `sign` or `access_token` in the signature computation
- Using regular SHA-256 instead of HMAC-SHA256
- Timestamp not within valid range (now - 5min to now + 30sec)
- Not using 10-digit Unix timestamp
- Not appending request body for non-multipart requests

## Access Scopes

### Public Scopes (available by default)

| Scope | Description |
|-------|-------------|
| Shop Authorized Information | Access seller's shop ID(s) |
| Product Basic | Sync product information |
| Product Modify | Manage products (listing, edit, status, inventory) |
| Product Delete & Recover | Delete and recover products |
| Order Information | Real-time access to all order data |
| Fulfillment Basic | Fulfill and manage orders |
| Package Split And Combine | Split and combine orders |
| Update Delivery Status | Push package to delivered (3PL) |
| Logistics Basic | Get logistics and warehouse info |
| Return & Refund Basic | Manage return and refund requests |
| Finance Information | Access transaction/settlement info |
| Promotion Information | Obtain promotion list and details |
| Promotion Modify | Create and manage promotions |
| Global Shop Information | Access global shop info |
| Global Product Information | Access global product info |
| Global Product Modify | Manage global products |
| Global Product Delete | Delete global products |
| Global Category Information | Access global product categories |

### Custom Scopes
- Contain sensitive data
- Apply via Partner Center > App & Service > Manage > Manage API
- Require approval from TikTok Shop team

## Error Codes (Authentication)

| Code | Message | Solution |
|------|---------|----------|
| 101000 | Invalid access token | Token invalid, shop mismatch, or wrong user_type |
| 105002 | Expired credentials | Refresh token using Get Refresh Token endpoint |
| 105005 | Access denied | Check granted scopes, reauthorize if needed |
| 106001 | Invalid sign parameter | Regenerate signature |
| 36009004 | Missing/invalid signature | Generate proper signature |
| 36009004 | Invalid app_key | Check format, app status, Partner Center |
| 36009004 | Invalid timestamp | Must be [now - 5min, now + 30sec] |
| 36009033 | IP not in allow list | Add IP in Partner Center |

# TikTok Developer - Rate Limits

## Rate Limit Model

Rate limits are calculated using a **one-minute sliding window**.

## Per-Endpoint Rate Limits

| Endpoint | Rate Limit |
|----------|------------|
| `/v2/user/info/` | 600 requests/minute |
| `/v2/video/query/` | 600 requests/minute |
| `/v2/video/list/` | 600 requests/minute |
| Content Posting (Direct Post init) | 6 requests/minute per user access token |

## Throttling Behavior

- When limits are exceeded, the API responds with:
  - **HTTP Status**: `429`
  - **Error Code**: `rate_limit_exceeded`

## Content Posting Limits

- Each user `access_token` is limited to **6 requests per minute** for the direct post endpoint
- Daily post caps are enforced **per user** and **per client**
- Unaudited clients are restricted to private account posting only

## Increasing Rate Limits

To request higher limits:
1. Contact TikTok via their Support Page
2. Provide justification for increased limits
3. TikTok will review the request
4. If approved, rate limits will be increased

## Notes

- No documented differences between sandbox and production rate limits
- No documented daily or monthly aggregate quotas (beyond content posting daily caps)
- No documented rate limit response headers (X-RateLimit-* style headers)
- No documented burst allowance or grace periods

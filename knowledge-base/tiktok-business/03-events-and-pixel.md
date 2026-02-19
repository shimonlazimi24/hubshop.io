# TikTok Events API & Pixel - Ad Measurement

## Overview

TikTok provides multiple methods for tracking user actions and attributing conversions back to ad campaigns. The primary tools are:

1. **Events API 2.0** - Server-side event tracking (recommended, current version)
2. **Events API 1.0** - Legacy server-side tracking
3. **TikTok Pixel** - Client-side JavaScript tracking
4. **TikTok App Events SDK** - Mobile app event tracking
5. **Events API Gateway** - Self-hosted proxy for event data

The recommended setup is **dual implementation**: Events API (server-side) + Pixel (client-side) with event deduplication.

---

## Events API 2.0 (Conversions API)

### Purpose

Server-side event tracking that sends conversion events directly from your server to TikTok. This is TikTok's equivalent of Meta's Conversions API. It provides more reliable attribution than client-side tracking alone, especially with increasing browser privacy restrictions.

### Base URL

```
https://business-api.tiktok.com/open_api/v2/event/track/
```

### Authentication

Uses the standard Marketing API `Access-Token` header.

### Event Types

Events API 2.0 supports four event source types:

| Source | Description | Use Case |
|---|---|---|
| **Web** | Website conversion events | E-commerce, lead gen, sign-ups |
| **App** | Mobile app events | App installs, in-app purchases |
| **Offline** | Offline conversion events | In-store purchases, phone orders |
| **CRM** | CRM lifecycle events | Lead status updates, pipeline events |

### Single Unified Endpoint

```
POST /v2/event/track/
```

Unlike Events API 1.0 which had separate endpoints per source, v2.0 uses a single endpoint with the `event_source` parameter to distinguish the source type.

### Key Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `event_source` | string | Yes | `web`, `app`, `offline`, `crm` |
| `event_source_id` | string | Yes | Pixel ID (web), App ID (app), Offline Event Set ID, CRM Event Set ID |
| `data` | array | Yes | Array of event objects |

### Event Object Structure (Web)

```json
{
  "event_source": "web",
  "event_source_id": "PIXEL_ID",
  "data": [
    {
      "event": "CompletePayment",
      "event_time": 1672531200,
      "event_id": "unique_event_id_for_dedup",
      "user": {
        "ttclid": "tiktok_click_id",
        "ttp": "tiktok_cookie_value",
        "external_id": "hashed_user_id",
        "email": "hashed_email",
        "phone": "hashed_phone",
        "ip": "user_ip_address",
        "user_agent": "user_agent_string"
      },
      "properties": {
        "contents": [
          {
            "content_id": "product_123",
            "content_type": "product",
            "content_name": "Product Name",
            "quantity": 1,
            "price": 29.99
          }
        ],
        "currency": "USD",
        "value": 29.99
      },
      "page": {
        "url": "https://example.com/checkout",
        "referrer": "https://example.com/cart"
      }
    }
  ]
}
```

### Supported Web Events

| Event | Description |
|---|---|
| `ViewContent` | User views a product/content page |
| `ClickButton` | User clicks a button |
| `Search` | User performs a search |
| `AddToWishlist` | User adds item to wishlist |
| `AddToCart` | User adds item to cart |
| `InitiateCheckout` | User starts checkout process |
| `AddPaymentInfo` | User adds payment information |
| `CompletePayment` | User completes a purchase |
| `PlaceAnOrder` | User places an order |
| `Contact` | User initiates contact |
| `Download` | User downloads content |
| `SubmitForm` | User submits a form |
| `CompleteRegistration` | User completes registration |
| `Subscribe` | User subscribes |
| `CustomEvent` | Custom-defined event |

### Supported App Events

| Event | Description |
|---|---|
| `InstallApp` | App install |
| `LaunchAPP` | App launch |
| `CompleteTutorial` | Tutorial completion |
| `CreateGroup` | Group creation |
| `JoinGroup` | Group join |
| `CreateGuestAccount` | Guest account creation |
| `AchieveLevel` | Level achievement |
| `SpendCredits` | Credit spending |
| `UnlockAchievement` | Achievement unlock |
| `Login` | User login |
| `Rate` | User rates something |
| (Plus all web events) | |

### User Matching Parameters

For attribution, TikTok matches events to ad clicks using these identifiers (in priority order):

| Parameter | Description | Hashing |
|---|---|---|
| `ttclid` | TikTok Click ID (from URL parameter) | Not hashed |
| `ttp` | TikTok `_ttp` cookie value | Not hashed |
| `external_id` | Your user ID | SHA-256 hashed |
| `email` | User email | SHA-256 hashed |
| `phone` | User phone number | SHA-256 hashed |
| `ip` | IP address | Not hashed |
| `user_agent` | Browser user agent | Not hashed |

### TikTok Click ID (ttclid)

When a user clicks a TikTok ad, the `ttclid` parameter is appended to the landing page URL:
```
https://example.com/landing?ttclid=E.C.P.xxx
```

You should:
1. Capture `ttclid` from the URL on landing
2. Store it in a first-party cookie or server-side session
3. Send it with every Events API call for that user

### TikTok Cookie (_ttp)

The TikTok Pixel sets a first-party cookie `_ttp` on the user's browser. This should be captured and sent with server-side events for enhanced matching.

### External ID

A stable, unique identifier for the user in your system. Must be SHA-256 hashed before sending.

### Event Deduplication

When using both Pixel and Events API, events may be reported twice. TikTok deduplicates using:

1. **Event ID**: Set the same `event_id` in both Pixel and Events API calls for the same event
2. **Deduplication Window**: TikTok deduplicates events with the same `event_id` within 48 hours

```javascript
// Pixel side
ttq.track('CompletePayment', {
  event_id: 'order_12345',
  // ... other params
});
```

```json
// Events API side
{
  "event": "CompletePayment",
  "event_id": "order_12345"
}
```

### Events API for Offline

Send offline conversion data (e.g., in-store purchases) for attribution:

```json
{
  "event_source": "offline",
  "event_source_id": "OFFLINE_EVENT_SET_ID",
  "data": [
    {
      "event": "CompletePayment",
      "event_time": 1672531200,
      "user": {
        "email": "hashed_email",
        "phone": "hashed_phone"
      },
      "properties": {
        "currency": "USD",
        "value": 150.00
      }
    }
  ]
}
```

### Events API for CRM

Send CRM lifecycle events for lead quality optimization:

```json
{
  "event_source": "crm",
  "event_source_id": "CRM_EVENT_SET_ID",
  "data": [
    {
      "event": "QualifiedLead",
      "event_time": 1672531200,
      "user": {
        "external_id": "hashed_lead_id",
        "email": "hashed_email"
      }
    }
  ]
}
```

### Payload Helper

TikTok provides a Payload Helper tool that:
- Validates your event payloads before sending
- Helps construct properly formatted requests
- Available for both Web and App event sources

### Payload Converter

Converts Events API 1.0 payloads to 2.0 format for migration.

### Limited Data Use

For privacy compliance (e.g., CCPA), you can set the `limited_data_use` flag:

```json
{
  "data": [
    {
      "limited_data_use": true,
      // ... event data
    }
  ]
}
```

### Events API 2.0 vs 1.0 Differences

| Feature | Events API 1.0 | Events API 2.0 |
|---|---|---|
| Endpoint | Separate per source type | Single unified endpoint |
| Event sources | Web, App, Offline | Web, App, Offline, CRM |
| Authentication | Access-Token | Access-Token |
| Payload format | Source-specific | Unified format |

---

## Events API 1.0 (Legacy)

### Web Events

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/pixel/track/` | POST | Report a web event |
| `/v1.3/pixel/batch/` | POST | Report web events in bulk |

### App Events

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/app/event/` | POST | Report an app event |
| `/v1.3/app/batch/` | POST | Report app events in bulk |

### Offline Events

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/offline/event/` | POST | Report an offline event |
| `/v1.3/offline/batch/` | POST | Report offline events in bulk |

### Offline Event Set Management

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/offline/create/` | POST | Create an offline event set |
| `/v1.3/offline/update/` | POST | Update an offline event set |
| `/v1.3/offline/delete/` | POST | Delete an offline event set |
| `/v1.3/offline/get/` | GET | Get offline event sets |

### App Management

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/app/get/` | GET | Get app info |
| `/v1.3/app/create/` | POST | Create an app |
| `/v1.3/app/update/` | POST | Update an app |
| `/v1.3/app/list/` | GET | Get app list |
| `/v1.3/app/conversion_event/` | GET | Get app conversion events |
| `/v1.3/app/retargeting_event/` | GET | Get app retargeting events |

### CRM Events

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/crm/event_set/get/` | GET | Get CRM event sets |

### CTM (Click-to-Message) Events

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/ctm/event_set/get/` | GET | Get message event sets for ad creation |

---

## TikTok Pixel (Client-Side)

### Purpose

JavaScript-based tracking code that runs in the user's browser to capture website events and send them to TikTok for ad attribution and optimization.

### Installation Methods

#### 1. Manual Code Installation

Add the base pixel code to your website's `<head>`:

```html
<script>
!function (w, d, t) {
  w.TiktokAnalyticsObject=t;
  var ttq=w[t]=w[t]||[];
  ttq.methods=["page","track","identify","instances","debug","on","off","once","ready","alias","group","enableCookie","disableCookie"];
  ttq.setAndDefer=function(t,e){t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}};
  for(var i=0;i<ttq.methods.length;i++)ttq.setAndDefer(ttq,ttq.methods[i]);
  ttq.instance=function(t){for(var e=ttq._i[t]||[],n=0;n<ttq.methods.length;n++)ttq.setAndDefer(e,ttq.methods[n]);return e};
  ttq.load=function(e,n){var i="https://analytics.tiktok.com/i18n/pixel/events.js";ttq._i=ttq._i||{};ttq._i[e]=[];ttq._i[e]._u=i;ttq._t=ttq._t||{};ttq._t[e+\"_\"+n]=+new Date;(function(o,u){var a=d.createElement("script");a.type="text/javascript";a.async=!0;a.src=i+"?sdkid="+e+"&lib="+t;var s=d.getElementsByTagName("script")[0];s.parentNode.insertBefore(a,s)})(w,d,"script",i,t)};

  ttq.load('PIXEL_ID');
  ttq.page();
}(window, document, 'ttq');
</script>
```

#### 2. Google Tag Manager (GTM)

TikTok provides a GTM template for easier integration:
- TikTok Pixel only setup
- Combined Events API + Pixel setup
- Supports data layer integration

### Pixel Event Tracking

```javascript
// Standard event
ttq.track('CompletePayment', {
  content_type: 'product',
  content_id: '301',
  content_name: 'Product Name',
  quantity: 1,
  price: 29.99,
  value: 29.99,
  currency: 'USD'
});

// Page view (automatic with ttq.page())
ttq.page();

// Custom event
ttq.track('CustomEvent', {
  // custom parameters
});
```

### Supported Pixel Events

| Event | Description |
|---|---|
| `ViewContent` | Content/product page view |
| `ClickButton` | Button click |
| `Search` | Search action |
| `AddToWishlist` | Wishlist addition |
| `AddToCart` | Cart addition |
| `InitiateCheckout` | Checkout initiation |
| `AddPaymentInfo` | Payment info added |
| `CompletePayment` | Purchase completed |
| `PlaceAnOrder` | Order placed |
| `Contact` | Contact initiated |
| `Download` | Download completed |
| `SubmitForm` | Form submitted |
| `CompleteRegistration` | Registration completed |
| `Subscribe` | Subscription completed |

### Advanced Matching

Enhanced user matching by passing additional identifiers:

```javascript
ttq.identify({
  email: 'user@example.com',       // Will be hashed automatically
  phone_number: '+1234567890',     // Will be hashed automatically
  external_id: 'user_123'          // Will be hashed automatically
});
```

### Cookie Consent Mode

For GDPR/privacy compliance:

```javascript
// Disable cookies until consent
ttq.disableCookie();

// Enable cookies after consent
ttq.enableCookie();
```

### Single Page Application (SPA) Support

For SPAs, call `ttq.page()` on route changes:

```javascript
// React Router example
router.afterEach((to) => {
  ttq.page();
});
```

### Content Security Policy (CSP)

Required CSP directives for Pixel:
```
script-src: https://analytics.tiktok.com
img-src: https://analytics.tiktok.com
connect-src: https://analytics.tiktok.com
```

### Debug Mode

Enable debug mode to validate pixel firing:

```javascript
ttq.debug(true);
```

### Pixel Management via API

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/pixel/get/` | GET | Get pixels |
| `/v1.3/pixel/create/` | POST | Create a pixel |
| `/v1.3/pixel/update/` | POST | Update a pixel |
| `/v1.3/pixel/event/create/` | POST | Create pixel events |
| `/v1.3/pixel/event/update/` | POST | Update a pixel event |
| `/v1.3/pixel/event/delete/` | POST | Delete a pixel event |
| `/v1.3/pixel/event/instant_page/` | GET | Get Instant Page events |
| `/v1.3/pixel/event/stats/` | GET | Get pixel event statistics |

---

## TikTok App Events SDK

### Purpose

Native mobile SDKs for tracking in-app events for attribution and optimization. Available for:
- **Android** (Java/Kotlin)
- **iOS** (Swift/Objective-C)
- **Unity** (C#)

### Key Features

- Combined SDK with Pangle (TikTok's ad network SDK)
- Automatic install tracking
- In-app event tracking
- Deep link support
- Age gating support
- Limited Data Use compliance
- Consent management

### Supported App Events

Standard events include:
- `InstallApp`, `LaunchAPP`, `CompleteTutorial`
- `AchieveLevel`, `CreateGroup`, `JoinGroup`
- `SpendCredits`, `UnlockAchievement`
- `Login`, `Rate`
- All standard web events (AddToCart, Purchase, etc.)
- Custom events

### Integration

The App Events SDK integrates with TikTok's ad attribution system to:
1. Track app installs from TikTok ads
2. Track post-install events for optimization
3. Support SKAdNetwork (SKAN) for iOS
4. Enable retargeting audiences based on app events

---

## Events API Gateway

### Purpose

A self-hosted proxy that sits between your website and TikTok's servers, providing:
- First-party data collection
- Improved data accuracy
- Reduced reliance on third-party cookies
- Server-side event forwarding

### Features

- **Self-hosted**: Deploy on your own infrastructure
- **Tenant management**: Support multiple event sources
- **User management**: Access control
- **Pixel integration**: Works alongside client-side Pixel
- **Configurable settings**: Custom routing and filtering

### Setup

Follow the self-host setup guide to deploy on your infrastructure. The Gateway acts as a first-party endpoint that forwards events to TikTok.

---

## Custom Conversions

Custom conversions allow you to create conversion events based on URL rules or event parameters, without modifying your tracking code.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/custom_conversion/get/` | GET | Get custom conversions for an event source |
| `/v1.3/custom_conversion/detail/` | GET | Get custom conversion details |
| `/v1.3/custom_conversion/create/` | POST | Create a custom conversion |
| `/v1.3/custom_conversion/update/` | POST | Update a custom conversion |
| `/v1.3/custom_conversion/delete/` | POST | Delete a custom conversion |

---

## Best Practices

### Recommended Setup

1. **Implement both Pixel and Events API** for redundant tracking
2. **Use event deduplication** with matching `event_id` values
3. **Send `ttclid`** with every server-side event for click attribution
4. **Send `_ttp` cookie** value for cookie-based matching
5. **Hash PII data** (email, phone) with SHA-256 before sending
6. **Use Advanced Matching** for improved attribution
7. **Implement consent management** for privacy compliance

### Data Flow

```
User clicks TikTok ad
    |
    v
Landing page loads (ttclid in URL)
    |
    +-- Pixel fires ViewContent (client-side)
    |
    +-- Server captures ttclid, _ttp cookie
    |
    v
User converts (e.g., purchase)
    |
    +-- Pixel fires CompletePayment (event_id: "order_123")
    |
    +-- Server sends Events API CompletePayment (event_id: "order_123")
    |
    v
TikTok deduplicates and attributes to the ad click
```

### Verification

TikTok provides verification tools to confirm:
- Events are being received
- User matching is working
- Deduplication is functioning
- Data quality is acceptable

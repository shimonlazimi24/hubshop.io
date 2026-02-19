# Pangle - TikTok's Ad Network

## Overview

Pangle is TikTok for Business's ad network that extends TikTok advertising reach beyond TikTok itself into a network of third-party apps and websites. It is the global version of what was originally known as "Chuanshanjia" in China. Pangle allows advertisers to serve ads across a vast network of premium mobile apps, helping them reach audiences when they are not actively using TikTok.

For publishers (app developers), Pangle provides monetization through displaying ads from TikTok's advertiser base.

## Key Features

- **Extended Reach**: Access audiences across thousands of third-party apps globally
- **Same Targeting**: Use TikTok's audience targeting capabilities across the network
- **Unified Reporting**: Campaign performance across TikTok and Pangle in one dashboard
- **Ad Format Variety**: Supports multiple ad formats optimized for different app types
- **Cross-Platform**: Available for iOS and Android apps
- **Unified SDK**: Combined with TikTok App Events SDK

---

## For Advertisers

### Pangle as a Placement

In the TikTok Marketing API, Pangle is treated as a placement option when creating ad groups. Advertisers can:

1. **Automatic Placement**: Let TikTok distribute ads across TikTok and Pangle automatically
2. **Manual Placement**: Explicitly include or exclude Pangle

### Placement Configuration

When creating an ad group:

```json
POST /v1.3/adgroup/create/

{
  "advertiser_id": "advertiser_id",
  "campaign_id": "campaign_id",
  "placement_type": "PLACEMENT_TYPE_NORMAL",
  "placements": ["PLACEMENT_TIKTOK", "PLACEMENT_PANGLE"],
  // ... other settings
}
```

### Pangle-Specific API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/pangle/block_list/get/` | GET | Get the Pangle block list (blocked apps/sites) |
| `/v1.3/pangle/block_list/update/` | POST | Update the Pangle block list |
| `/v1.3/pangle/audience_package/get/` | GET | Get Pangle audience packages |

### Pangle Block List

Advertisers can maintain a block list to prevent their ads from appearing on specific Pangle network apps:

```json
GET /v1.3/pangle/block_list/get/?advertiser_id=xxx

// Response
{
  "code": 0,
  "data": {
    "block_list": [
      "app_package_name_1",
      "app_package_name_2"
    ]
  }
}
```

```json
POST /v1.3/pangle/block_list/update/

{
  "advertiser_id": "advertiser_id",
  "block_list": ["app_to_block_1", "app_to_block_2"],
  "action": "ADD"   // or "REMOVE"
}
```

### Pangle Audience Packages

Audience packages are pre-defined audience segments available specifically for Pangle placements:

```
GET /v1.3/pangle/audience_package/get/?advertiser_id=xxx
```

### Ad Formats on Pangle

| Format | Description |
|---|---|
| **Rewarded Video** | Full-screen video ads that users opt into for in-app rewards |
| **Interstitial** | Full-screen ads displayed at natural break points |
| **Native/In-Feed** | Ads that match the look and feel of the host app |
| **Banner** | Standard banner ads within apps |
| **App Open** | Ads shown when an app is opened or foregrounded |
| **Playable** | Interactive HTML5 ads (especially for gaming) |

### Reporting on Pangle Performance

When running reports, Pangle performance is available through the `placement` dimension:

```json
GET /v1.3/report/integrated/get/?
  advertiser_id=xxx&
  report_type=BASIC&
  dimensions=["placement","stat_time_day"]&
  metrics=["spend","impressions","clicks","conversions"]&
  data_level=AUCTION_ADGROUP&
  start_date=2025-01-01&
  end_date=2025-01-31
```

The `placement` dimension returns values like:
- `PLACEMENT_TIKTOK` - TikTok app
- `PLACEMENT_PANGLE` - Pangle network
- `PLACEMENT_GLOBAL_APP_BUNDLE` - Global App Bundle

### SKAN Dedicated Campaigns for Pangle

For iOS 14+ with App Tracking Transparency (ATT), TikTok supports SKAdNetwork (SKAN) dedicated campaigns per ad network:

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/campaign/skan/quota/` | GET | Get quota for SKAN Dedicated Campaign per ad network |

---

## For Publishers (App Developers)

### Pangle Publisher SDK

Pangle provides a publisher SDK for app developers who want to monetize their apps by displaying ads from the TikTok advertising ecosystem.

### SDK Platforms

| Platform | Description |
|---|---|
| **Android** | Native Android SDK |
| **iOS** | Native iOS SDK |
| **Unity** | Unity plugin for game developers |

### Combined SDK

The **TikTok App Events SDK and Pangle SDK are combined** into a single SDK package. This means:

- App developers who integrate Pangle for monetization also get event tracking
- Advertisers who integrate for tracking also get Pangle-ready
- Reduces SDK bloat and integration complexity

### Publisher Integration Features

| Feature | Description |
|---|---|
| Ad Mediation | Works with major mediation platforms |
| Waterfall/Bidding | Supports both waterfall and header bidding |
| COPPA Compliance | Age-gating and child-directed content support |
| GDPR/CCPA | Privacy compliance controls |
| Server-side Verification | Rewarded video completion verification |

### Publisher SDK Integration Steps

#### Android

1. Add Pangle SDK dependency to `build.gradle`
2. Configure AndroidManifest.xml with required permissions
3. Initialize SDK with your App ID
4. Implement ad loading and display for chosen formats
5. Handle ad lifecycle callbacks

#### iOS

1. Add Pangle SDK via CocoaPods, Carthage, or Swift Package Manager
2. Configure Info.plist with required settings
3. Initialize SDK in AppDelegate
4. Implement ad loading and display
5. Handle ad lifecycle delegates

#### Unity

1. Import Pangle Unity plugin
2. Configure platform-specific settings
3. Initialize SDK
4. Implement ad loading and display via C# scripts
5. Handle ad lifecycle events

---

## Pangle Network Coverage

### Geographic Availability

Pangle is available in most global markets where TikTok for Business operates, with particularly strong coverage in:

- Asia-Pacific (Japan, Southeast Asia, South Korea)
- North America
- Europe
- Middle East
- Latin America

### App Categories

The Pangle network includes apps across categories:

- Gaming (mobile games)
- Entertainment
- News and media
- Utilities
- Social
- Education
- Lifestyle
- Finance

---

## Brand Safety on Pangle

### Controls Available

| Control | Description |
|---|---|
| **Block List** | Block specific apps from showing your ads |
| **Content Categories** | Exclude specific content categories |
| **Brand Safety Partners** | Use third-party verification (IAS, DoubleVerify, etc.) |
| **Inventory Filters** | Control ad environment quality |

### Brand Safety API Integration

```json
GET /v1.3/brand_safety/get/?advertiser_id=xxx

// Returns Brand Safety Hub settings including Pangle-specific controls
```

---

## Pangle vs TikTok Placement Comparison

| Aspect | TikTok | Pangle |
|---|---|---|
| Environment | TikTok app only | Network of third-party apps |
| Ad Experience | In-feed, branded content | Various formats per host app |
| User Intent | Content discovery/entertainment | Varies by app context |
| Targeting | Full TikTok targeting | Same targeting, expanded reach |
| Cost | Typically higher CPM | Typically lower CPM |
| Engagement | Higher engagement rates | Varies by format and app |
| Scale | TikTok's user base | Extended reach beyond TikTok |
| Brand Safety | TikTok's content moderation | Block lists + third-party verification |

---

## Best Practices for Advertisers

### When to Use Pangle
- To extend reach beyond TikTok's user base
- For app promotion campaigns (rewarded video drives installs)
- When TikTok inventory is limited or expensive
- For retargeting users across the web/app ecosystem
- When optimizing for cost efficiency (lower CPMs)

### When to Avoid Pangle
- If brand safety is paramount and you cannot maintain a block list
- For brand awareness campaigns requiring premium placement control
- When your target audience is exclusively on TikTok

### Optimization Tips
1. **Start with automatic placement** - Let TikTok's algorithm decide optimal distribution
2. **Monitor placement reports** - Review TikTok vs Pangle performance separately
3. **Maintain block lists** - Regularly update to exclude low-quality placements
4. **Use placement-specific creatives** - Different formats may perform differently
5. **Test incrementally** - Enable Pangle gradually and measure incremental lift
6. **Leverage rewarded video** - Highest engagement format on Pangle for app campaigns

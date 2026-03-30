# TikTok Unified Platform Research

## Part 1: The TikTok Platform Ecosystem

### TikTok Business Platforms

|Platform                   |URL                                   |Purpose                                                                 |
|---------------------------|--------------------------------------|------------------------------------------------------------------------|
|**TikTok Business Center** |business.tiktok.com                   |Central hub — manage ads, creators, commerce, and marketing in one place|
|**TikTok Ads Manager**     |ads.tiktok.com                        |Campaign creation, budget management, targeting, reporting              |
|**TikTok API for Business**|business-api.tiktok.com/portal        |Developer API — Ads Manager, Business Center, Creator Marketplace       |
|**TikTok One**             |Via Ads Manager                       |All-in-one creative platform — creators, tools, agencies in one place   |
|**TikTok Market Scope**    |Via Ads Manager                       |Analytics platform — audience insights across the funnel                |
|**Creative Center**        |ads.tiktok.com/business/creativecenter|Trending products, hashtags, songs, ad inspiration                      |
|**TikTok Pixel**           |Via Ads Manager                       |Browser-based website event tracking                                    |
|**Events API (EAPI)**      |Via Business API                      |Server-side event tracking — web, app, offline/CRM                      |
|**TikTok Symphony**        |Via Ads Manager                       |AI-powered creative tools — dubbing, generation, optimization           |

### TikTok Shop Platforms

|Platform                 |URL                         |Purpose                                                                |
|-------------------------|----------------------------|-----------------------------------------------------------------------|
|**Seller Center**        |seller-us.tiktok.com        |Storefront management — products, orders, fulfillment, customer service|
|**Partner Center**       |partner.tiktokshop.com      |Developer hub — APIs, Widgets, app development for Shop ecosystem      |
|**Affiliate Center**     |Via Seller Center           |Creator-seller matching — commissions, campaigns, performance tracking |
|**TikTok Shop Open APIs**|partner.tiktokshop.com/docv2|Seller API, Products API, Orders API, Fulfillment API, Affiliate APIs  |

### TikTok Developer / Open Platform

|Platform                  |URL                  |Purpose                                         |
|--------------------------|---------------------|------------------------------------------------|
|**TikTok for Developers** |developers.tiktok.com|Central developer portal — all kits and APIs    |
|**Login Kit**             |Via Developer Portal |OAuth login with TikTok credentials             |
|**Share Kit**             |Via Developer Portal |Share content from your app to TikTok           |
|**Content Posting API**   |Via Developer Portal |Post videos/drafts from external apps to TikTok |
|**Display API**           |Via Developer Portal |Embed TikTok content in external apps           |
|**Commercial Content API**|Via Developer Portal |Search ads/commercial content (researchers only)|
|**Research API**          |Via Developer Portal |Academic research on public TikTok data         |

-----

## Part 2: Official TikTok GitHub Repos (all 22)

### DIRECTLY RELEVANT to Your Unified Platform

#### 1. tiktok-business-api-sdk ⭐⭐⭐

- **Link:** https://github.com/tiktok/tiktok-business-api-sdk
- **Stars:** 165 | **Language:** Python, JS, Java
- **Why:** This is your #1 repo. Official SDK for the TikTok Business API. Covers campaign creation, reporting, pixel tracking, Business Center management. Includes Python SDK, JS SDK, and Java SDK. Direct integration point for ad management automation.

#### 2. tiktok-business-ios-sdk ⭐⭐

- **Link:** https://github.com/tiktok/tiktok-business-ios-sdk
- **Stars:** 31 | **Language:** Objective-C
- **Why:** iOS event tracking SDK. If your unified platform has a mobile app or serves clients with iOS apps, this handles TikTok Pixel events natively on iOS devices. Critical for app install campaigns and in-app event tracking.

#### 3. tiktok-business-android-sdk ⭐⭐

- **Link:** https://github.com/tiktok/tiktok-business-android-sdk
- **Stars:** 22 | **Language:** Java
- **Why:** Android counterpart of the iOS SDK. Same use case — native in-app event tracking for Android. Needed if your platform supports Android app clients.

#### 4. tiktok-business-unity-sdk ⭐

- **Link:** https://github.com/tiktok/tiktok-business-unity-sdk
- **Stars:** 8 | **Language:** C#
- **Why:** Unity game engine integration. Lower priority unless you have gaming clients. Handles TikTok event tracking inside Unity-built apps.

#### 5. gtm-template-pixel ⭐⭐

- **Link:** https://github.com/tiktok/gtm-template-pixel
- **Stars:** 14 | **Language:** Smarty
- **Why:** Official Google Tag Manager template for TikTok Pixel. Essential if your unified platform manages GTM setups for e-commerce clients. Simplifies pixel deployment.

#### 6. gtm-template-eapi ⭐⭐

- **Link:** https://github.com/tiktok/gtm-template-eapi
- **Stars:** 9 | **Language:** Smarty
- **Why:** Official GTM template for TikTok Events API (server-side). Critical for server-side tracking setups via GTM Server. Pairs with the pixel template above for dual-channel tracking.

#### 7. tiktok-opensdk-ios ⭐⭐

- **Link:** https://github.com/tiktok/tiktok-opensdk-ios
- **Stars:** 134 | **Language:** Swift
- **Why:** Login Kit + Share Kit for iOS. If your platform lets users authenticate via TikTok or share content to TikTok from your app, this is needed.

#### 8. tiktok-opensdk-android ⭐⭐

- **Link:** https://github.com/tiktok/tiktok-opensdk-android
- **Stars:** 100 | **Language:** Kotlin
- **Why:** Android counterpart of the iOS OpenSDK. Same Login Kit + Share Kit functionality for Android.

#### 9. tiktok-research-api-wrapper ⭐

- **Link:** https://github.com/tiktok/tiktok-research-api-wrapper
- **Stars:** 30 | **Language:** R, Python
- **Why:** Official wrapper for TikTok Research API. Useful for competitive analysis, trending content analysis, and shop data research via the Research API’s TikTok Shop endpoints.

### NOT DIRECTLY RELEVANT (Internal Tooling / ML / Dev Tools)

|# |Repo                                                                                  |Stars|What It Is                             |Why Skip                                   |
|--|--------------------------------------------------------------------------------------|-----|---------------------------------------|-------------------------------------------|
|10|[sparkling](https://github.com/tiktok/sparkling)                                      |74   |Cross-platform infrastructure framework|Internal TikTok infra, not API-related     |
|11|[knit](https://github.com/tiktok/knit)                                                |65   |Kotlin dependency injection framework  |Internal dev tooling                       |
|12|[sparo](https://github.com/tiktok/sparo)                                              |249  |Git optimization for monorepos         |Dev tooling, no business use               |
|13|[TikTokSans](https://github.com/tiktok/TikTokSans)                                    |196  |TikTok’s open-source font              |Nice for branding, not functional          |
|14|[rush-plugins](https://github.com/tiktok/rush-plugins)                                |27   |Rush.js monorepo plugins               |Internal build tools                       |
|15|[pnpm-sync](https://github.com/tiktok/pnpm-sync)                                      |24   |PNPM dependency sync tool              |Package manager tool                       |
|16|[huvr](https://github.com/tiktok/huvr)                                                |24   |AI vision model research               |ML research, not business                  |
|17|[fast_prompt_alignment](https://github.com/tiktok/fast_prompt_alignment)              |13   |AI prompt alignment research           |ML research                                |
|18|[ts-bulk-suppress](https://github.com/tiktok/ts-bulk-suppress)                        |10   |TypeScript error suppression           |Dev tooling                                |
|19|[jest-bdd-generator](https://github.com/tiktok/jest-bdd-generator)                    |4    |BDD test generator                     |Testing tool                               |
|20|[mia-rule-engine](https://github.com/tiktok/mia-rule-engine)                          |5    |Lightweight rule engine                |Could be useful for custom logic, but niche|
|21|[spatial-video-quality-metric](https://github.com/tiktok/spatial-video-quality-metric)|4    |Video quality research                 |Research only                              |
|22|[project-impact-graph](https://github.com/tiktok/project-impact-graph)                |8    |Monorepo impact analysis               |Dev tooling                                |

-----

## Part 3: Community & Third-Party Repos Worth Using

### Must-Have for a Unified TikTok Platform

#### 1. TikTok Ads MCP Server ⭐⭐⭐

- **Link:** https://github.com/AdsMCP/tiktok-ads-mcp-server
- **Why:** MCP server for TikTok Ads API. Lets Claude interact directly with your TikTok ad accounts. Since you already use MCP integrations, this plugs right into your workflow.

#### 2. TikTok Ads MCP (Alternative) ⭐⭐⭐

- **Link:** https://github.com/ysntony/tiktok-ads-mcp
- **Why:** Another MCP server for TikTok Business API. More comprehensive — covers campaigns, reporting, audience management. Compare features with the one above and pick the best fit.

#### 3. Unofficial TikTok API (davidteather) ⭐⭐⭐

- **Link:** https://github.com/davidteather/TikTok-Api
- **Why:** The most popular unofficial TikTok API wrapper in Python. Scrape trending content, user data, video data, hashtag data. Useful for competitive intelligence and content research that the official APIs don’t cover.

#### 4. TikTokLive ⭐⭐

- **Link:** https://github.com/isaackogan/TikTokLive
- **Why:** Python library for real-time TikTok LIVE data — comments, gifts, viewer counts. If your clients use TikTok Shop LIVE selling, this captures live stream engagement data.

#### 5. ResearchTikPy ⭐⭐

- **Link:** https://github.com/HohnerJulian/ResearchTikPy
- **Why:** Clean Python wrapper for TikTok’s Research API. Easier to use than the official wrapper. Good for pulling public data for market research.

#### 6. TikTok Conversion API Tag (GTM SS) ⭐⭐

- **Link:** https://github.com/addingwell/tiktok-conversion-api-tag
- **Why:** Community-built GTM Server-Side tag for TikTok Conversions API. More flexible than the official template. Good for custom server-side tracking implementations.

#### 7. TikTok Shop Affiliate Outreach Bot ⭐⭐

- **Link:** https://github.com/Zeeshanahmad4/TikTok-Shop-Affiliate-Outreach-Bot
- **Why:** Automates creator outreach on TikTok Seller Center. Directly relevant to your TikTok Shop creator management work.

#### 8. python-tiktok (sns-sdks) ⭐

- **Link:** https://github.com/sns-sdks/python-tiktok
- **Why:** Clean Python wrapper around TikTok’s official APIs (Display, Content Posting, etc.). Good alternative to using the raw API.

#### 9. Magento2 TikTok Conversion Plugin ⭐

- **Link:** https://github.com/rishigupta121/conversion-api-tiktok
- **Why:** If any clients run Magento, this handles TikTok Pixel/CAPI integration. Niche but useful.

#### 10. TikTok Shop API (Lundehund) ⭐

- **Link:** https://github.com/Lundehund/tiktok-shop-api
- **Why:** Python wrapper for TikTok Shop product data. Search products, get trending items, export to CSV.

-----

### EXPANDED Community Repos (New Finds)

#### SHOP API SDKs & WRAPPERS

#### 11. EcomPHP/tiktokshop-php ⭐⭐⭐

- **Link:** https://github.com/EcomPHP/tiktokshop-php
- **Stars:** 198 | **Language:** PHP
- **Why:** Most complete community TikTok Shop SDK. Covers Products, Orders, Fulfillment, Auth, Webhooks. Uses API v202309+. Actively maintained (last updated Dec 2025).

#### 12. ipfans/tiktok (Go Shop SDK) ⭐⭐

- **Link:** https://github.com/ipfans/tiktok
- **Stars:** ~50 | **Language:** Go
- **Why:** Go SDK for TikTok Shop Open Platform. Covers Auth, Orders, Fulfillment, Logistics, Products. If building Go-based microservices.

#### 13. laraditz/tiktok (Laravel) ⭐⭐

- **Link:** https://github.com/laraditz/tiktok
- **Language:** PHP/Laravel
- **Why:** Laravel package for TikTok Shop API. Clean interface for shop management, orders, products, webhooks. Good if your stack uses Laravel.

#### 14. bilalyasin1616/tiktok-shop-api (Node.js) ⭐⭐

- **Link:** https://www.npmjs.com/package/@bilalyasin1616/tiktok-shop-api
- **Language:** Node.js/TypeScript
- **Why:** NPM package for TikTok Shop API. Covers auth, products, orders. Useful for JS-based integrations.

#### 15. nVuln/tiktokshop-php (Legacy API) ⭐

- **Link:** https://github.com/nVuln/tiktokshop-php
- **Language:** PHP
- **Why:** TikTok Shop SDK for pre-Sept 2023 legacy API version. Reference for older integrations or migration projects.

#### 16. prayogadhi/tiktok-api-client ⭐

- **Link:** https://github.com/prayogadhi/tiktok-api-client
- **Language:** PHP
- **Why:** Another PHP client for TikTok Shop API. Lightweight alternative.

#### 17. jianjungki/tiktok (Go Shop SDK #2) ⭐

- **Link:** https://github.com/jianjungki/tiktok
- **Language:** Go
- **Why:** Second Go SDK for TikTok Shop. Covers Auth, Orders, Fulfillment, Logistics, Products.

-----

#### MCP SERVERS (AI Integration)

#### 18. Seym0n/tiktok-mcp ⭐⭐⭐

- **Link:** https://github.com/Seym0n/tiktok-mcp
- **Stars:** 129 | **Language:** JavaScript
- **Why:** MCP server for TikTok content analysis. Analyze videos for virality factors, extract content/subtitles, chat with TikTok videos via Claude. Directly useful for your creative strategy work.

#### 19. yap-audio/tiktok-mcp ⭐⭐

- **Link:** https://github.com/yap-audio/tiktok-mcp
- **Language:** Python
- **Why:** MCP service for TikTok video discovery and metadata extraction. Search TikTok videos by keyword, extract detailed post metadata. Good for content research via Claude.

-----

#### TRACKING & ATTRIBUTION

#### 20. stape-io/tiktok-tag ⭐⭐⭐

- **Link:** https://github.com/stape-io/tiktok-tag
- **Language:** JavaScript (GTM Template)
- **Why:** Stape’s TikTok Events API Tag for GTM Server Side. Sends user data (email, phone, IP, user agent), event properties, and objects. More robust than the official GTM EAPI template. Critical for your server-side tracking setups.

#### 21. aws-samples/uploading-audiences-to-tiktok-ads ⭐⭐

- **Link:** https://github.com/aws-samples/uploading-audiences-to-tiktok-ads
- **Language:** Python/AWS
- **Why:** AWS solution for automating custom audience uploads to TikTok Ads. Hashes and uploads CRM data. Relevant for your audience sync and offline conversion workflows.

#### 22. ldsink/python-tiktok-business-api-sdk ⭐

- **Link:** https://github.com/ldsink/python-tiktok-business-api-sdk
- **Language:** Python
- **Why:** Maintained fork of the official TikTok Business API SDK. Often has bug fixes faster than the official repo.

-----

#### CONTENT SCRAPERS & DATA EXTRACTION

#### 23. Evil0ctal/Douyin_TikTok_Download_API ⭐⭐⭐

- **Link:** https://github.com/Evil0ctal/Douyin_TikTok_Download_API
- **Stars:** 16,300+ | **Language:** Python
- **Why:** Most popular TikTok data tool on GitHub. High-performance async scraper for TikTok + Douyin. Supports batch downloads, API calls. Use for creative research, competitor analysis, viral content sourcing.

#### 24. drawrowfly/tiktok-scraper ⭐⭐⭐

- **Link:** https://github.com/drawrowfly/tiktok-scraper
- **Stars:** ~3,800 | **Language:** TypeScript
- **Why:** Classic TikTok scraper. Download video posts, collect user/trend/hashtag/music feed metadata. CLI and Node.js module. Good foundation for content intelligence tools.

#### 25. HasData/tiktok-scraping ⭐⭐

- **Link:** https://github.com/HasData/tiktok-scraping
- **Language:** Python & Node.js
- **Why:** Collection of ready-to-use scripts for scraping TikTok profiles, videos, comments, search results. Structured JSON output. Good starting templates.

#### 26. bellingcat/tiktok-hashtag-analysis ⭐⭐

- **Link:** https://github.com/bellingcat/tiktok-hashtag-analysis
- **Language:** Python
- **Why:** Built by Bellingcat (OSINT). Download posts/videos by hashtag, analyze co-occurring hashtags, frequency analysis over time. Great for trend research and competitive hashtag analysis.

#### 27. stel-oberts/tiktok-trending-creators-insights ⭐⭐

- **Link:** https://github.com/stel-oberts/tiktok-trending-creators-insights
- **Language:** Python
- **Why:** Discover trending TikTok creators in any market. Rich performance metrics and recent viral content. Directly useful for your affiliate/creator discovery workflow.

#### 28. vooltex8egp/tiktok-shop-scraper ⭐⭐

- **Link:** https://github.com/vooltex8egp/tiktok-shop-scraper
- **Language:** Python
- **Why:** Extracts TikTok Shop product data — prices, ratings, sellers, availability. Use for competitive pricing analysis and product research for your Shop clients.

#### 29. AhsanRiaz786/tiktok-ads-scraper ⭐⭐

- **Link:** https://github.com/AhsanRiaz786/tiktok-ads-scraper
- **Language:** Python (Playwright)
- **Why:** Scrapes TikTok Ads Manager data. GUI to log in, extract ad creative data, engagement metrics. Useful for competitive ad intelligence and creative inspiration.

#### 30. harrychangjr/tiktok-analytics ⭐

- **Link:** https://github.com/harrychangjr/tiktok-analytics
- **Language:** Python
- **Why:** Processes TikTok Analytics exports (Overview, Content, Followers) and generates dashboards/visualizations. Useful for client reporting.

#### 31. Shorya777/tiktok-data-scraper-rag-recommender ⭐

- **Link:** https://github.com/Shorya777/tiktok-data-scraper-rag-recommender
- **Language:** Python
- **Why:** AI-powered platform using RAG to discover trending content, analyze engagement patterns, and recommend content strategies. Interesting for AI-assisted creative planning.

-----

#### LIVE STREAM TOOLS

#### 32. zerodytrash/TikTok-Live-Connector ⭐⭐⭐

- **Link:** https://github.com/zerodytrash/TikTok-Live-Connector
- **Stars:** 1,900 | **Language:** TypeScript/Node.js
- **Why:** Real-time TikTok LIVE events — comments, gifts, viewers, shares. WebSocket-based. Essential if your clients do TikTok Shop LIVE selling. Most popular Node.js option.

#### 33. steampoweredtaco/gotiktoklive ⭐

- **Link:** https://github.com/steampoweredtaco/gotiktoklive
- **Language:** Go
- **Why:** Go port of TikTokLive. Download livestreams, receive events in real-time. If building Go microservices for LIVE monitoring.

#### 34. petersvp/TikTokLiveTool ⭐

- **Link:** https://github.com/petersvp/TikTokLiveTool
- **Language:** C#
- **Why:** GUI tool that processes TikTok LIVE data in real-time. Categorizes events, outputs to flat files. Good for non-technical team members monitoring LIVE sessions.

-----

#### VIDEO UPLOAD & SCHEDULING

#### 35. wkaisertexas/tiktok-uploader ⭐⭐⭐

- **Link:** https://github.com/wkaisertexas/tiktok-uploader
- **Stars:** ~1,500 | **Language:** Python (Playwright)
- **Why:** Most popular automated TikTok video uploader. Schedule uploads, set hashtags, manage descriptions. Good for content automation workflows.

#### 36. makiisthenes/TiktokAutoUploader ⭐⭐

- **Link:** https://github.com/makiisthenes/TiktokAutoUploader
- **Language:** Python
- **Why:** Schedule videos for multiple accounts, 20 days to 2 years ahead. Auto-source from YouTube/Reddit/X. Multi-account management.

#### 37. haziq-exe/TikTokAutoUploader ⭐⭐

- **Link:** https://github.com/haziq-exe/TikTokAutoUploader
- **Language:** Python
- **Why:** Updated Feb 2026. Upload with favorited sounds, hashtags, VPN support, Telegram notifications. Copyright check feature.

#### 38. jtayped/tiktok-manager ⭐

- **Link:** https://github.com/jtayped/tiktok-manager
- **Language:** Python (Selenium)
- **Why:** Manage MULTIPLE TikTok accounts. Generate short-form clips from YouTube videos with FFmpeg. Schedule in advance. Good for client content management.

#### 39. wanghaisheng/tiktoka-studio-uploader ⭐

- **Link:** https://github.com/wanghaisheng/tiktoka-studio-uploader
- **Language:** Python
- **Why:** Bulk batch upload and scheduling across platforms. Uses Playwright/Selenium. Cross-platform publishing tool.

-----

#### E-COMMERCE CONNECTORS

#### 40. m2eteam/tiktok-shop-adobe-commerce ⭐⭐

- **Link:** https://github.com/m2eteam/tiktok-shop-adobe-commerce
- **Language:** PHP (Magento 2)
- **Why:** M2E’s official Magento 2 extension for TikTok Shop. Inventory upload, automatic sync, order management. Trusted by Adobe Commerce marketplace.

#### 41. AfterShip/tiktok-shop ⭐

- **Link:** https://github.com/AfterShip/tiktok-shop
- **Language:** PHP (Magento 2)
- **Why:** AfterShip’s TikTok Shop extension for Magento 2. From a well-known e-commerce company. Order tracking integration.

-----

#### ADS AUDIT & OPTIMIZATION

#### 42. AgriciDaniel/claude-ads ⭐⭐⭐

- **Link:** https://github.com/AgriciDaniel/claude-ads
- **Language:** Claude Code Skill
- **Why:** Paid advertising audit & optimization skill for Claude Code. 186 checks across Google Ads, Meta Ads, TikTok Ads, LinkedIn, YouTube, Microsoft. Directly relevant to your agency audit work. Can plug into your Claude workflow.

#### 43. Marcos8060/Campaign_Performance_Prediction ⭐

- **Link:** https://github.com/Marcos8060/Campaign_Performance_Prediction
- **Language:** Python
- **Why:** ML system for managing campaigns across multiple ad platforms (including TikTok). Handles different APIs, data schemas, rate limits. Reference architecture.

-----

#### GO & ALTERNATIVE LANGUAGE SDKs

#### 44. HiWay-Media/tiktok-go-sdk ⭐

- **Link:** https://github.com/HiWay-Media/tiktok-go-sdk
- **Language:** Go
- **Why:** Go SDK for TikTok’s Developer API (not Shop). Content Posting, Display, Login Kit.

#### 45. hung12ct/go-tiktok-business-sdk ⭐

- **Link:** https://github.com/hung12ct/go-tiktok-business-sdk
- **Language:** Go
- **Why:** Go library for TikTok Business API. Lightweight alternative for Go-based ad management tools.

#### 46. lanrenbulan/tiktok-open-api ⭐

- **Link:** https://github.com/lanrenbulan/tiktok-open-api
- **Language:** Go
- **Why:** TikTok Open API SDK in Go. General-purpose wrapper.

-----

#### AUTOMATION & ENGAGEMENT

#### 47. sudoguy/tiktokpy ⭐⭐

- **Link:** https://github.com/sudoguy/tiktokpy
- **Stars:** 838 | **Language:** Python
- **Why:** Tool for automated TikTok interactions. Updated Feb 2026. Can be used for engagement automation research.

#### 48. soualahmohammedzakaria/TikTok-Automation ⭐

- **Link:** https://github.com/soualahmohammedzakaria/TikTok-Automation
- **Language:** Python
- **Why:** Automated video scheduling with AI-powered descriptions. Transcribes video content, generates descriptions. Interesting AI-content workflow.

-----

### Summary: Top Priority Community Repos for Thing02

|Priority  |Repo                                         |Use Case                      |
|----------|---------------------------------------------|------------------------------|
|🔴 Critical|EcomPHP/tiktokshop-php                       |Shop API SDK (most complete)  |
|🔴 Critical|stape-io/tiktok-tag                          |Server-side tracking (GTM SS) |
|🔴 Critical|AdsMCP/tiktok-ads-mcp-server                 |AI ads management via Claude  |
|🔴 Critical|AgriciDaniel/claude-ads                      |Ad audit skill for Claude Code|
|🟡 High    |Seym0n/tiktok-mcp                            |Content analysis via Claude   |
|🟡 High    |Evil0ctal/Douyin_TikTok_Download_API         |Content research & scraping   |
|🟡 High    |zerodytrash/TikTok-Live-Connector            |LIVE selling monitoring       |
|🟡 High    |wkaisertexas/tiktok-uploader                 |Content automation            |
|🟡 High    |aws-samples/uploading-audiences-to-tiktok-ads|Custom audience automation    |
|🟡 High    |vooltex8egp/tiktok-shop-scraper              |Shop competitive intelligence |
|🟡 High    |bellingcat/tiktok-hashtag-analysis           |Hashtag/trend research        |
|🟡 High    |stel-oberts/tiktok-trending-creators-insights|Creator discovery             |
|🟢 Useful  |bilalyasin1616/tiktok-shop-api               |Node.js Shop SDK              |
|🟢 Useful  |AhsanRiaz786/tiktok-ads-scraper              |Ad creative intelligence      |
|🟢 Useful  |makiisthenes/TiktokAutoUploader              |Multi-account scheduling      |
|🟢 Useful  |m2eteam/tiktok-shop-adobe-commerce           |Magento connector             |

-----

## Part 4: Architecture Recommendation

### What a “Unified TikTok Platform” Should Connect

```
┌─────────────────────────────────────────────────┐
│              YOUR UNIFIED PLATFORM               │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐  ┌──────────────────────────┐ │
│  │  TikTok Ads  │  │  TikTok Shop             │ │
│  │  Layer        │  │  Layer                   │ │
│  │              │  │                           │ │
│  │ • Business   │  │ • Seller API (products,  │ │
│  │   API SDK    │  │   orders, fulfillment)   │ │
│  │ • Campaigns  │  │ • Affiliate API          │ │
│  │ • Reporting  │  │ • Partner Center widgets │ │
│  │ • Pixel/EAPI │  │ • Shop analytics         │ │
│  │ • Audiences  │  │ • Creator management     │ │
│  └──────────────┘  └──────────────────────────┘ │
│                                                  │
│  ┌──────────────┐  ┌──────────────────────────┐ │
│  │  Content &   │  │  Tracking &              │ │
│  │  Creative    │  │  Attribution             │ │
│  │              │  │                           │ │
│  │ • Content    │  │ • TikTok Pixel           │ │
│  │   Posting API│  │ • Events API (EAPI)      │ │
│  │ • Creative   │  │ • GTM Templates          │ │
│  │   Center     │  │ • Offline Conversions    │ │
│  │ • Research   │  │ • MCP Integration        │ │
│  │   API        │  │                           │ │
│  └──────────────┘  └──────────────────────────┘ │
│                                                  │
│  ┌──────────────────────────────────────────── │ │
│  │  Auth Layer                                 │ │
│  │  • Login Kit (iOS + Android OpenSDK)        │ │
│  │  • OAuth for Business API                   │ │
│  │  • Partner Center auth for Shop APIs        │ │
│  └──────────────────────────────────────────── │ │
└─────────────────────────────────────────────────┘
```

### Key Integration Points

1. **Business API SDK** → Core of ad management (Python/JS)
1. **TikTok Shop Open APIs** → Core of commerce (via Partner Center)
1. **Events API + Pixel** → Core of tracking
1. **MCP Servers** → AI-powered automation layer on top of everything
1. **Research API** → Market intelligence layer

### What’s Missing from Official GitHub

TikTok does NOT open-source:

- TikTok Shop Seller API SDKs (you’ll use the REST API directly or community wrappers)
- Affiliate Center APIs (documentation only at Partner Center)
- Creative Center tools
- Symphony AI tools
- Market Scope analytics

These are API-only — no official SDK repos exist. You’ll need to build wrappers or use community ones.
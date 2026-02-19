# TikTok Symphony (AI Creative Suite)

## Overview

TikTok Symphony is a suite of generative AI solutions that elevates TikTok content creation. It spans from script writing to video production and asset optimization. Symphony is integrated across both TikTok Creative Center and TikTok Ads Manager.

**Tagline:** "If you can imagine it, you can create it with Symphony."

**URL:** `https://ads.tiktok.com/business/creativecenter/tools/tiktok-symphony/pc/en`

## Symphony Products

### 1. Symphony Creative Studio

**Purpose:** AI-powered video generator that produces TikTok-fit videos in minutes with minimal inputs.

**Key Capabilities:**
- Generate complete TikTok ad videos from product URLs or brief descriptions
- AI-generated scripts, visuals, and voiceovers
- Multiple output variations for A/B testing
- TikTok-native formatting (vertical video, trending styles)
- Support for multiple languages

**Access:** `https://ads.tiktok.com/creative/creativestudio/home/create`

**Workflow:**
1. Provide a product URL or brand information
2. Symphony generates script options
3. AI produces video with visuals, music, and voiceover
4. User can customize and iterate
5. Export directly to TikTok Ads Manager

### 2. Symphony in Ads Manager

Natively integrated AI capabilities within TikTok Ads Manager at the campaign creation level:

#### Generate
- Create brand-new, TikTok-fit creative assets from minimal inputs
- AI generates ad copy, video scripts, and visual concepts
- Based on brand guidelines and campaign objectives

#### Optimize
- AI reviews existing creatives and suggests optimization opportunities
- One-click application of recommended improvements
- Performance prediction based on historical data patterns

#### Edit
- AI-powered last-minute edits to existing creative assets
- TikTok-style editing features (trending transitions, effects)
- Quick adjustments to text overlays, CTAs, and visual elements

## Marketing API - Creative Tools

The following Symphony-related tools are available via the Marketing API:

### Smart Creative
- `GET /smart_creative/material/get/` - Get Smart Creative materials
- `POST /smart_creative/ad/create/` - Create Smart Creative ads
- `POST /smart_creative/material/update/` - Update Smart Creative materials
- Auto-generates multiple creative variations from provided assets

### Smart Text Recommendations
- `GET /creative/smart_text/recommend/` - Get AI-recommended ad text suggestions
- Generates compelling copy based on product/brand context

### CTA Recommendations
- `GET /creative/cta/recommend/` - Get recommended call-to-action texts
- AI-optimized CTAs based on objective and industry

### Smart Fix
- `POST /creative/smart_fix/create/` - Create a Smart Fix task
- `GET /creative/smart_fix/result/` - Get results of a Smart Fix task
- Automatically identifies and fixes creative quality issues

### Creative Fatigue Detection
- `GET /creative/fatigue/detect/` - Get Creative Fatigue Detection results
- Identifies when ad creatives are losing effectiveness
- Suggests refresh timing and approaches

### AIGC Self-Disclosure Toggle
- Available at the ad creation level
- Marks AI-generated content for transparency compliance

## Symphony Capabilities Summary

| Feature | Access Point | API Available |
|---|---|---|
| Video Generation | Creative Studio (Web) | No (UI only) |
| Script Writing | Creative Studio (Web) | No (UI only) |
| Smart Creative | Ads Manager + API | Yes |
| Smart Text | Ads Manager + API | Yes |
| Smart Fix | Ads Manager + API | Yes |
| CTA Recommendations | Ads Manager + API | Yes |
| Fatigue Detection | Ads Manager + API | Yes |
| Asset Optimization | Ads Manager | Partial (via Smart Creative) |

## Deprecated Symphony Tools (via API)

The following tools have been deprecated in the Marketing API:
- Smart Video Soundtrack
- Smart Video
- Quick Optimization
- Dynamic Scene

## Relationship to TikTok One

Symphony is a key pillar within TikTok One, providing the AI-powered creative generation and optimization capabilities. The Creative Studio is accessible through both Creative Center and TikTok One interfaces.

## Availability

- **Creative Studio**: Available to all TikTok for Business account holders
- **Symphony in Ads Manager**: Available during campaign creation workflow
- **API Tools**: Available via Marketing API with appropriate permissions
- **Languages**: Multi-language support for content generation

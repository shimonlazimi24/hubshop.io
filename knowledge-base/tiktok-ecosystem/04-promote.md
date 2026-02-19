# TikTok Promote

## Overview

TikTok Promote is TikTok's self-serve, in-app promotion tool that allows creators and small business owners to boost their organic TikTok content to reach more people. It is a simplified advertising tool designed for users who do not need the full complexity of TikTok Ads Manager.

## Key Characteristics

- **In-app only**: Accessible directly within the TikTok mobile app
- **Self-serve**: No need for a TikTok for Business account or Ads Manager
- **Simplified interface**: Minimal setup compared to full ad campaigns
- **Organic content focus**: Promotes existing TikTok posts rather than creating new ad creatives
- **Budget-friendly**: Low minimum spend thresholds for individual creators

## How It Works

1. **Select Content**: Choose any existing TikTok video from your profile
2. **Choose Goal**: Select a promotion objective:
   - More video views
   - More website visits
   - More followers
   - More messages
   - More profile views
3. **Define Audience**: Set targeting parameters:
   - Automatic (TikTok optimizes for you)
   - Custom audience (gender, age range, interests, location)
4. **Set Budget & Duration**: Choose daily or total budget and promotion period
5. **Launch**: Submit for review and go live

## Promote vs. TikTok Ads Manager

| Feature | TikTok Promote | TikTok Ads Manager |
|---|---|---|
| Access | In-app (mobile) | Web platform |
| Complexity | Simple, guided | Full campaign management |
| Content | Existing organic posts | Custom ad creatives + organic |
| Targeting | Basic demographics | Advanced (custom audiences, lookalikes, pixels) |
| Objectives | 5 simple goals | 10+ detailed objectives |
| Analytics | Basic metrics | Comprehensive reporting |
| API Access | No | Yes (Marketing API) |
| Minimum Budget | Very low | Higher minimums |
| Account Needed | TikTok account | TikTok for Business account |

## Marketing API Integration

TikTok Promote has a dedicated API surface within the Marketing API:

### Promote Campaign API
- Part of the Campaign Management section
- `promote_campaign` endpoints for managing Promote campaigns
- Allows programmatic creation and management of Promote campaigns
- Integration with the broader Marketing API reporting system

### Realtime API
- Real-time performance data for Promote campaigns
- Available within the Campaign Management API section

## Availability

- Available to all TikTok creators with eligible accounts
- Geographic availability matches TikTok's general availability
- Creator must meet minimum follower/account age requirements in some regions
- Budget options vary by region/currency

## Relevance for Integration

- No standalone public API for Promote
- Promote campaigns appear within Ads Manager reporting if the account is linked
- The Marketing API includes Promote campaign management endpoints
- Third-party tools can create and manage Promote-style campaigns via the Marketing API

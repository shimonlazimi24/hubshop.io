# TikTok Developer - API Scopes Reference

## Overview

Scopes represent end-user-granted permissions to access specific data resources or perform specific actions. Being approved for scopes does not automatically grant access; users must individually authorize each scope during the OAuth flow.

**Default scope:** `user.info.basic` is automatically added for all apps with Login Kit.

---

## User Scopes

| Scope | Access | Description |
|-------|--------|-------------|
| `user.info.basic` | Read | Read avatar URL and display name (default for Login Kit) |
| `user.info.profile` | Read | Read bio, verification status, and profile links |
| `user.info.stats` | Read | Read engagement metrics: follower count, following count, video count, likes count |

## Video Scopes

| Scope | Access | Description |
|-------|--------|-------------|
| `video.list` | Read | Read a user's public videos on TikTok |
| `video.publish` | Write | Direct content posting to creator profiles |
| `video.upload` | Write | Draft sharing for creator editing before posting |

## Research Scopes

| Scope | Access | Description |
|-------|--------|-------------|
| `research.data.basic` | Read | Access to TikTok public data for research purposes |
| `research.adlib.basic` | Read | Access to public commercial data (ad library) for research purposes |
| `research.data.u18eu` | Read | Access to European under-18 data plus public content |
| `research.data.vra` | Read | Provisioned data access for vetted researchers |

## Data Portability Scopes

| Scope | Type | Description |
|-------|------|-------------|
| `portability.all.single` | One-time | Full user data archive export |
| `portability.all.ongoing` | Ongoing | Repeated full data archive requests |
| `portability.postsandprofile.single` | One-time | Posts and profile data export |
| `portability.postsandprofile.ongoing` | Ongoing | Repeated posts and profile data requests |
| `portability.activity.single` | One-time | Activity data export |
| `portability.activity.ongoing` | Ongoing | Repeated activity data requests |
| `portability.directmessages.single` | One-time | Direct message data export |
| `portability.directmessages.ongoing` | Ongoing | Repeated direct message data requests |

## Local Service Scopes

| Scope | Access | Description |
|-------|--------|-------------|
| `local.product.manage` | Write | Create and manage product listings |
| `local.shop.manage` | Write | Create and manage local shops |
| `local.voucher.manage` | Write | Validate and redeem vouchers |

## Scope Management

- Developers request scopes during app registration or update
- Additional scopes can be requested from the app settings page
- Users selectively approve requested scopes during OAuth authorization
- Some scopes require additional application review before becoming available

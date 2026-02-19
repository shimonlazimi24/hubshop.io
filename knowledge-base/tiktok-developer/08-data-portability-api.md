# TikTok Developer - Data Portability API

## Overview

The Data Portability API allows developers to request and download user data exports on behalf of authorized TikTok users. It supports both one-time and ongoing data export requests across multiple data categories.

## Endpoints

### Add Data Request

Initiates a data export for an authorized user.

### Check Status of Data Request

Monitors the progress of an ongoing data request.

### Cancel Data Request

Terminates an active data request.

### Download Data

Retrieves the prepared data package. Data is available for download for **4 days** after preparation completes.

## Data Portability Scopes

| Scope | Type | Description |
|-------|------|-------------|
| `portability.all.single` | One-time | Complete user data (single export) |
| `portability.all.ongoing` | Ongoing | Complete user data (repeated exports, returns full dataset each time) |
| `portability.postsandprofile.single` | One-time | Videos and profile information |
| `portability.postsandprofile.ongoing` | Ongoing | Videos and profile information (repeated) |
| `portability.activity.single` | One-time | User engagement history |
| `portability.activity.ongoing` | Ongoing | User engagement history (repeated) |
| `portability.directmessages.single` | One-time | Direct messaging content |
| `portability.directmessages.ongoing` | Ongoing | Direct messaging content (repeated) |

**Note:** "Single" scopes permit one-time requests. "Ongoing" scopes enable repeated exports that return the full dataset for the given scope each time.

## Authentication Requirements

- Valid TikTok developer account with registered app (minimum **Staging** status)
- OAuth authorization with approved Data Portability API scopes
- **Login Kit** and **Webhooks** products must be configured on the app
- User must explicitly authorize the requested data categories

## Data Request Workflow

1. **Submit** export request specifying desired data categories
2. **Monitor** (optional): Poll the status-check endpoint, or wait for webhook
3. **Cancel** (optional): Cancel an ongoing request if needed
4. **Receive notification**: Webhook event `portability.download.ready` fires when data is prepared (typically seconds to hours)
5. **Download**: Retrieve packaged data within the 4-day download window

## Webhook Integration

- Webhook event: `portability.download.ready`
- Webhook notifications are optional; status polling is available as an alternative
- See Webhooks documentation for payload format

## Application Review

- Review typically requires **3-4 weeks**
- Detailed **UX mockups** are required during the approval process
- Must demonstrate how user data will be displayed and used

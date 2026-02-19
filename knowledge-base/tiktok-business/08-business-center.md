# TikTok Business Center API

## Overview

The **Business Center (BC)** is TikTok's centralized management platform for organizations to manage multiple ad accounts, team members, partners, creative assets, catalogs, pixels, and billing from a single hub. It is TikTok's equivalent of Meta's Business Manager.

The Business Center API provides programmatic access to all BC management functions, enabling enterprises and agencies to automate multi-account management at scale.

## Base URL

```
https://business-api.tiktok.com/open_api/v1.3/
```

## Authentication

Standard Marketing API `Access-Token` header. The token must have BC-level permissions.

---

## Business Center Structure

```
Business Center (BC)
  |
  |-- Members (team users with roles)
  |-- Partners (external agencies/businesses)
  |
  |-- Assets
  |    |-- Ad Accounts (advertisers)
  |    |-- TikTok Accounts (organic)
  |    |-- Pixels (tracking)
  |    |-- Catalogs (product feeds)
  |    |-- Audiences (custom audiences)
  |    |-- Creative Assets
  |
  |-- Asset Groups (logical groupings)
  |-- Billing Groups
  |-- Payment Portfolios
  |
  |-- Finance
       |-- Balance management
       |-- Transaction records
       |-- Invoices
```

---

## BC Management

### Core BC Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/bc/get/` | GET | Get Business Centers the user has access to |
| `/v1.3/bc/activity_log/get/` | GET | Get the activity log of a Business Center |

### Getting Business Centers

```
GET /v1.3/bc/get/?page=1&page_size=10
```

Returns list of BCs with:
- BC ID, name, status
- Creation time
- Role of the current user
- Associated ad accounts count

---

## BC Members

Manage team members who have access to the Business Center.

### Member Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/bc/member/get/` | GET | Get members of a BC |
| `/v1.3/bc/member/invite/` | POST | Invite members to a BC |
| `/v1.3/bc/member/update/` | POST | Update member info/role |
| `/v1.3/bc/member/delete/` | POST | Remove member or revoke invitation |

### Member Roles

| Role | Permissions |
|---|---|
| **Admin** | Full access to all BC features and settings |
| **Finance Editor** | Manage billing, payments, and invoices |
| **Finance Analyst** | View-only access to financial data |
| **Operator** | Manage ad accounts and campaigns |
| **Analyst** | View-only access to reports and data |

### Inviting Members

```json
POST /v1.3/bc/member/invite/

{
  "bc_id": "business_center_id",
  "member_emails": ["user@example.com"],
  "role": "OPERATOR"
}
```

---

## BC Partners

Manage external partners (agencies, other businesses) who need access to your BC assets.

### Partner Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/bc/partner/get/` | GET | Get partners of a BC |
| `/v1.3/bc/partner/add/` | POST | Add a partner to a BC |
| `/v1.3/bc/partner/delete/` | POST | Remove a partner from a BC |
| `/v1.3/bc/partner/asset/cancel/` | POST | Cancel asset sharing with partner |
| `/v1.3/bc/partner/asset/get/` | GET | Get assets shared with a partner |

### Adding a Partner

```json
POST /v1.3/bc/partner/add/

{
  "bc_id": "your_bc_id",
  "partner_bc_id": "partner_business_center_id",
  "relationship_type": "PARTNER"
}
```

---

## BC Assets

### Ad Account Management

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/bc/asset/ad_account/create/` | POST | Create an ad account under BC |
| `/v1.3/bc/asset/ad_account/update/` | POST | Update ad account settings |
| `/v1.3/bc/asset/ad_account/disable/` | POST | Disable an ad account |
| `/v1.3/bc/asset/qualification/upload/` | POST | Upload business certificate |
| `/v1.3/bc/asset/qualification/get/` | GET | Get qualifications in a BC |
| `/v1.3/bc/asset/unionpay/check/` | GET | Check UnionPay verification requirement |
| `/v1.3/bc/asset/unionpay/submit/` | POST | Submit UnionPay verification |

### Creating an Ad Account

```json
POST /v1.3/bc/asset/ad_account/create/

{
  "bc_id": "business_center_id",
  "advertiser_name": "New Ad Account",
  "timezone": "America/New_York",
  "currency": "USD",
  "industry_id": "industry_code"
}
```

### Organization Account

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/bc/asset/organization_account/create/` | POST | Create Organization Account in BC |

### General Asset Management

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/bc/asset/get/` | GET | Get assets in a BC |
| `/v1.3/bc/asset/admin/get/` | GET | Get assets (admin view) |
| `/v1.3/bc/asset/assign/` | POST | Assign asset to members/partners |
| `/v1.3/bc/asset/unassign/` | POST | Unassign asset |
| `/v1.3/bc/asset/delete/` | POST | Delete assets from BC |
| `/v1.3/bc/asset/binding/get/` | GET | Get binding info of an asset |

### TikTok Account Management

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/bc/asset/tt_account/auth_url/` | GET | Get TikTok account authorization URL |
| `/v1.3/bc/asset/tt_account/link/` | POST | Link TikTok account to ad account |
| `/v1.3/bc/asset/tt_account/unlink/` | POST | Unlink TikTok account |
| `/v1.3/bc/asset/tt_account/ad_account/get/` | GET | Get ad accounts linked to TikTok account |

### Pixel Management in BC

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/bc/asset/pixel/manage/` | POST | Manage a pixel in BC |
| `/v1.3/bc/asset/pixel/transfer/` | POST | Transfer pixel from advertiser to BC |
| `/v1.3/bc/asset/pixel/link/` | POST | Link/unlink pixel to ad accounts |
| `/v1.3/bc/asset/pixel/ad_account/get/` | GET | Get ad accounts linked to a pixel |

### Cross-Asset Queries

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/bc/asset/partner/get/` | GET | Get partners by an asset |
| `/v1.3/bc/asset/member/get/` | GET | Get members by an asset |

---

## BC Asset Groups

Organize assets into logical groups for easier management and access control.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/bc/asset_group/create/` | POST | Create an Asset Group |
| `/v1.3/bc/asset_group/update/` | POST | Update an Asset Group |
| `/v1.3/bc/asset_group/get/` | GET | Get all Asset Groups |
| `/v1.3/bc/asset_group/detail/` | GET | Get Asset Group details |
| `/v1.3/bc/asset_group/delete/` | POST | Delete Asset Groups |

### Creating an Asset Group

```json
POST /v1.3/bc/asset_group/create/

{
  "bc_id": "business_center_id",
  "asset_group_name": "APAC Markets",
  "asset_ids": ["ad_account_1", "ad_account_2"],
  "member_ids": ["member_1", "member_2"]
}
```

---

## BC Billing Groups

Group ad accounts for consolidated billing.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/bc/billing_group/create/` | POST | Create a Billing Group |
| `/v1.3/bc/billing_group/update/` | POST | Update a Billing Group |
| `/v1.3/bc/billing_group/get/` | GET | Get Billing Groups |
| `/v1.3/bc/billing_group/advertiser/get/` | GET | Get advertiser list of a Billing Group |

---

## BC Finance / Payments

### Balance and Budget Management

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/bc/payment/process/` | POST | Process a payment |
| `/v1.3/bc/payment/balance_budget/get/` | GET | Get balance and budget of ad accounts |
| `/v1.3/bc/payment/balance/get/` | GET | Get BC balance |
| `/v1.3/bc/payment/transaction/get/` | GET | Get transaction records (BC or ad accounts) |
| `/v1.3/bc/payment/transaction/ad_account/get/` | GET | Get ad account transaction records |
| `/v1.3/bc/payment/transaction/bc/get/` | GET | Get BC transaction records |
| `/v1.3/bc/payment/budget_history/get/` | GET | Get budget change history of ad account |
| `/v1.3/bc/payment/cost/get/` | GET | Get cost records of BC and ad accounts |

### Processing a Payment (Fund Transfer)

```json
POST /v1.3/bc/payment/process/

{
  "bc_id": "business_center_id",
  "advertiser_id": "target_ad_account_id",
  "transfer_type": "GRANT",      // or "RECLAIM"
  "amount": 1000.00
}
```

### Payment Portfolios

Payment Portfolios allow grouping ad accounts under a shared payment method and credit line.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/bc/payment_portfolio/get/` | GET | Get Payment Portfolios |
| `/v1.3/bc/payment_portfolio/create/` | POST | Create a Payment Portfolio |
| `/v1.3/bc/payment_portfolio/ad_account/link/` | POST | Link ad accounts |
| `/v1.3/bc/payment_portfolio/credit_line/allocate/` | POST | Allocate credit line |
| `/v1.3/bc/payment_portfolio/ad_account/get/` | GET | Get linked ad accounts |
| `/v1.3/bc/payment_portfolio/user/get/` | GET | Get authorized users |

---

## BC Invoices

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/bc/invoice/get/` | GET | Get BC invoices |
| `/v1.3/bc/invoice/unpaid/get/` | GET | Get unpaid amount |
| `/v1.3/bc/invoice/download/sync/` | GET | Download invoices synchronously |
| `/v1.3/bc/invoice/download/async/create/` | POST | Create async download task |
| `/v1.3/bc/invoice/download/async/get/` | GET | Get async download tasks |
| `/v1.3/bc/invoice/download/async/list/` | GET | Get async download task list |

---

## BC Reporting

Business Center-level reporting across all ad accounts.

### BC Report Endpoint

Use the standard reporting endpoint with `report_type: BC`:

```json
GET /v1.3/report/integrated/get/?
  bc_id=xxx&
  report_type=BC&
  dimensions=["stat_time_day"]&
  metrics=["spend","impressions","clicks"]&
  start_date=2025-01-01&
  end_date=2025-01-31
```

### BC-Specific Report Features

- Does not require `advertiser_id` (uses `bc_id` instead)
- Does not require `service_type` or `data_level`
- Aggregates data across all ad accounts in the BC
- Supports dimensions specific to BC reporting

### BC Reporting Helper

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/bc/reporting/currency_region/get/` | GET | Get currencies and registration areas for ad accounts |

---

## Subscription (Webhook) Management

Subscribe to events for real-time notifications about ad account changes.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/subscription/create/` | POST | Create a subscription |
| `/v1.3/subscription/get/` | GET | Get subscription details |
| `/v1.3/subscription/cancel/` | POST | Cancel a subscription |

### Subscribable Events

| Event Type | Description |
|---|---|
| Ad account status changes | Budget exhaustion, policy violations |
| Campaign/ad status changes | Approval, rejection, delivery status |
| Audience status changes | Audience processing completion |
| Billing events | Payment failures, balance alerts |

---

## Use Cases

### Agency Management

1. Create a BC for your agency
2. Add clients as partners
3. Create ad accounts under BC for each client
4. Assign team members with appropriate roles
5. Manage billing across all client accounts
6. Generate cross-account reports

### Enterprise Multi-Brand

1. Create a BC for the enterprise
2. Create ad accounts per brand/region
3. Organize into Asset Groups (by brand, market, etc.)
4. Share pixels and audiences across accounts
5. Centralize payment through Payment Portfolios
6. Generate consolidated BC-level reports

### Automated Account Provisioning

1. Use API to create ad accounts programmatically
2. Upload business certifications
3. Assign to appropriate Asset Groups
4. Configure payment/billing
5. Set up pixels and link to catalogs
6. Invite team members with correct roles

---

## Business Messaging API

The Business Messaging API enables managing direct messages between businesses and users on TikTok.

### Core Messaging

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/business/message/send/` | POST | Send message to a conversation |
| `/v1.3/business/message/conversation/list/` | GET | Get conversations |
| `/v1.3/business/message/list/` | GET | Get messages |
| `/v1.3/business/message/image/upload/` | POST | Upload image for message |
| `/v1.3/business/message/media/download/` | GET | Download media from message |
| `/v1.3/business/message/capability/check/` | GET | Check messaging capability |

### Comment-to-Message

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/business/message/comment_to_message/update/` | POST | Enable/disable Comment-to-Message |
| `/v1.3/business/message/comment_to_message/get/` | GET | Get Comment-to-Message setting |

### Messaging Webhooks

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/business/message/webhook/create/` | POST | Create webhook configuration |
| `/v1.3/business/message/webhook/get/` | GET | Get webhook configuration |
| `/v1.3/business/message/webhook/delete/` | POST | Delete webhook configuration |

### Automatic Messages

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/business/message/auto/create/` | POST | Create automatic message |
| `/v1.3/business/message/auto/update/` | POST | Update automatic message |
| `/v1.3/business/message/auto/status/update/` | POST | Toggle automatic message |
| `/v1.3/business/message/auto/get/` | GET | Get automatic messages |
| `/v1.3/business/message/auto/delete/` | POST | Delete automatic message |
| `/v1.3/business/message/auto/sort/` | POST | Sort automatic messages |

### Messaging Limits

The Business Messaging API has specific messaging limits:
- Rate limits per Business Account
- Message content restrictions
- Conversation window requirements
- Data security and privacy review required for access

---

## Lead Generation via BC

### Lead Management Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/lead/test/create/` | POST | Create a test lead |
| `/v1.3/lead/test/get/` | GET | Get a test lead |
| `/v1.3/lead/test/delete/` | POST | Delete a test lead |
| `/v1.3/lead/download/create/` | POST | Create lead download task |
| `/v1.3/lead/download/` | GET | Download leads |
| `/v1.3/lead/form/get/` | GET | Get form libraries |
| `/v1.3/lead/bc/migrate/` | POST | Migrate leads to a BC |
| `/v1.3/lead/form/fields/` | GET | Get Instant Form fields |
| `/v1.3/lead/form/detail/` | GET | Get form/DM lead details |
| `/v1.3/lead/get/` | GET | Get a lead record |

---

## Media Mix Modeling (MMM)

Request aggregated data for media mix modeling analysis.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/mmm/request/create/` | POST | Create MMM data request |
| `/v1.3/mmm/request/status/` | GET | Check request status |
| `/v1.3/mmm/request/download/` | GET | Get download URL for MMM data |
| `/v1.3/mmm/request/history/` | GET | Get request history |

---

## Best Practices

### BC Organization
- Create clear naming conventions for ad accounts
- Use Asset Groups to organize by market, brand, or team
- Assign minimum necessary roles to members
- Regularly audit member access and remove inactive users

### Financial Management
- Use Payment Portfolios for consolidated billing
- Monitor account balances proactively
- Set up webhook subscriptions for payment alerts
- Review invoices and transaction records regularly

### Partner Management
- Share only necessary assets with partners
- Use Asset Groups to control partner access scope
- Regularly review and revoke unnecessary partner access
- Maintain clear communication about shared asset usage

### Scaling Operations
- Automate ad account provisioning via API
- Use BC-level reporting for cross-account insights
- Leverage Asset Groups for bulk management
- Implement webhook subscriptions for real-time monitoring

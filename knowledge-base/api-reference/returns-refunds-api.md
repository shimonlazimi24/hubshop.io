# Return, Refund & Cancel API Reference

## Description
Process buyer return/refund/cancellation requests and manage after-sales situations.

## Endpoint Count: 13

## Endpoints

| # | Method | Endpoint | Doc |
|---|--------|----------|-----|
| 1 | GET | Get Reject Reasons | [Link](https://partner.tiktokshop.com/docv2/page/get-reject-reasons-202309) |
| 2 | POST | Create Return | [Link](https://partner.tiktokshop.com/docv2/page/create-return-202309) |
| 3 | POST | Approve Return | [Link](https://partner.tiktokshop.com/docv2/page/approve-return-202309) |
| 4 | POST | Reject Return | [Link](https://partner.tiktokshop.com/docv2/page/reject-return-202309) |
| 5 | POST | Search Returns | [Link](https://partner.tiktokshop.com/docv2/page/search-returns-202309) |
| 6 | GET | Get Return Records | [Link](https://partner.tiktokshop.com/docv2/page/get-return-records-202309) |
| 7 | POST | Cancel Order | [Link](https://partner.tiktokshop.com/docv2/page/cancel-order-202309) |
| 8 | POST | Approve Cancellation | [Link](https://partner.tiktokshop.com/docv2/page/approve-cancellation-202309) |
| 9 | POST | Reject Cancellation | [Link](https://partner.tiktokshop.com/docv2/page/reject-cancellation-202309) |
| 10 | POST | Search Cancellations | [Link](https://partner.tiktokshop.com/docv2/page/search-cancellations-202309) |
| 11 | POST | Calculate Refund | [Link](https://partner.tiktokshop.com/docv2/page/calculate-refund-202309) |
| 12 | GET | Get Aftersale Eligibility | [Link](https://partner.tiktokshop.com/docv2/page/get-aftersale-eligibility-202512) |
| 13 | GET | Get Decision Eligibility | [Link](https://partner.tiktokshop.com/docv2/page/get-decision-eligibility-202601) |

## Key Policies

- Seller must respond to buyer requests within **48 hours** (auto-approved otherwise)
- Cancel types: BUYER_CANCEL (requires seller review) and CANCEL (direct)
- Return-less refunds supported (seller can choose buyer keeps items)
- Replacement orders supported (platform generates new fulfillment order)
- US and UK: Partial cancellation supported on item out of stock

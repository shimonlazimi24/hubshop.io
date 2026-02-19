# Finance API Reference

## Description
Access transaction details, settlement statements, payments, and withdrawals for financial reconciliation.

## Endpoint Count: 6

## Endpoints

| # | Method | Endpoint | Doc |
|---|--------|----------|-----|
| 1 | GET | Get Statements | [Link](https://partner.tiktokshop.com/docv2/page/get-statements-202309) |
| 2 | GET | Get Payments | [Link](https://partner.tiktokshop.com/docv2/page/get-payments-202309) |
| 3 | GET | Get Withdrawals | [Link](https://partner.tiktokshop.com/docv2/page/get-withdrawals-202309) |
| 4 | GET | Get Transactions by Order | [Link](https://partner.tiktokshop.com/docv2/page/get-transactions-by-order-202501) |
| 5 | GET | Get Transactions by Statement | [Link](https://partner.tiktokshop.com/docv2/page/get-transactions-by-statement-202501) |
| 6 | GET | Get Unsettled Transactions | [Link](https://partner.tiktokshop.com/docv2/page/get-unsettled-transactions-202507) |

## Key Concepts

- **Statements**: Daily settled order collections (generated at UTC 0:00, closed next day)
- **Payments**: Payout fund transaction records
- **One statement = one payment** (may combine small statements)
- **Adjustment types**: Shipping fee adjustment, Chargeback, Platform compensation, Platform penalty, Logistics reimbursement, and more

# Orders API Reference

## Description
Obtain order information, order details, and manage external order references.

## Endpoint Count: 7

## Endpoints

| # | Method | Endpoint | Doc |
|---|--------|----------|-----|
| 1 | POST | Get Order List | [Link](https://partner.tiktokshop.com/docv2/page/get-order-list-202309) |
| 2 | GET | Get Price Detail | [Link](https://partner.tiktokshop.com/docv2/page/get-price-detail-202407) |
| 3 | POST | Add External Order References | [Link](https://partner.tiktokshop.com/docv2/page/add-external-order-references-202406) |
| 4 | GET | Get External Order References | [Link](https://partner.tiktokshop.com/docv2/page/get-external-order-references-202406) |
| 5 | POST | Search Order By External Reference | [Link](https://partner.tiktokshop.com/docv2/page/search-order-by-external-order-reference-202406) |
| 6 | GET | Get Order Detail | [Link](https://partner.tiktokshop.com/docv2/page/get-order-detail-202507) |
| 7 | POST | Update Blind Box Opening Results | [Link](https://partner.tiktokshop.com/docv2/page/update-the-blind-box-opening-results-202511) |

## Order Statuses

```
UNPAID -> ON_HOLD -> AWAITING_SHIPMENT -> PARTIALLY_SHIPPING ->
AWAITING_COLLECTION -> IN_TRANSIT -> DELIVERED -> COMPLETED
                                                  -> CANCELLED
```

## Key Concepts

- **SLA Information**: rts_sla, tts_sla, delivery_sla, cancel_order_sla
- **Fulfillment Types**: FULFILLMENT_BY_SELLER, FULFILLMENT_BY_TIKTOK
- **Shipping Types**: TikTok Shipping, Seller Shipping
- **Buyer Remorse**: 1-hour cancellation window after purchase

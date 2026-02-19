# Promotion API Reference

## Description
Create and manage promotion activities -- Product Discounts, Flash Deals, and Coupons/Vouchers.

## Endpoint Count: 9

## Endpoints

| # | Method | Endpoint | Doc |
|---|--------|----------|-----|
| 1 | POST | Create Activity | [Link](https://partner.tiktokshop.com/docv2/page/create-activity-202309) |
| 2 | PUT | Update Activity | [Link](https://partner.tiktokshop.com/docv2/page/update-activity-202309) |
| 3 | POST | Deactivate Activity | [Link](https://partner.tiktokshop.com/docv2/page/deactivate-activity-202309) |
| 4 | GET | Get Activity | [Link](https://partner.tiktokshop.com/docv2/page/get-activity-202309) |
| 5 | POST | Search Activities | [Link](https://partner.tiktokshop.com/docv2/page/search-activities-202309) |
| 6 | PUT | Update Activity Product | [Link](https://partner.tiktokshop.com/docv2/page/update-activity-product-202309) |
| 7 | DELETE | Remove Activity Product | [Link](https://partner.tiktokshop.com/docv2/page/remove-activity-product-202309) |
| 8 | GET | Get Coupon | [Link](https://partner.tiktokshop.com/docv2/page/get-coupon-202406) |
| 9 | POST | Search Coupons | [Link](https://partner.tiktokshop.com/docv2/page/search-coupons-202406) |

## Key Concepts

- **Activity types**: Product Discount (Fixed Price or Percentage Off), Flash Deal (time-limited countdown)
- **Coupons/Vouchers**: Cannot be created via API, only searched/retrieved
- Flash deal price must be <= price paid by customers in last 30 days
- All promotions are 100% seller-funded

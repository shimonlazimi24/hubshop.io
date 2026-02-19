# Fulfillment API Reference

## Description
Fulfill TikTok Shop orders -- manage packages, shipping labels, tracking, split/consolidated shipments.

## Endpoint Count: 24

## TikTok Shipping Endpoints

| # | Method | Endpoint | Doc |
|---|--------|----------|-----|
| 1 | GET | Get Order Split Attributes | [Link](https://partner.tiktokshop.com/docv2/page/get-order-split-attributes-202309) |
| 2 | POST | Split Orders | [Link](https://partner.tiktokshop.com/docv2/page/split-orders-202309) |
| 3 | POST | Get Eligible Shipping Service | [Link](https://partner.tiktokshop.com/docv2/page/get-eligible-shipping-service-202309) |
| 4 | POST | Create First Mile Bundle | [Link](https://partner.tiktokshop.com/docv2/page/create-first-mile-bundle-202407) |
| 5 | POST | Search Package | [Link](https://partner.tiktokshop.com/docv2/page/search-package-202309) |
| 6 | GET | Search Combinable Packages | [Link](https://partner.tiktokshop.com/docv2/page/search-combinable-packages-202309) |
| 7 | POST | Combine Package | [Link](https://partner.tiktokshop.com/docv2/page/combine-package-202309) |
| 8 | POST | Uncombine Packages | [Link](https://partner.tiktokshop.com/docv2/page/uncombine-packages-202309) |
| 9 | GET | Get Package Handover Time Slots | [Link](https://partner.tiktokshop.com/docv2/page/get-package-handover-time-slots-202309) |
| 10 | POST | Ship Package | [Link](https://partner.tiktokshop.com/docv2/page/ship-package-202309) |
| 11 | POST | Batch Ship Packages | [Link](https://partner.tiktokshop.com/docv2/page/batch-ship-packages-202309) |
| 12 | POST | Mark Package As Shipped | [Link](https://partner.tiktokshop.com/docv2/page/mark-package-as-shipped-202309) |
| 13 | GET | Get Package Shipping Document | [Link](https://partner.tiktokshop.com/docv2/page/get-package-shipping-document-202309) |
| 14 | GET | Get Package Detail | [Link](https://partner.tiktokshop.com/docv2/page/get-package-detail-202309) |
| 15 | GET | Get Tracking | [Link](https://partner.tiktokshop.com/docv2/page/get-tracking-202309) |
| 16 | POST | Update Shipping Info | [Link](https://partner.tiktokshop.com/docv2/page/update-shipping-info-202309) |
| 17 | POST | Update Package Shipping Info | [Link](https://partner.tiktokshop.com/docv2/page/update-package-shipping-info-202309) |
| 18 | POST | Upload Delivery File | [Link](https://partner.tiktokshop.com/docv2/page/fulfillment-upload-delivery-file-202309) |
| 19 | POST | Upload Delivery Image | [Link](https://partner.tiktokshop.com/docv2/page/fulfillment-upload-delivery-image-202309) |
| 20 | POST | Update Package Delivery Status | [Link](https://partner.tiktokshop.com/docv2/page/update-package-delivery-status-202309) |
| 21 | POST | Upload Invoice | [Link](https://partner.tiktokshop.com/docv2/page/upload-invoice-202502) |
| 22 | GET | TTS Tracking Validation | [Link](https://partner.tiktokshop.com/docv2/page/tts-tracking-validation-202508) |
| 23 | POST | Create First Mile Bundle V2 | [Link](https://partner.tiktokshop.com/docv2/page/create-first-mile-bundle-v2-202510) |
| 24 | POST | Create Packages | [Link](https://partner.tiktokshop.com/docv2/page/create-packages-202512) |

## Key Policies

- **Consolidation**: Max 20 orders per tracking number, same recipient name/address
- **SEA market**: Cannot split below SKU level
- **US/EMEA/LATAM/JP**: No splitting restrictions
- **Brazil**: Must upload invoice before shipping

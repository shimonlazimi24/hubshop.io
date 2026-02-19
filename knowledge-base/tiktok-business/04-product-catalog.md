# TikTok Product Catalog API

## Overview

The TikTok Catalog Management API enables advertisers to create and manage product catalogs for dynamic product advertising. Catalogs power several ad formats including Catalog Ads (formerly Dynamic Showcase Ads/DSA), Video Shopping Ads, and Catalog Listing Ads. Products in catalogs are dynamically matched to users based on their browsing behavior and interests.

## Base URL

```
https://business-api.tiktok.com/open_api/v1.3/
```

## Authentication

Standard Marketing API `Access-Token` header.

---

## Catalog Management

### Core Catalog CRUD

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/catalog/create/` | POST | Create a new catalog |
| `/v1.3/catalog/update/` | POST | Update catalog name |
| `/v1.3/catalog/delete/` | POST | Delete a catalog |
| `/v1.3/catalog/get/` | GET | List catalogs |
| `/v1.3/catalog/lexicon/get/` | GET | Get lexicon list for a catalog |
| `/v1.3/catalog/bc/migrate/` | POST | Migrate catalog to a Business Center |
| `/v1.3/catalog/region/get/` | GET | Get available regions |
| `/v1.3/catalog/location_currency/get/` | GET | Get locations and currencies |
| `/v1.3/catalog/overview/get/` | GET | Get catalog overview |

### Catalog Types

Catalogs can be created for different product verticals:

| Catalog Type | Description |
|---|---|
| **E-commerce** | General retail products |
| **Travel (Hotels)** | Hotel and accommodation listings |
| **Travel (Flights)** | Flight listings |
| **Automotive (Inventory)** | Vehicle inventory listings |
| **Automotive (Models)** | Vehicle model information |
| **Real Estate** | Property listings |
| **Streaming** | Content/media listings |
| **Mini Series** | Content series listings |

### Creating a Catalog

```json
POST /v1.3/catalog/create/

{
  "bc_id": "business_center_id",
  "catalog_name": "My Product Catalog",
  "catalog_type": "ECOMMERCE",
  "vertical_type": "ECOMMERCE"
}
```

---

## Product Management

### Product Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/catalog/product/file/upload/` | POST | Upload products via file URL |
| `/v1.3/catalog/product/upload/` | POST | Upload products via JSON schema |
| `/v1.3/catalog/product/update/` | POST | Update existing products |
| `/v1.3/catalog/product/delete/` | POST | Remove products |
| `/v1.3/catalog/product/get/` | GET | Get products |
| `/v1.3/catalog/product/log/` | GET | Get product handling log |

### Upload Methods

#### 1. Upload via JSON Schema

Upload products directly in the API request body:

```json
POST /v1.3/catalog/product/upload/

{
  "bc_id": "business_center_id",
  "catalog_id": "catalog_id",
  "products": [
    {
      "sku_id": "product_001",
      "title": "Blue Running Shoes",
      "description": "Comfortable running shoes in blue",
      "availability": "IN_STOCK",
      "condition": "NEW",
      "price": {
        "price": "49.99",
        "currency": "USD"
      },
      "sale_price": {
        "price": "39.99",
        "currency": "USD"
      },
      "link": "https://example.com/products/blue-shoes",
      "image_link": "https://example.com/images/blue-shoes.jpg",
      "brand": "Example Brand",
      "google_product_category": "Apparel & Accessories > Shoes",
      "item_group_id": "shoes_group_001"
    }
  ]
}
```

#### 2. Upload via File URL

Upload a CSV, TSV, or XML feed file:

```json
POST /v1.3/catalog/product/file/upload/

{
  "bc_id": "business_center_id",
  "catalog_id": "catalog_id",
  "file_url": "https://example.com/feeds/products.csv"
}
```

### Product Fields by Catalog Type

#### E-commerce Products

| Field | Required | Description |
|---|---|---|
| `sku_id` | Yes | Unique product identifier |
| `title` | Yes | Product title |
| `description` | Yes | Product description |
| `availability` | Yes | `IN_STOCK`, `OUT_OF_STOCK`, `PREORDER` |
| `condition` | Yes | `NEW`, `REFURBISHED`, `USED` |
| `price` | Yes | Product price with currency |
| `link` | Yes | Product URL |
| `image_link` | Yes | Main product image URL |
| `brand` | Recommended | Brand name |
| `sale_price` | Optional | Sale price with currency |
| `google_product_category` | Recommended | Google product taxonomy category |
| `item_group_id` | Optional | Group ID for product variants |
| `additional_image_link` | Optional | Additional images |
| `color` | Optional | Product color |
| `size` | Optional | Product size |
| `gender` | Optional | Target gender |
| `age_group` | Optional | Target age group |
| `material` | Optional | Product material |
| `pattern` | Optional | Product pattern |
| `custom_label_0-4` | Optional | Custom classification labels |

### Product Image Requirements

- Minimum resolution: 500x500 pixels
- Recommended: 1080x1080 pixels or higher
- Supported formats: JPG, PNG
- Maximum file size: varies by format
- Images should clearly show the product
- No watermarks, promotional text, or borders

---

## Catalog Feeds

Feeds allow automated, scheduled product updates from an external data source.

### Feed Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/catalog/feed/create/` | POST | Create a feed |
| `/v1.3/catalog/feed/get/` | GET | Get feeds |
| `/v1.3/catalog/feed/update/` | POST | Update a feed |
| `/v1.3/catalog/feed/delete/` | POST | Delete a feed |
| `/v1.3/catalog/feed/log/` | GET | Get feed processing log |
| `/v1.3/catalog/feed/schedule/update/` | POST | Update feed schedule |

### Feed Types

| Type | Description |
|---|---|
| URL Feed | Products fetched from a hosted file URL |
| File Upload | Products uploaded via direct file upload |

### Feed Schedule

Feeds can be configured with automatic refresh schedules:
- Hourly
- Daily
- Weekly
- Custom intervals

### Creating a Feed

```json
POST /v1.3/catalog/feed/create/

{
  "bc_id": "business_center_id",
  "catalog_id": "catalog_id",
  "feed_name": "Daily Product Feed",
  "feed_url": "https://example.com/feeds/products.csv",
  "auto_update": true,
  "schedule": {
    "interval": "DAILY",
    "time": "03:00"
  }
}
```

---

## Product Sets

Product sets are subsets of catalog products defined by rules or manual selection, used to target specific products in ad groups.

### Product Set Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/catalog/product_set/get/` | GET | Get product sets |
| `/v1.3/catalog/product_set/product/get/` | GET | Get products in a set |
| `/v1.3/catalog/product_set/condition/create/` | POST | Create set by conditions |
| `/v1.3/catalog/product_set/file/create/` | POST | Create set by file |
| `/v1.3/catalog/product_set/update/` | POST | Update a product set |
| `/v1.3/catalog/product_set/delete/` | POST | Delete product sets |

### Product Set Rules

Product sets can be defined using conditions based on product fields:

| Operator | Description |
|---|---|
| `EQUAL` | Field equals value |
| `NOT_EQUAL` | Field does not equal value |
| `CONTAINS` | Field contains substring |
| `NOT_CONTAINS` | Field does not contain substring |
| `IN` | Field is in list of values |
| `NOT_IN` | Field is not in list of values |
| `GREATER_THAN` | Numeric field greater than value |
| `LESS_THAN` | Numeric field less than value |
| `BETWEEN` | Numeric field between two values |
| `IS_EMPTY` | Field is empty |
| `IS_NOT_EMPTY` | Field is not empty |

### Example: Create Product Set by Conditions

```json
POST /v1.3/catalog/product_set/condition/create/

{
  "bc_id": "business_center_id",
  "catalog_id": "catalog_id",
  "product_set_name": "Shoes Under $50",
  "conditions": [
    {
      "field": "google_product_category",
      "operator": "CONTAINS",
      "value": "Shoes"
    },
    {
      "field": "price",
      "operator": "LESS_THAN",
      "value": "50.00"
    }
  ]
}
```

---

## Catalog Event Sources

Link event sources (pixels, apps) to catalogs for retargeting and dynamic product matching.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/catalog/event_source/bind/` | POST | Bind event source to catalog |
| `/v1.3/catalog/event_source/unbind/` | POST | Unbind event source |
| `/v1.3/catalog/event_source/get/` | GET | Get event source binding info |

### Event Source Binding

Connecting a Pixel or App event source to a catalog enables:
- **Retargeting**: Show products to users who viewed them on your site
- **Dynamic Product Ads**: Automatically show relevant products from catalog
- **Cross-sell/Upsell**: Show related products to recent purchasers

---

## Catalog Videos

Upload and manage videos associated with catalog products.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/catalog/video/upload/` | POST | Upload catalog videos via file URL |
| `/v1.3/catalog/video/log/` | GET | Get video handling log |
| `/v1.3/catalog/video/get/` | GET | Get uploaded catalog videos |
| `/v1.3/catalog/video/delete/` | POST | Delete catalog videos |

---

## Catalog Diagnostics

Troubleshoot catalog issues and product quality.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/catalog/diagnostics/product/get/` | GET | Get product diagnostic info (sync) |
| `/v1.3/catalog/diagnostics/product/download/create/` | POST | Create async diagnostic download task |
| `/v1.3/catalog/diagnostics/product/download/` | GET | Download diagnostic info |
| `/v1.3/catalog/diagnostics/event_source/get/` | GET | Get event source diagnostic info |
| `/v1.3/catalog/diagnostics/event_source/trend/` | GET | Get event trends and match rate |

### Diagnostic Categories

- **Product errors**: Missing required fields, invalid values
- **Product warnings**: Low-quality images, missing recommended fields
- **Event source issues**: Low match rates, missing events
- **Feed errors**: Parse failures, URL issues

---

## Catalog Insights

Analyze catalog performance and discover trends.

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/catalog/insights/filter/get/` | GET | Get filters for insights |
| `/v1.3/catalog/insights/product/trending/` | GET | Get trending products |
| `/v1.3/catalog/insights/category/trending/` | GET | Get trending categories |

---

## Using Catalogs with Ads

### Catalog Ads (formerly Dynamic Showcase Ads)

Catalog Ads automatically display products from your catalog to users most likely to be interested. The system:

1. Matches user behavior (from Pixel/Events API) to catalog products
2. Dynamically generates ad creatives with product images, prices, titles
3. Optimizes which products to show each user

### Ad Formats Using Catalogs

| Format | Description |
|---|---|
| **Video Shopping Ads** | Video creative + product cards from catalog |
| **Catalog Ads** | Dynamic product ads from catalog |
| **Catalog Listing Ads** | Product listing format (to be deprecated) |
| **Product Shopping Ads** | Direct product promotion (to be deprecated) |
| **Live Shopping Ads** | Live stream + catalog products |

### Campaign Setup with Catalogs

When creating campaigns with catalog products:

1. Create a catalog and upload products
2. Bind event source (Pixel) to catalog
3. Create product sets (optional, for targeting specific products)
4. Create campaign with `PRODUCT_SALES` objective
5. Create ad group with catalog_id and product_set_id
6. Create ad with catalog creative settings

---

## TikTok Store Integration

For TikTok Shop sellers, the API also provides store product access:

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/store/get/` | GET | Get available stores under ad account |
| `/v1.3/store/product/get/` | GET | Get products within a TikTok Shop |

### Showcase Integration

For creators with Showcase (product display) permission:

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1.3/showcase/identity/get/` | GET | Get identities with Showcase permission |
| `/v1.3/showcase/region/get/` | GET | Get available regions for Showcase |
| `/v1.3/showcase/product/get/` | GET | Get available Showcase products |

---

## Best Practices

### Catalog Quality
- Provide high-resolution product images (1080x1080+)
- Include complete product information (title, description, price, availability)
- Use accurate `google_product_category` values
- Keep prices and availability up to date via scheduled feeds
- Use `item_group_id` to group product variants

### Event Source Integration
- Bind Pixel to catalog for retargeting
- Ensure `content_id` in Pixel events matches `sku_id` in catalog
- Monitor match rates via Catalog Diagnostics
- Use ViewContent, AddToCart, and Purchase events for retargeting signals

### Feed Management
- Schedule feeds to update at least daily
- Monitor feed logs for errors
- Use CSV or XML format for large catalogs
- Include all required fields to avoid product rejections

# TikTok Shop - SDK & Widgets

## Official SDK

The TikTok Shop API SDK simplifies integration by handling authentication (signature generation) automatically.

### Supported Languages

| Language | Integration Guide |
|----------|-------------------|
| Java | [Integrate Java SDK](https://partner.tiktokshop.com/docv2/page/integrate-java-sdk) |
| Go (GoLang) | [Integrate GoLang SDK](https://partner.tiktokshop.com/docv2/page/integrate-golang-sdk) |
| Node.js | [Integrate Node.js SDK](https://partner.tiktokshop.com/docv2/page/integrate-node-js-sdk) |

**Note:** Python is NOT officially supported via SDK, but code samples are available for manual integration (see authentication docs).

### SDK Limitations

- Cannot register or process webhooks
- Currently available to a subset of developers (whitelist-based)
- Expanding to all developers over time

### SDK Download

Available at: https://partner.tiktokshop.com/docv2/page/download-sdk

## Widgets

Widgets are **frontend UI components** built on TikTok Shop APIs that provide out-of-the-box seller interfaces.

### API vs Widget Comparison

| Aspect | TikTok Shop API | TikTok Shop Widget |
|--------|----------------|-------------------|
| Architecture | REST backend-to-backend | Frontend SDK with backend calls |
| Development | Backend development | Frontend development |
| UI Flexibility | Full control, customizable | Out-of-the-box, not customizable |
| Use Case | Custom integrations | Quick standard UIs |

### Available Widgets

| Widget | Description | Markets |
|--------|-------------|---------|
| Warehouse Widget | Set up warehouse info (contact, address, sales range) | US, UK |
| Shipping Template Widget | Set shipping templates for self-shipping/3PL sellers | US, UK |
| Product Optimizer Widget | AI-powered product quality recommendations | US, UK |
| Orders by TikTok Shipping (4PL) Widget | Process 4PL orders (labels, shipments) | US |

### Widget Integration Steps

1. Browse widget options in Development Kits > Widget tab
2. Configure widget settings (provide domain URLs, max 10 root domains)
3. Obtain authentication token via **Get Widget Token** API
4. Integrate using Widget SDK

### Widget SDK

- Get Widget Token: https://partner.tiktokshop.com/docv2/page/get-widget-token
- Widget SDK User Guide: https://partner.tiktokshop.com/docv2/page/widget-sdk-user-guide

## Developer Tools

| Tool | Description |
|------|-------------|
| Seller Center Development Shops | Sandbox for testing |
| API Testing Tool | Interactive API testing in Partner Center |
| Developer Dashboard | Monitor app performance and usage |

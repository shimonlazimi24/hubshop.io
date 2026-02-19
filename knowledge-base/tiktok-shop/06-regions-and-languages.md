# TikTok Shop - Regions & Languages

## Locale Standard

Uses **IETF BCP 47** locale codes.

## Supported Regions (16 Countries)

| Country | Code | Default Locale | Region |
|---------|------|----------------|--------|
| United States | US | en-US | Americas |
| Brazil | BR | pt-BR | Americas |
| Mexico | MX | es-MX | Americas |
| United Kingdom | GB | en-GB | Europe |
| France | FR | fr-FR | Europe |
| Germany | DE | de-DE | Europe |
| Ireland | IE | en-IE | Europe |
| Italy | IT | it-IT | Europe |
| Spain | ES | es-ES | Europe |
| Indonesia | ID | id-ID | Southeast Asia |
| Malaysia | MY | ms-MY | Southeast Asia |
| Philippines | PH | en-PH | Southeast Asia |
| Singapore | SG | en-SG | Southeast Asia |
| Thailand | TH | th-TH | Southeast Asia |
| Vietnam | VN | vi-VN | Southeast Asia |
| Japan | JP | ja-JP | East Asia |

## Supported Languages (11)

| Language | Locale Codes |
|----------|-------------|
| English | en-GB, en-IE, en-PH, en-SG, en-US |
| French | fr-FR |
| German | de-DE |
| Indonesian | id-ID |
| Italian | it-IT |
| Japanese | ja-JP |
| Malay | ms-MY |
| Portuguese | pt-BR |
| Spanish | es-ES, es-MX |
| Thai | th-TH |
| Vietnamese | vi-VN |

## Regional API Differences

### Fulfillment
- **SEA markets**: Cannot split below SKU level
- **US/EMEA/LATAM/JP**: No restriction on splitting
- **Brazil**: Must upload invoice before shipping

### Affiliate APIs
- **UK and EU**: Affiliate Seller/Creator/Partner APIs NOT available

### Customer Engagement
- **US local sellers only**: Customer Engagement API restricted to US

### EU Compliance
- EU markets require GPSR Responsible Person/Manufacturer information on products
- Dedicated API endpoints for managing Manufacturer and Responsible Person entities

## Notes

- Global sellers based in China can pass `zh-CN` for machine-translated Chinese versions of property text
- Specifying Chinese text in text fields is NOT supported
- Cross-border operations use the Seller API for shop status and Global Product feature eligibility

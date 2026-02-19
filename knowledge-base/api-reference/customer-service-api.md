# Customer Service API Reference

## Description
Integrate buyer messaging with third-party customer support platforms. Manage conversations, send messages, configure agent settings.

## Endpoint Count: 10

## Endpoints

| # | Method | Endpoint | Doc |
|---|--------|----------|-----|
| 1 | POST | Create Conversation | [Link](https://partner.tiktokshop.com/docv2/page/create-conversation-202309) |
| 2 | GET | Get Conversations | [Link](https://partner.tiktokshop.com/docv2/page/get-conversations-202309) |
| 3 | GET | Get Conversation Messages | [Link](https://partner.tiktokshop.com/docv2/page/get-conversation-messages-202309) |
| 4 | POST | Upload Buyer Messages Image | [Link](https://partner.tiktokshop.com/docv2/page/upload-buyer-messages-image-202309) |
| 5 | POST | Send Message | [Link](https://partner.tiktokshop.com/docv2/page/send-message-202309) |
| 6 | POST | Read Message | [Link](https://partner.tiktokshop.com/docv2/page/read-message-202309) |
| 7 | GET | Get Agent Settings | [Link](https://partner.tiktokshop.com/docv2/page/get-agent-settings-202309) |
| 8 | PUT | Update Agent Settings | [Link](https://partner.tiktokshop.com/docv2/page/update-agent-settings-202309) |
| 9 | GET | Get CS Performance | [Link](https://partner.tiktokshop.com/docv2/page/get-customer-service-performance-202407) |
| 10 | GET | Get Conversation | [Link](https://partner.tiktokshop.com/docv2/page/get-conversation-202601) |

## Key Policies

- **Custom API access**: Requires 1,000+ authorized sellers or 1M+ API calls/day
- **24-hour response rate target**: >= 80%
- **Resolution rate target**: >= 65%
- **Customer satisfaction target**: >= 75%
- **Message types**: Text, Image, Emoji, Video, Product card, Order card, Logistic card, Order Reverse card, Coupon card
- Conversation auto-closes after 6 hours buyer inactivity or 7 days without seller response

## Webhooks
- New Conversation
- New Message

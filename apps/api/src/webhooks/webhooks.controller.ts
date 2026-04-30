import { Body, Controller, Headers, Post, Req } from "@nestjs/common";
import type { FrodoRequest } from "../tenancy/workspace-context";
import { computeWebhookIdempotencyKey } from "./idempotency";
import { WebhooksService } from "./webhooks.service";

@Controller("webhooks")
export class WebhooksController {
  constructor(private readonly webhooks: WebhooksService) {}

  /**
   * TikTok Shop webhook ingress.
   * Signature verification: TODO (use req.rawBody + app secret per TikTok docs).
   */
  @Post("shop")
  async shop(
    @Req() req: FrodoRequest,
    @Headers("x-idempotency-key") headerKey: string | undefined,
    @Body() body: Record<string, unknown>,
  ) {
    const eventType = String(body.type ?? body.event_type ?? "unknown");
    const rawBody =
      req.rawBody ?? Buffer.from(JSON.stringify(body ?? {}), "utf8");
    const idempotencyKey = computeWebhookIdempotencyKey(
      headerKey,
      rawBody,
      "shop",
      eventType,
    );

    const result = await this.webhooks.ingestShopWebhook({
      idempotencyKey,
      eventType,
      payload: body,
      workspaceId: null,
    });

    return { ok: true, ...result };
  }
}

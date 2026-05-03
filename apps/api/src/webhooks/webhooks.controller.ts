import {
  BadRequestException,
  Body,
  Controller,
  Headers,
  Logger,
  Post,
  Req,
  UnauthorizedException,
} from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import {
  DEFAULT_TIKTOK_WEBHOOK_MAX_SKEW_SECONDS,
  verifyTikTokShopWebhookSignature,
} from "@frodo/domain";
import type { FrodoRequest } from "../tenancy/workspace-context";
import { computeWebhookIdempotencyKey } from "./idempotency";
import { WebhooksService } from "./webhooks.service";

function firstHeader(
  v: string | string[] | undefined,
): string | undefined {
  if (v === undefined) return undefined;
  return Array.isArray(v) ? v[0] : v;
}

@Controller("webhooks")
export class WebhooksController {
  private readonly logger = new Logger(WebhooksController.name);

  constructor(
    private readonly webhooks: WebhooksService,
    private readonly config: ConfigService,
  ) {}

  /**
   * TikTok Shop webhook ingress.
   * Verifies `TikTok-Signature` (HMAC-SHA256 over `t + '.' + rawBody`) before DB/SQS — see `@frodo/domain` verifyTikTokShopWebhookSignature.
   */
  @Post("shop")
  async shop(
    @Req() req: FrodoRequest,
    @Headers("x-idempotency-key") headerKey: string | undefined,
    @Body() body: Record<string, unknown>,
  ) {
    const rawBody = req.rawBody;
    if (!rawBody?.length) {
      throw new BadRequestException(
        "webhook_missing_raw_body",
      );
    }

    const appEnv = this.config.get<string>("APP_ENV") ?? "development";
    const allowUnverified =
      appEnv === "development" &&
      this.config.get<boolean>("ALLOW_UNVERIFIED_WEBHOOKS") === true;

    if (!allowUnverified) {
      const secret =
        this.config.get<string>("TIKTOK_SHOP_APP_SECRET")?.trim() ?? "";
      const sigHeader =
        firstHeader(req.headers["tiktok-signature"]) ??
        firstHeader(req.headers["TikTok-Signature"]);

      const maxSkewConfigured = this.config.get<number>(
        "TIKTOK_WEBHOOK_MAX_SKEW_SECONDS",
      );
      const maxSkew =
        typeof maxSkewConfigured === "number" &&
        Number.isFinite(maxSkewConfigured) &&
        maxSkewConfigured > 0
          ? maxSkewConfigured
          : DEFAULT_TIKTOK_WEBHOOK_MAX_SKEW_SECONDS;

      const verified = verifyTikTokShopWebhookSignature({
        rawBody,
        signatureHeader: sigHeader,
        appSecret: secret,
        maxSkewSeconds: maxSkew,
      });

      if (!verified.ok) {
        this.logger.warn(`shop_webhook_verify_failed code=${verified.code}`);
        throw new UnauthorizedException("webhook_signature_invalid");
      }
    } else {
      this.logger.warn(
        "shop_webhook_verify_skipped development_allow_unverified_webhooks",
      );
    }

    const eventType = String(body.type ?? body.event_type ?? "unknown");
    const idempotencyKey = computeWebhookIdempotencyKey(
      headerKey,
      rawBody,
      "shop",
      eventType,
    );

    const ingestResult = await this.webhooks.ingestShopWebhook({
      idempotencyKey,
      eventType,
      payload: body,
      workspaceId: null,
    });

    return { ok: true, ...ingestResult };
  }
}

import { createHmac } from "node:crypto";
import { BadRequestException, UnauthorizedException } from "@nestjs/common";
import type { ConfigService } from "@nestjs/config";
import { describe, expect, it, vi } from "vitest";
import type { FrodoRequest } from "../tenancy/workspace-context";
import { WebhooksController } from "./webhooks.controller";
import type { WebhooksService } from "./webhooks.service";

describe("WebhooksController POST /webhooks/shop", () => {
  const secret = "webhook-test-secret-32chars!!";
  const bodyObj = { type: 5, shop_id: "s1" };
  const rawBody = Buffer.from(JSON.stringify(bodyObj), "utf8");
  const t = String(Math.floor(Date.now() / 1000));
  const sig = createHmac("sha256", secret)
    .update(`${t}.${rawBody.toString("utf8")}`, "utf8")
    .digest("hex");
  const tiktokHeader = `t=${t},s=${sig}`;

  function makeReq(over: Partial<FrodoRequest> = {}): FrodoRequest {
    return {
      rawBody,
      headers: { "tiktok-signature": tiktokHeader },
      ...over,
    } as FrodoRequest;
  }

  function cfg(partial: Record<string, unknown> = {}): ConfigService {
    const defaults: Record<string, unknown> = {
      APP_ENV: "development",
      ALLOW_UNVERIFIED_WEBHOOKS: false,
      TIKTOK_SHOP_APP_SECRET: secret,
      TIKTOK_WEBHOOK_MAX_SKEW_SECONDS: 300,
    };
    const merged = { ...defaults, ...partial };
    return {
      get: (k: string) => merged[k],
    } as unknown as ConfigService;
  }

  it("rejects missing raw body and does not ingest", async () => {
    const ingest = vi.fn();
    const ctrl = new WebhooksController(
      { ingestShopWebhook: ingest } as unknown as WebhooksService,
      cfg(),
    );
    await expect(
      ctrl.shop(
        { headers: {}, rawBody: undefined } as unknown as FrodoRequest,
        undefined,
        bodyObj,
      ),
    ).rejects.toThrow(BadRequestException);
    expect(ingest).not.toHaveBeenCalled();
  });

  it("rejects missing TikTok-Signature and does not ingest", async () => {
    const ingest = vi.fn();
    const ctrl = new WebhooksController(
      { ingestShopWebhook: ingest } as unknown as WebhooksService,
      cfg(),
    );
    await expect(
      ctrl.shop(makeReq({ headers: {} }), undefined, bodyObj),
    ).rejects.toThrow(UnauthorizedException);
    expect(ingest).not.toHaveBeenCalled();
  });

  it("rejects invalid signature and does not ingest", async () => {
    const ingest = vi.fn();
    const ctrl = new WebhooksController(
      { ingestShopWebhook: ingest } as unknown as WebhooksService,
      cfg(),
    );
    await expect(
      ctrl.shop(
        makeReq({
          headers: { "tiktok-signature": `t=${t},s=abcd` },
        }),
        undefined,
        bodyObj,
      ),
    ).rejects.toThrow(UnauthorizedException);
    expect(ingest).not.toHaveBeenCalled();
  });

  it("accepts valid signature and calls ingest", async () => {
    const ingest = vi
      .fn()
      .mockResolvedValue({ webhookEventId: "evt-1", duplicate: false });
    const ctrl = new WebhooksController(
      { ingestShopWebhook: ingest } as unknown as WebhooksService,
      cfg(),
    );
    await expect(ctrl.shop(makeReq(), undefined, bodyObj)).resolves.toEqual({
      ok: true,
      webhookEventId: "evt-1",
      duplicate: false,
    });
    expect(ingest).toHaveBeenCalledTimes(1);
    expect(ingest.mock.calls[0]?.[0]).toMatchObject({
      eventType: "5",
      workspaceId: null,
    });
  });

  it("skips verification only when development + ALLOW_UNVERIFIED_WEBHOOKS", async () => {
    const ingest = vi
      .fn()
      .mockResolvedValue({ webhookEventId: "x", duplicate: false });
    const ctrl = new WebhooksController(
      { ingestShopWebhook: ingest } as unknown as WebhooksService,
      cfg({
        ALLOW_UNVERIFIED_WEBHOOKS: true,
        TIKTOK_SHOP_APP_SECRET: "",
      }),
    );
    await ctrl.shop(makeReq({ headers: {} }), undefined, bodyObj);
    expect(ingest).toHaveBeenCalledTimes(1);
  });
});

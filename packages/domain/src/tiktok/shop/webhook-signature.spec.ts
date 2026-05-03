import { createHmac } from "node:crypto";
import { describe, expect, it } from "vitest";
import {
  DEFAULT_TIKTOK_WEBHOOK_MAX_SKEW_SECONDS,
  parseTikTokSignatureHeader,
  verifyTikTokShopWebhookSignature,
} from "./webhook-signature";

function sign(secret: string, t: string, body: Buffer): string {
  const signedPayload = `${t}.${body.toString("utf8")}`;
  return createHmac("sha256", secret).update(signedPayload, "utf8").digest("hex");
}

describe("parseTikTokSignatureHeader", () => {
  it("parses t and s", () => {
    expect(
      parseTikTokSignatureHeader(
        "t=1633174587,s=18494715036ac4416a1d0a673871a2edbcfc94d94bd88ccd2c5ec9b3425afe66",
      ),
    ).toEqual({
      t: "1633174587",
      s: "18494715036ac4416a1d0a673871a2edbcfc94d94bd88ccd2c5ec9b3425afe66",
    });
  });

  it("accepts reversed order", () => {
    expect(
      parseTikTokSignatureHeader(
        "s=abc,t=123",
      ),
    ).toEqual({ t: "123", s: "abc" });
  });

  it("returns null when incomplete", () => {
    expect(parseTikTokSignatureHeader("t=123")).toBeNull();
    expect(parseTikTokSignatureHeader(undefined)).toBeNull();
  });
});

describe("verifyTikTokShopWebhookSignature malformed header", () => {
  it("returns malformed when header present but unparsable", () => {
    const r = verifyTikTokShopWebhookSignature({
      rawBody: Buffer.from("{}"),
      signatureHeader: "not-a-key-value-pair",
      appSecret: "s".repeat(16),
      nowUnixSeconds: 1700000000,
    });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.code).toBe("malformed_signature_header");
  });
});

describe("verifyTikTokShopWebhookSignature", () => {
  const secret = "partner-app-secret-test-value";
  const body = Buffer.from('{"type":1,"shop_id":"x"}', "utf8");
  const t = "1700000100";
  const header = `t=${t},s=${sign(secret, t, body)}`;

  it("accepts valid signature", () => {
    const r = verifyTikTokShopWebhookSignature({
      rawBody: body,
      signatureHeader: header,
      appSecret: secret,
      nowUnixSeconds: 1700000100,
      maxSkewSeconds: DEFAULT_TIKTOK_WEBHOOK_MAX_SKEW_SECONDS,
    });
    expect(r).toEqual({ ok: true });
  });

  it("rejects tampered body", () => {
    const tampered = Buffer.from('{"type":2}', "utf8");
    const r = verifyTikTokShopWebhookSignature({
      rawBody: tampered,
      signatureHeader: header,
      appSecret: secret,
      nowUnixSeconds: 1700000100,
    });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.code).toBe("signature_mismatch");
  });

  it("rejects invalid signature hex", () => {
    const r = verifyTikTokShopWebhookSignature({
      rawBody: body,
      signatureHeader: `t=${t},s=not-hex`,
      appSecret: secret,
      nowUnixSeconds: 1700000100,
    });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.code).toBe("signature_mismatch");
  });

  it("rejects missing header", () => {
    const r = verifyTikTokShopWebhookSignature({
      rawBody: body,
      signatureHeader: undefined,
      appSecret: secret,
      nowUnixSeconds: 1700000100,
    });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.code).toBe("missing_signature_header");
  });

  it("rejects empty secret", () => {
    const r = verifyTikTokShopWebhookSignature({
      rawBody: body,
      signatureHeader: header,
      appSecret: "   ",
      nowUnixSeconds: 1700000100,
    });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.code).toBe("missing_app_secret");
  });

  it("rejects timestamp skew", () => {
    const r = verifyTikTokShopWebhookSignature({
      rawBody: body,
      signatureHeader: header,
      appSecret: secret,
      nowUnixSeconds: 1700000100 + 99999,
      maxSkewSeconds: 300,
    });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.code).toBe("timestamp_skew");
  });

  it("rejects malformed timestamp", () => {
    const badHeader = `t=not-a-number,s=${sign(secret, t, body)}`;
    const r = verifyTikTokShopWebhookSignature({
      rawBody: body,
      signatureHeader: badHeader,
      appSecret: secret,
      nowUnixSeconds: 1700000100,
    });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.code).toBe("invalid_timestamp");
  });
});

/**
 * TikTok Shop / TikTok Partner webhooks — signature verification per official docs:
 * https://developers.tiktok.com/doc/webhooks-verification
 *
 * Header: `TikTok-Signature` (HTTP headers are case-insensitive; Express uses lowercase keys).
 * Format: `t=<unix_seconds>,s=<hex_hmac>`
 *
 * signed_payload = `${t}.${raw_body_utf8}` (must match the exact POST body bytes TikTok signed).
 * HMAC-SHA256(key = app secret / client secret, message = signed_payload) → compare to `s` with timing-safe equality.
 *
 * Assumption: Shop Partner webhooks use the same scheme as the linked TikTok Developers doc. If TikTok
 * changes algorithms, extend this module rather than ad-hoc checks in the API layer.
 */

import { createHmac, timingSafeEqual } from "node:crypto";

export type TikTokWebhookVerifyFailureCode =
  | "missing_signature_header"
  | "malformed_signature_header"
  | "missing_app_secret"
  | "invalid_timestamp"
  | "timestamp_skew"
  | "signature_mismatch";

export type TikTokShopWebhookVerifyResult =
  | { ok: true }
  | { ok: false; code: TikTokWebhookVerifyFailureCode };

/** Default replay window if TikTok docs do not mandate a specific value (± seconds). */
export const DEFAULT_TIKTOK_WEBHOOK_MAX_SKEW_SECONDS = 300;

function hexToBuffer(hex: string): Buffer | null {
  const normalized = hex.trim();
  if (
    normalized.length === 0 ||
    normalized.length % 2 !== 0 ||
    !/^[0-9a-fA-F]+$/.test(normalized)
  ) {
    return null;
  }
  return Buffer.from(normalized, "hex");
}

/**
 * Parse `TikTok-Signature` value: comma-separated `t=...` and `s=...` pairs (order-independent).
 */
export function parseTikTokSignatureHeader(
  header: string | undefined,
): { t: string; s: string } | null {
  if (!header?.trim()) {
    return null;
  }
  let t: string | undefined;
  let s: string | undefined;
  for (const part of header.split(",")) {
    const trimmed = part.trim();
    const eq = trimmed.indexOf("=");
    if (eq <= 0) continue;
    const key = trimmed.slice(0, eq).trim();
    const val = trimmed.slice(eq + 1).trim();
    if (key === "t") t = val;
    else if (key === "s") s = val;
  }
  if (!t || !s) return null;
  return { t, s };
}

export function verifyTikTokShopWebhookSignature(input: {
  rawBody: Buffer;
  signatureHeader: string | undefined;
  appSecret: string;
  /** Max |now - t| in seconds (default DEFAULT_TIKTOK_WEBHOOK_MAX_SKEW_SECONDS). */
  maxSkewSeconds?: number;
  /** Unix seconds (defaults to Date.now()/1000). Injectable for tests. */
  nowUnixSeconds?: number;
}): TikTokShopWebhookVerifyResult {
  const secret = input.appSecret.trim();
  if (!secret) {
    return { ok: false, code: "missing_app_secret" };
  }

  const rawHeader = input.signatureHeader?.trim();
  if (!rawHeader) {
    return { ok: false, code: "missing_signature_header" };
  }

  const parsed = parseTikTokSignatureHeader(rawHeader);
  if (!parsed) {
    return { ok: false, code: "malformed_signature_header" };
  }

  const tsNum = Number(parsed.t);
  if (!Number.isFinite(tsNum) || tsNum < 1) {
    return { ok: false, code: "invalid_timestamp" };
  }

  const now =
    input.nowUnixSeconds ?? Math.floor(Date.now() / 1000);
  const maxSkew =
    input.maxSkewSeconds ?? DEFAULT_TIKTOK_WEBHOOK_MAX_SKEW_SECONDS;
  if (Math.abs(now - tsNum) > maxSkew) {
    return { ok: false, code: "timestamp_skew" };
  }

  const bodyUtf8 = input.rawBody.toString("utf8");
  const signedPayload = `${parsed.t}.${bodyUtf8}`;
  const expectedHex = createHmac("sha256", secret)
    .update(signedPayload, "utf8")
    .digest("hex");

  const receivedBuf = hexToBuffer(parsed.s);
  const expectedBuf = hexToBuffer(expectedHex);
  if (
    !receivedBuf ||
    !expectedBuf ||
    receivedBuf.length !== expectedBuf.length
  ) {
    return { ok: false, code: "signature_mismatch" };
  }

  try {
    if (!timingSafeEqual(receivedBuf, expectedBuf)) {
      return { ok: false, code: "signature_mismatch" };
    }
  } catch {
    return { ok: false, code: "signature_mismatch" };
  }

  return { ok: true };
}

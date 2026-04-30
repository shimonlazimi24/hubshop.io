import { createHash } from "node:crypto";

/** Prefer vendor/header idempotency; otherwise SHA-256(rawBody | platform | eventType). */
export function computeWebhookIdempotencyKey(
  headerKey: string | undefined,
  rawBody: Buffer,
  platform: string,
  eventType: string,
): string {
  if (headerKey?.trim()) {
    return headerKey.trim().slice(0, 255);
  }
  const h = createHash("sha256")
    .update(rawBody)
    .update("|")
    .update(platform)
    .update("|")
    .update(eventType)
    .digest("hex");
  return `sha256:${h}`;
}

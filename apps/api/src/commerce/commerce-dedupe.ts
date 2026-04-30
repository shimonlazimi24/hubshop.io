import { createHash } from "node:crypto";

/** Stable hourly dedupe for enqueue ↔ worker (UTC hour bucket). */
export function buildCommerceDedupeKey(
  workspaceId: string,
  shopId: string,
  kind: "orders" | "products",
): string {
  const hourBucket = new Date().toISOString().slice(0, 13);
  const raw = `${workspaceId}|${shopId}|${kind}|${hourBucket}`;
  return createHash("sha256").update(raw, "utf8").digest("hex");
}

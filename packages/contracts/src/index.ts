import { z } from "zod";

/** Discriminated job payloads sent on SQS (JSON body). */
export const jobEnvelopeSchema = z.discriminatedUnion("type", [
  z.object({
    type: z.literal("process_webhook_event"),
    webhookEventId: z.string().uuid(),
    workspaceId: z.string().uuid().nullable(),
    platform: z.enum(["shop", "developer", "marketing", "live", "research"]),
    eventType: z.string(),
  }),
  z.object({
    type: z.literal("token_refresh_tick"),
    scheduledJobRunId: z.string().uuid().optional(),
  }),
  z.object({
    type: z.literal("refresh_workspace_tokens"),
    workspaceId: z.string().uuid(),
    connectedAccountId: z.string().uuid(),
  }),
  z.object({
    type: z.literal("sync_shop_orders"),
    workspaceId: z.string().uuid(),
    /** Frodo `shops.id` (UUID), not TikTok `shop_id` string. */
    shopId: z.string().uuid(),
    connectedAccountId: z.string().uuid(),
    /** Stable idempotency for enqueue/worker dedupe (required from API). */
    dedupeKey: z.string().min(16).max(128),
    /** Optional paging / filtering hints (defensive; TikTok field names vary). */
    cursor: z.string().max(2048).optional(),
    createTimeGe: z.number().int().optional(),
    createTimeLe: z.number().int().optional(),
  }),
  z.object({
    type: z.literal("sync_shop_products"),
    workspaceId: z.string().uuid(),
    shopId: z.string().uuid(),
    connectedAccountId: z.string().uuid(),
    dedupeKey: z.string().min(16).max(128),
    cursor: z.string().max(2048).optional(),
  }),
  z.object({
    type: z.literal("emit_realtime_event"),
    workspaceId: z.string().uuid(),
    channel: z.string(),
    payload: z.record(z.unknown()),
  }),
  z.object({
    type: z.literal("shop_discovery_after_connect"),
    workspaceId: z.string().uuid(),
    connectedAccountId: z.string().uuid(),
    dedupeKey: z.string().min(16).max(128),
  }),
]);

export type JobEnvelope = z.infer<typeof jobEnvelopeSchema>;

export function parseJobEnvelope(raw: string): JobEnvelope {
  const json: unknown = JSON.parse(raw);
  return jobEnvelopeSchema.parse(json);
}

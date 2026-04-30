import { and, eq, or } from "drizzle-orm";
import { webhookEvents } from "@frodo/db";
import type { JobEnvelope } from "@frodo/contracts";
import type { FrodoDb } from "@frodo/db";

export async function handleWebhook(
  db: FrodoDb,
  job: Extract<JobEnvelope, { type: "process_webhook_event" }>,
): Promise<void> {
  const id = job.webhookEventId;

  const guard = and(
    eq(webhookEvents.id, id),
    or(
      eq(webhookEvents.status, "received"),
      eq(webhookEvents.status, "failed"),
    ),
  );

  const updated = await db
    .update(webhookEvents)
    .set({ status: "processing", updatedAt: new Date() })
    .where(guard)
    .returning({ id: webhookEvents.id });

  if (updated.length === 0) {
    return;
  }

  try {
    // Placeholder: route by platform/eventType and call TikTok APIs via @frodo/domain.
    await db
      .update(webhookEvents)
      .set({ status: "processed", updatedAt: new Date() })
      .where(eq(webhookEvents.id, id));
  } catch (e) {
    await db
      .update(webhookEvents)
      .set({
        status: "failed",
        errorMessage: String(e).slice(0, 1000),
        updatedAt: new Date(),
      })
      .where(eq(webhookEvents.id, id));
    throw e;
  }
}

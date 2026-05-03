import { scheduledJobRuns } from "@frodo/db";
import type { FrodoDb } from "@frodo/db";

/** Bucket per UTC hour to dedupe scheduled ticks across replicas. */
export async function handleTokenRefreshTick(db: FrodoDb): Promise<void> {
  const periodBucket = new Date().toISOString().slice(0, 13);
  const inserted = await db
    .insert(scheduledJobRuns)
    .values({
      jobKey: "token_refresh_tick",
      periodBucket,
    })
    .onConflictDoNothing({
      target: [scheduledJobRuns.jobKey, scheduledJobRuns.periodBucket],
    })
    .returning({ id: scheduledJobRuns.id });

  if (inserted.length === 0) {
    console.info("token_refresh_tick already ran this bucket; skip fan-out");
    return;
  }

  // Out of current Shop-only scope: enqueue `refresh_workspace_tokens` per account when token refresh is implemented (ADR job envelope already exists).
}

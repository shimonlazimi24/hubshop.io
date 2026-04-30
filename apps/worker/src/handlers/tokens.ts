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

  // Placeholder: query accounts due for refresh and enqueue refresh_workspace_tokens jobs.
  console.info("token_refresh_tick: enqueue per-account jobs (TODO)");
}

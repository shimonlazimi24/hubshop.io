import type { JobEnvelope } from "@frodo/contracts";
import type Redis from "ioredis";

export async function handleEmitRealtime(
  redis: Redis | null,
  job: Extract<JobEnvelope, { type: "emit_realtime_event" }>,
): Promise<void> {
  if (!redis) {
    return;
  }
  const channel = `frodo:workspace:${job.workspaceId}`;
  await redis.publish(
    channel,
    JSON.stringify({ channel: job.channel, payload: job.payload }),
  );
}

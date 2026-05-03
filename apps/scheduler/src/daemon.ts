import { loadSchedulerEnv } from "@frodo/config";

const env = loadSchedulerEnv();
const intervalMs = Math.max(
  10_000,
  Number(process.env.CRON_TICK_INTERVAL_MS ?? 60_000),
);

async function tickOnce(): Promise<void> {
  const url = new URL("/api/internal/cron/tick", env.CRON_BASE_URL);
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "X-Cron-Secret": env.INTERNAL_CRON_SECRET,
    },
  });
  const body = await res.text();
  if (!res.ok) {
    throw new Error(`Cron tick HTTP ${res.status}: ${body}`);
  }
  console.log(body);
}

async function main(): Promise<void> {
  console.info(
    `Scheduler daemon: POST /api/internal/cron/tick every ${intervalMs}ms → ${env.CRON_BASE_URL}`,
  );
  for (;;) {
    try {
      await tickOnce();
    } catch (e) {
      console.error(e instanceof Error ? e.message : e);
    }
    await new Promise((r) => setTimeout(r, intervalMs));
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

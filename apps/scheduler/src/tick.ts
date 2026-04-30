import { loadSchedulerEnv } from "@frodo/config";

const env = loadSchedulerEnv();
const url = new URL("/api/internal/cron/tick", env.CRON_BASE_URL);

const res = await fetch(url, {
  method: "POST",
  headers: {
    "X-Cron-Secret": env.INTERNAL_CRON_SECRET,
  },
});

if (!res.ok) {
  console.error(await res.text());
  process.exit(1);
}

console.log(await res.text());

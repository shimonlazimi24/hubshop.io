import { z } from "zod";

const schedulerSchema = z.object({
  CRON_BASE_URL: z.string().url(),
  INTERNAL_CRON_SECRET: z.string().min(8),
});

export type FrodoSchedulerEnv = z.infer<typeof schedulerSchema>;

export function loadSchedulerEnv(
  env: NodeJS.ProcessEnv = process.env,
): FrodoSchedulerEnv {
  const parsed = schedulerSchema.safeParse(env);
  if (!parsed.success) {
    throw new Error(
      `Invalid scheduler environment: ${JSON.stringify(parsed.error.flatten().fieldErrors)}`,
    );
  }
  return parsed.data;
}

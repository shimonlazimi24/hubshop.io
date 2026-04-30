import { z } from "zod";

const workerSchema = z.object({
  APP_ENV: z.enum(["development", "staging", "production"]).default("development"),
  DATABASE_URL: z
    .string()
    .min(
      1,
      "DATABASE_URL is required: PostgreSQL connection string for the worker (runtime only). Do not use DATABASE_MIGRATION_URL here — see docs/v2/ENVIRONMENT.md.",
    ),
  AWS_REGION: z.string().min(1),
  SQS_QUEUE_URL: z.string().min(1),
  REDIS_URL: z.string().optional(),
  /** ReceiveMessage visibility timeout (seconds). */
  SQS_VISIBILITY_TIMEOUT_SECONDS: z.coerce.number().int().min(30).max(43200).optional(),
  /** Additional visibility extension applied after receive (optional). */
  SQS_VISIBILITY_EXTENSION_SECONDS: z.coerce.number().int().min(0).max(43200).optional(),
  /** Max seconds to wait for in-flight jobs on shutdown. */
  WORKER_SHUTDOWN_DRAIN_SECONDS: z.coerce.number().int().min(1).max(600).optional(),
  TIKTOK_COMMERCE_PROBE_URL: z.string().url().optional(),
  AWS_ACCESS_KEY_ID: z.string().optional(),
  AWS_SECRET_ACCESS_KEY: z.string().optional(),
  TOKEN_ENCRYPTION_KEY: z.string().optional(),
  TIKTOK_SHOP_APP_KEY: z.string().optional(),
  TIKTOK_SHOP_APP_SECRET: z.string().optional(),
  TIKTOK_OPEN_API_BASE: z.string().url().optional(),
});

export type FrodoWorkerEnv = z.infer<typeof workerSchema>;

export function loadWorkerEnv(
  env: NodeJS.ProcessEnv = process.env,
): FrodoWorkerEnv {
  const parsed = workerSchema.safeParse(env);
  if (!parsed.success) {
    throw new Error(
      `Invalid worker environment: ${JSON.stringify(parsed.error.flatten().fieldErrors)}`,
    );
  }
  return parsed.data;
}

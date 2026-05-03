import { z } from "zod";

function envBool(v: unknown): boolean | undefined {
  if (v === undefined || v === "") {
    return undefined;
  }
  if (typeof v === "boolean") {
    return v;
  }
  const s = String(v).toLowerCase();
  if (s === "true" || s === "1" || s === "yes") {
    return true;
  }
  if (s === "false" || s === "0" || s === "no") {
    return false;
  }
  return undefined;
}

const workerSchema = z
  .object({
    APP_ENV: z.enum(["development", "staging", "production"]).default("development"),
    DATABASE_URL: z
      .string()
      .min(
        1,
        "DATABASE_URL is required: PostgreSQL connection string for the worker (runtime only). Do not use DATABASE_MIGRATION_URL here — see docs/v2/ENVIRONMENT.md.",
      ),
    /**
     * When `true` and `APP_ENV=development`, the worker stays up without AWS/SQS (no job consumption).
     * For staging/production you must set `AWS_REGION` and `SQS_QUEUE_URL` instead.
     */
    WORKER_SQS_DISABLED: z.preprocess(envBool, z.boolean().optional()),
    AWS_REGION: z.string().optional(),
    SQS_QUEUE_URL: z.string().optional(),
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
  })
  .superRefine((data, ctx) => {
    const sqsDisabled = data.WORKER_SQS_DISABLED === true;
    if (sqsDisabled && data.APP_ENV !== "development") {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["WORKER_SQS_DISABLED"],
        message:
          "WORKER_SQS_DISABLED is only allowed when APP_ENV=development (set real SQS for staging/production).",
      });
    }
    if (!sqsDisabled) {
      if (!data.AWS_REGION?.trim()) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["AWS_REGION"],
          message: "Required unless WORKER_SQS_DISABLED=true with APP_ENV=development.",
        });
      }
      if (!data.SQS_QUEUE_URL?.trim()) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["SQS_QUEUE_URL"],
          message: "Required unless WORKER_SQS_DISABLED=true with APP_ENV=development.",
        });
      }
    }
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

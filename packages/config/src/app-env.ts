import { z } from "zod";

export const appEnvironmentSchema = z.enum([
  "development",
  "staging",
  "production",
]);

export type AppEnvironment = z.infer<typeof appEnvironmentSchema>;

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

const baseApiSchema = z.object({
  APP_ENV: appEnvironmentSchema.default("development"),
  NODE_ENV: z.string().optional(),
  DATABASE_URL: z
    .string()
    .min(
      1,
      "DATABASE_URL is required: PostgreSQL connection string for the API (runtime only). For Drizzle migrations use DATABASE_MIGRATION_URL or DATABASE_URL in the migrate context — see docs/v2/ENVIRONMENT.md.",
    ),
  JWT_SECRET: z.string().min(16, "JWT_SECRET must be at least 16 characters"),
  JWT_ACCESS_EXPIRE_MINUTES: z.coerce.number().int().positive().optional(),
  JWT_REFRESH_EXPIRE_DAYS: z.coerce.number().int().positive().optional(),
  REDIS_URL: z.string().optional(),
  REQUIRE_REDIS_FOR_AUTH: z.preprocess(
    (v) => envBool(v),
    z.boolean().optional(),
  ),
  ALLOW_ASYNC_SKIP: z.preprocess((v) => envBool(v), z.boolean().optional()),
  AWS_REGION: z.string().optional(),
  AWS_ACCESS_KEY_ID: z.string().optional(),
  AWS_SECRET_ACCESS_KEY: z.string().optional(),
  SQS_QUEUE_URL: z.string().optional(),
  TOKEN_ENCRYPTION_KEY: z.string().optional(),
  PUBLIC_WEB_ORIGIN: z.string().optional(),
  PORT: z.coerce.number().int().positive().optional(),
  INTERNAL_CRON_SECRET: z.string().optional(),
  /** TikTok Shop Partner Open API (OAuth + signed requests). */
  TIKTOK_SHOP_APP_KEY: z.string().optional(),
  TIKTOK_SHOP_APP_SECRET: z.string().optional(),
  TIKTOK_SHOP_SERVICE_ID: z.string().optional(),
  /** Must match Partner Center redirect URL exactly (e.g. http://localhost:8001/api/connect/shop/callback). */
  TIKTOK_SHOP_REDIRECT_URI: z.string().optional(),
  TIKTOK_SHOP_AUTH_BASE: z.string().optional(),
  TIKTOK_TOKEN_URL: z.string().optional(),
  TIKTOK_OPEN_API_BASE: z.string().optional(),
  /** Defaults to JWT_SECRET when unset; used only for Shop OAuth `state` signing. */
  SHOP_OAUTH_STATE_SECRET: z.string().optional(),
});

export type ApiEnvInput = z.input<typeof baseApiSchema>;

export type FrodoApiEnv = z.infer<typeof baseApiSchema> & {
  readonly effectiveRequireRedis: boolean;
  readonly effectiveAllowAsyncSkip: boolean;
  readonly sqsRequired: boolean;
};

function refineApiEnv(
  parsed: z.infer<typeof baseApiSchema>,
): FrodoApiEnv {
  const appEnv = parsed.APP_ENV;
  const allowSkipExplicit = parsed.ALLOW_ASYNC_SKIP === true;

  if (allowSkipExplicit && appEnv !== "development") {
    throw new Error(
      "ALLOW_ASYNC_SKIP is only permitted when APP_ENV=development (local dev only)",
    );
  }

  const allowSkip = appEnv === "development" && allowSkipExplicit === true;

  const requireRedisDefault =
    appEnv === "staging" || appEnv === "production";
  const requireRedis =
    parsed.REQUIRE_REDIS_FOR_AUTH !== undefined
      ? parsed.REQUIRE_REDIS_FOR_AUTH
      : requireRedisDefault;

  const sqsRequired = !allowSkip;

  if (sqsRequired) {
    if (!parsed.AWS_REGION?.trim()) {
      throw new Error(
        "AWS_REGION is required unless APP_ENV=development and ALLOW_ASYNC_SKIP=true",
      );
    }
    if (!parsed.SQS_QUEUE_URL?.trim()) {
      throw new Error(
        "SQS_QUEUE_URL is required unless APP_ENV=development and ALLOW_ASYNC_SKIP=true",
      );
    }
  }

  if (requireRedis) {
    if (!parsed.REDIS_URL?.trim()) {
      throw new Error(
        "REDIS_URL is required when REQUIRE_REDIS_FOR_AUTH is true (default in staging/production) for JWT blacklist/logout",
      );
    }
  }

  return {
    ...parsed,
    effectiveRequireRedis: requireRedis,
    effectiveAllowAsyncSkip: allowSkip,
    sqsRequired,
  };
}

/** Validates API process env. Call at bootstrap before Nest starts. */
export function loadApiEnv(
  env: NodeJS.ProcessEnv = process.env,
): FrodoApiEnv {
  const raw = { ...env };
  const parsed = baseApiSchema.safeParse(raw);
  if (!parsed.success) {
    const msg = parsed.error.flatten().fieldErrors;
    throw new Error(`Invalid API environment: ${JSON.stringify(msg)}`);
  }
  return refineApiEnv(parsed.data);
}

/** Nest ConfigModule validate hook — receives merged env. */
export function validateApiEnvForNest(
  config: Record<string, unknown>,
): FrodoApiEnv {
  return loadApiEnv(config as NodeJS.ProcessEnv);
}

import { describe, expect, it } from "vitest";
import { loadApiEnv } from "./app-env";

describe("loadApiEnv", () => {
  it("allows development with ALLOW_ASYNC_SKIP without SQS", () => {
    const env = loadApiEnv({
      APP_ENV: "development",
      DATABASE_URL: "postgresql://localhost/db",
      JWT_SECRET: "0123456789abcdef",
      ALLOW_ASYNC_SKIP: "true",
    });
    expect(env.effectiveAllowAsyncSkip).toBe(true);
    expect(env.sqsRequired).toBe(false);
  });

  it("rejects ALLOW_ASYNC_SKIP in staging", () => {
    expect(() =>
      loadApiEnv({
        APP_ENV: "staging",
        DATABASE_URL: "postgresql://localhost/db",
        JWT_SECRET: "0123456789abcdef",
        ALLOW_ASYNC_SKIP: "true",
        AWS_REGION: "us-east-1",
        SQS_QUEUE_URL: "https://sqs.us-east-1.amazonaws.com/123/q",
        REDIS_URL: "redis://localhost:6379",
        TIKTOK_SHOP_APP_SECRET: "tiktok-test-secret-for-staging-env",
      }),
    ).toThrow(/ALLOW_ASYNC_SKIP/);
  });

  it("requires SQS in staging", () => {
    expect(() =>
      loadApiEnv({
        APP_ENV: "staging",
        DATABASE_URL: "postgresql://localhost/db",
        JWT_SECRET: "0123456789abcdef",
        REDIS_URL: "redis://localhost:6379",
        TIKTOK_SHOP_APP_SECRET: "tiktok-test-secret-for-staging-env",
      }),
    ).toThrow(/AWS_REGION/);
  });

  it("requires Redis by default in staging", () => {
    expect(() =>
      loadApiEnv({
        APP_ENV: "staging",
        DATABASE_URL: "postgresql://localhost/db",
        JWT_SECRET: "0123456789abcdef",
        AWS_REGION: "us-east-1",
        SQS_QUEUE_URL: "https://sqs.us-east-1.amazonaws.com/123/q",
        TIKTOK_SHOP_APP_SECRET: "tiktok-test-secret-for-staging-env",
      }),
    ).toThrow(/REDIS_URL/);
  });

  it("requires TIKTOK_SHOP_APP_SECRET in staging", () => {
    expect(() =>
      loadApiEnv({
        APP_ENV: "staging",
        DATABASE_URL: "postgresql://localhost/db",
        JWT_SECRET: "0123456789abcdef",
        AWS_REGION: "us-east-1",
        SQS_QUEUE_URL: "https://sqs.us-east-1.amazonaws.com/123/q",
        REDIS_URL: "redis://localhost:6379",
      }),
    ).toThrow(/TIKTOK_SHOP_APP_SECRET/);
  });

  it("rejects ALLOW_UNVERIFIED_WEBHOOKS outside development", () => {
    expect(() =>
      loadApiEnv({
        APP_ENV: "staging",
        DATABASE_URL: "postgresql://localhost/db",
        JWT_SECRET: "0123456789abcdef",
        AWS_REGION: "us-east-1",
        SQS_QUEUE_URL: "https://sqs.us-east-1.amazonaws.com/123/q",
        REDIS_URL: "redis://localhost:6379",
        TIKTOK_SHOP_APP_SECRET: "tiktok-test-secret-for-staging-env",
        ALLOW_UNVERIFIED_WEBHOOKS: "true",
      }),
    ).toThrow(/ALLOW_UNVERIFIED_WEBHOOKS/);
  });

  it("requires TIKTOK_SHOP_APP_SECRET in production", () => {
    expect(() =>
      loadApiEnv({
        APP_ENV: "production",
        DATABASE_URL: "postgresql://localhost/db",
        JWT_SECRET: "0123456789abcdef",
        AWS_REGION: "us-east-1",
        SQS_QUEUE_URL: "https://sqs.us-east-1.amazonaws.com/123/q",
        REDIS_URL: "redis://localhost:6379",
      }),
    ).toThrow(/TIKTOK_SHOP_APP_SECRET/);
  });

  it("allows production when TikTok secret is set", () => {
    const env = loadApiEnv({
      APP_ENV: "production",
      DATABASE_URL: "postgresql://localhost/db",
      JWT_SECRET: "0123456789abcdef",
      AWS_REGION: "us-east-1",
      SQS_QUEUE_URL: "https://sqs.us-east-1.amazonaws.com/123/q",
      REDIS_URL: "redis://localhost:6379",
      TIKTOK_SHOP_APP_SECRET: "tiktok-test-secret-for-production-env",
    });
    expect(env.TIKTOK_SHOP_APP_SECRET).toBe("tiktok-test-secret-for-production-env");
  });
});

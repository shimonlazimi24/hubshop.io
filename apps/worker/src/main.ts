import {
  ChangeMessageVisibilityCommand,
  DeleteMessageCommand,
  ReceiveMessageCommand,
  SQSClient,
} from "@aws-sdk/client-sqs";
import { createHash } from "node:crypto";
import { loadWorkerEnv } from "@frodo/config";
import { createDb } from "@frodo/db";
import { parseJobEnvelope, type JobEnvelope } from "@frodo/contracts";
import { dispatch } from "./dispatch";
import Redis from "ioredis";
import { isZodError } from "./parse-errors";

let env: ReturnType<typeof loadWorkerEnv>;
try {
  env = loadWorkerEnv();
} catch (e) {
  console.error(
    e instanceof Error ? e.message : e,
  );
  console.error(
    "Worker requires valid environment variables (DATABASE_URL, AWS_REGION, SQS_QUEUE_URL, …). See docs/v2/ENVIRONMENT.md.",
  );
  process.exit(1);
}

if (env.WORKER_SQS_DISABLED === true) {
  console.warn(
    "WORKER_SQS_DISABLED: SQS polling is off (APP_ENV=development only). Set AWS_REGION + SQS_QUEUE_URL and unset WORKER_SQS_DISABLED to consume jobs.",
  );
  const id = setInterval(() => {
    console.info("worker idle (WORKER_SQS_DISABLED)");
  }, 300_000);
  const shutdown = (): void => {
    clearInterval(id);
    process.exit(0);
  };
  process.once("SIGINT", shutdown);
  process.once("SIGTERM", shutdown);
} else {
const sqs = new SQSClient({ region: env.AWS_REGION! });
const db = createDb(env.DATABASE_URL);
const redisClient = env.REDIS_URL ? new Redis(env.REDIS_URL) : null;

const receiveVisibility =
  env.SQS_VISIBILITY_TIMEOUT_SECONDS ?? 300;
const extendVisibility = env.SQS_VISIBILITY_EXTENSION_SECONDS ?? 0;

let shuttingDown = false;

function fingerprint(body: string | undefined): string {
  return createHash("sha256")
    .update(body ?? "", "utf8")
    .digest("hex")
    .slice(0, 16);
}

async function extendVisibilityIfConfigured(
  receiptHandle: string,
): Promise<void> {
  if (!extendVisibility) {
    return;
  }
  await sqs.send(
    new ChangeMessageVisibilityCommand({
      QueueUrl: env.SQS_QUEUE_URL,
      ReceiptHandle: receiptHandle,
      VisibilityTimeout: receiveVisibility + extendVisibility,
    }),
  );
}

function isPoisonParseError(e: unknown): boolean {
  return e instanceof SyntaxError || isZodError(e);
}

function parseJobOrPoison(body: string | undefined): JobEnvelope {
  try {
    return parseJobEnvelope(body ?? "");
  } catch (e) {
    if (isPoisonParseError(e)) {
      const wrapped = new Error("poison parse") as Error & {
        poison?: boolean;
        cause?: unknown;
      };
      wrapped.poison = true;
      wrapped.cause = e;
      throw wrapped;
    }
    throw e;
  }
}

async function processMessage(
  body: string | undefined,
  receiptHandle: string,
): Promise<void> {
  await extendVisibilityIfConfigured(receiptHandle);

  let job: JobEnvelope;
  try {
    job = parseJobOrPoison(body);
  } catch (e) {
    const err = e as { poison?: boolean; cause?: unknown };
    if (err.poison) {
      console.error(
        `Deleting poison message fingerprint=${fingerprint(body)}`,
        err.cause ?? e,
      );
      await sqs.send(
        new DeleteMessageCommand({
          QueueUrl: env.SQS_QUEUE_URL,
          ReceiptHandle: receiptHandle,
        }),
      );
      return;
    }
    throw e;
  }

  try {
    await dispatch(db, job, redisClient);
  } catch (e) {
    console.error(
      `Dispatch failed fingerprint=${fingerprint(body)} (message returns to queue for retry)`,
      e,
    );
    throw e;
  }

  await sqs.send(
    new DeleteMessageCommand({
      QueueUrl: env.SQS_QUEUE_URL,
      ReceiptHandle: receiptHandle,
    }),
  );
}

async function run(): Promise<void> {
  process.on("SIGINT", () => {
    shuttingDown = true;
    console.info("SIGINT received, stopping poll loop…");
  });
  process.on("SIGTERM", () => {
    shuttingDown = true;
    console.info("SIGTERM received, stopping poll loop…");
  });

  while (!shuttingDown) {
    const out = await sqs.send(
      new ReceiveMessageCommand({
        QueueUrl: env.SQS_QUEUE_URL,
        MaxNumberOfMessages: 5,
        WaitTimeSeconds: shuttingDown ? 0 : 20,
        VisibilityTimeout: receiveVisibility,
      }),
    );

    const messages = out.Messages ?? [];
    if (messages.length === 0) {
      if (shuttingDown) {
        break;
      }
      continue;
    }

    for (const m of messages) {
      const receipt = m.ReceiptHandle;
      const body = m.Body;
      if (!receipt) {
        continue;
      }
      try {
        await processMessage(body, receipt);
      } catch {
        // Retry via SQS visibility / DLQ policy (dispatch failure only)
      }
    }
  }

  if (redisClient) {
    redisClient.disconnect();
  }
  console.info("Worker exited cleanly");
}

run().catch((e) => {
  console.error(e);
  process.exit(1);
});
}

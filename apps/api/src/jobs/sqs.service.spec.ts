import { ServiceUnavailableException } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { describe, expect, it, vi } from "vitest";
import { SqsService } from "./sqs.service";

describe("SqsService", () => {
  it("throws when SQS is not configured", async () => {
    const config = {
      get: vi.fn((key: string) => {
        if (key === "sqsRequired") {
          return false;
        }
        if (key === "SQS_QUEUE_URL") {
          return undefined;
        }
        if (key === "AWS_REGION") {
          return undefined;
        }
        return undefined;
      }),
    } as unknown as ConfigService;

    const svc = new SqsService(config);
    await expect(
      svc.sendJob({
        type: "token_refresh_tick",
      }),
    ).rejects.toThrow(ServiceUnavailableException);
  });
});

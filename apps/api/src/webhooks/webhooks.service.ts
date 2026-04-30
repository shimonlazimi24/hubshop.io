import { Injectable, Logger } from "@nestjs/common";
import { Inject } from "@nestjs/common";
import { eq } from "drizzle-orm";
import { webhookEvents } from "@frodo/db";
import type { FrodoDb } from "@frodo/db";
import { DRIZZLE } from "../database/database.module";
import { SqsService } from "../jobs/sqs.service";

@Injectable()
export class WebhooksService {
  private readonly logger = new Logger(WebhooksService.name);

  constructor(
    @Inject(DRIZZLE) private readonly db: FrodoDb,
    private readonly sqs: SqsService,
  ) {}

  async ingestShopWebhook(input: {
    idempotencyKey: string;
    eventType: string;
    payload: Record<string, unknown>;
    workspaceId: string | null;
  }): Promise<{ webhookEventId: string; duplicate: boolean }> {
    const inserted = await this.db
      .insert(webhookEvents)
      .values({
        platform: "shop",
        eventType: input.eventType,
        idempotencyKey: input.idempotencyKey,
        payload: input.payload,
        status: "received",
        workspaceId: input.workspaceId,
      })
      .onConflictDoNothing({ target: webhookEvents.idempotencyKey })
      .returning({ id: webhookEvents.id });

    if (inserted.length === 0) {
      const existing = await this.db
        .select({ id: webhookEvents.id })
        .from(webhookEvents)
        .where(eq(webhookEvents.idempotencyKey, input.idempotencyKey))
        .limit(1);

      return {
        webhookEventId: existing[0]?.id ?? "",
        duplicate: true,
      };
    }

    const row = inserted[0];

    try {
      await this.sqs.sendJob({
        type: "process_webhook_event",
        webhookEventId: row.id,
        workspaceId: input.workspaceId,
        platform: "shop",
        eventType: input.eventType,
      });
    } catch (err) {
      await this.db.delete(webhookEvents).where(eq(webhookEvents.id, row.id));
      this.logger.error(
        `Webhook row rolled back after failed enqueue: ${row.id}`,
        err,
      );
      throw err;
    }

    return { webhookEventId: row.id, duplicate: false };
  }
}

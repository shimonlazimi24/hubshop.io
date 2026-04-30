import { Controller, Post, UseGuards } from "@nestjs/common";
import { SqsService } from "../jobs/sqs.service";
import { CronSecretGuard } from "./cron-secret.guard";

/**
 * Enqueue-only scheduler tick (Railway Cron or external cron POSTs here).
 */
@Controller("internal/cron")
export class SchedulerController {
  constructor(private readonly sqs: SqsService) {}

  @Post("tick")
  @UseGuards(CronSecretGuard)
  async tick() {
    await this.sqs.sendJob({ type: "token_refresh_tick" });
    return { ok: true, enqueued: "token_refresh_tick" };
  }
}

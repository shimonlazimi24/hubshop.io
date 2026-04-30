import { Module } from "@nestjs/common";
import { JobsModule } from "../jobs/jobs.module";
import { SchedulerController } from "./scheduler.controller";

@Module({
  imports: [JobsModule],
  controllers: [SchedulerController],
})
export class SchedulerModule {}

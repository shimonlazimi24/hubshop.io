import { validateApiEnvForNest } from "@frodo/config";
import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";
import { AuthModule } from "./auth/auth.module";
import { CommerceModule } from "./commerce/commerce.module";
import { ConnectModule } from "./connect/connect.module";
import { DatabaseModule } from "./database/database.module";
import { FeatureFlagsModule } from "./feature-flags/feature-flags.module";
import { HealthModule } from "./health/health.module";
import { InternalDebugModule } from "./internal/internal-debug.module";
import { JobsModule } from "./jobs/jobs.module";
import { RealtimeModule } from "./realtime/realtime.module";
import { RedisModule } from "./redis/redis.module";
import { SchedulerModule } from "./scheduler/scheduler.module";
import { TenancyModule } from "./tenancy/tenancy.module";
import { WebhooksModule } from "./webhooks/webhooks.module";
import { WorkspacesModule } from "./workspaces/workspaces.module";

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      validate: validateApiEnvForNest,
    }),
    DatabaseModule,
    RedisModule,
    TenancyModule,
    JobsModule,
    HealthModule,
    AuthModule,
    WorkspacesModule,
    ConnectModule,
    WebhooksModule,
    CommerceModule,
    RealtimeModule,
    FeatureFlagsModule,
    SchedulerModule,
    InternalDebugModule,
  ],
})
export class AppModule {}

import { Module } from "@nestjs/common";
import { AuthModule } from "../auth/auth.module";
import { RedisModule } from "../redis/redis.module";
import { TenancyModule } from "../tenancy/tenancy.module";
import { RealtimeController } from "./realtime.controller";

@Module({
  imports: [RedisModule, TenancyModule, AuthModule],
  controllers: [RealtimeController],
})
export class RealtimeModule {}

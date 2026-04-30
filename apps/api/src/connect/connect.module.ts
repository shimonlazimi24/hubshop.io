import { Module } from "@nestjs/common";
import { AuthModule } from "../auth/auth.module";
import { JobsModule } from "../jobs/jobs.module";
import { TenancyModule } from "../tenancy/tenancy.module";
import { ConnectController } from "./connect.controller";
import { ConnectService } from "./connect.service";

@Module({
  imports: [JobsModule, TenancyModule, AuthModule],
  controllers: [ConnectController],
  providers: [ConnectService],
})
export class ConnectModule {}

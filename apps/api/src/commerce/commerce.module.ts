import { Module } from "@nestjs/common";
import { AuthModule } from "../auth/auth.module";
import { JobsModule } from "../jobs/jobs.module";
import { TenancyModule } from "../tenancy/tenancy.module";
import { CommerceController } from "./commerce.controller";
import { CommerceService } from "./commerce.service";

@Module({
  imports: [JobsModule, TenancyModule, AuthModule],
  controllers: [CommerceController],
  providers: [CommerceService],
})
export class CommerceModule {}

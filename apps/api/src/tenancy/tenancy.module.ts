import { Module } from "@nestjs/common";
import { WorkspaceMembershipGuard } from "./workspace-membership.guard";

@Module({
  providers: [WorkspaceMembershipGuard],
  exports: [WorkspaceMembershipGuard],
})
export class TenancyModule {}

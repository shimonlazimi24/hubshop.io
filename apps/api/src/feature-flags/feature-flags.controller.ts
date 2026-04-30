import {
  Body,
  Controller,
  Get,
  Param,
  Put,
  UseGuards,
} from "@nestjs/common";
import { IsBoolean } from "class-validator";
import { AuthGuard } from "@nestjs/passport";
import { WorkspaceCtx } from "../tenancy/workspace.decorators";
import type { WorkspaceRequestContext } from "../tenancy/workspace-context";
import { WorkspaceMembershipGuard } from "../tenancy/workspace-membership.guard";
import { FeatureFlagsService } from "./feature-flags.service";

class SetFlagDto {
  @IsBoolean()
  enabled!: boolean;
}

@Controller("feature-flags")
@UseGuards(AuthGuard("jwt"), WorkspaceMembershipGuard)
export class FeatureFlagsController {
  constructor(private readonly flags: FeatureFlagsService) {}

  @Get()
  async list(@WorkspaceCtx() ws: WorkspaceRequestContext) {
    return this.flags.list(ws.workspaceId);
  }

  @Put(":flagKey")
  async set(
    @WorkspaceCtx() ws: WorkspaceRequestContext,
    @Param("flagKey") flagKey: string,
    @Body() body: SetFlagDto,
  ) {
    await this.flags.set(ws.workspaceId, flagKey, body.enabled);
    return { ok: true };
  }
}

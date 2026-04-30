import { Controller, Get, Req, UseGuards } from "@nestjs/common";
import type { Request } from "express";
import { AuthGuard } from "@nestjs/passport";
import type { AccessJwtPayload } from "../auth/jwt.strategy";
import { WorkspacesService } from "./workspaces.service";

@Controller("workspaces")
@UseGuards(AuthGuard("jwt"))
export class WorkspacesController {
  constructor(private readonly workspaces: WorkspacesService) {}

  @Get()
  async list(@Req() req: Request & { user: AccessJwtPayload }) {
    return this.workspaces.listForUser(req.user.sub);
  }
}

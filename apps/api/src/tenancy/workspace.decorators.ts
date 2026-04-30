import {
  createParamDecorator,
  ExecutionContext,
  InternalServerErrorException,
} from "@nestjs/common";
import type { WorkspaceRequestContext } from "./workspace-context";

export const WorkspaceCtx = createParamDecorator(
  (_data: unknown, ctx: ExecutionContext): WorkspaceRequestContext => {
    const req = ctx.switchToHttp().getRequest<{
      workspaceContext?: WorkspaceRequestContext;
    }>();
    const w = req.workspaceContext;
    if (!w) {
      throw new InternalServerErrorException(
        "Workspace context missing — use WorkspaceMembershipGuard",
      );
    }
    return w;
  },
);

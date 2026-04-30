import {
  BadRequestException,
  CanActivate,
  ExecutionContext,
  ForbiddenException,
  Injectable,
  UnauthorizedException,
} from "@nestjs/common";
import { Inject } from "@nestjs/common";
import { and, eq } from "drizzle-orm";
import { memberships, users } from "@frodo/db";
import type { FrodoDb } from "@frodo/db";
import { DRIZZLE } from "../database/database.module";
import type { AccessJwtPayload } from "../auth/jwt.strategy";
import type { WorkspaceRequestContext } from "./workspace-context";
import { parseUuidParam } from "./parse-uuid";

@Injectable()
export class WorkspaceMembershipGuard implements CanActivate {
  constructor(@Inject(DRIZZLE) private readonly db: FrodoDb) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const req = context.switchToHttp().getRequest<{
      user?: AccessJwtPayload;
      headers: Record<string, string | string[] | undefined>;
      query: Record<string, string | string[] | undefined>;
      params: Record<string, string | undefined>;
      workspaceContext?: WorkspaceRequestContext;
    }>();

    const user = req.user;
    if (!user?.sub) {
      throw new UnauthorizedException();
    }

    const headerWs =
      (req.headers["x-workspace-id"] as string | undefined) ??
      (req.headers["X-Workspace-Id"] as string | undefined);
    const queryWs = req.query["workspaceId"];
    const paramWs = req.params["workspaceId"];

    const raw =
      (typeof headerWs === "string" ? headerWs : undefined) ??
      (typeof queryWs === "string" ? queryWs : Array.isArray(queryWs) ? queryWs[0] : undefined) ??
      paramWs;

    if (!raw?.trim()) {
      throw new BadRequestException(
        "Workspace scope requires X-Workspace-Id header or workspaceId in route/query",
      );
    }

    const workspaceId = parseUuidParam("Workspace id", raw);

    const [row] = await this.db
      .select({
        membershipId: memberships.id,
        organizationId: memberships.organizationId,
        workspaceId: memberships.workspaceId,
        role: memberships.role,
      })
      .from(memberships)
      .innerJoin(users, eq(users.id, memberships.userId))
      .where(
        and(
          eq(memberships.userId, user.sub),
          eq(memberships.workspaceId, workspaceId),
          eq(users.isActive, true),
        ),
      )
      .limit(1);

    if (!row?.workspaceId) {
      throw new ForbiddenException("No membership for this workspace");
    }

    req.workspaceContext = {
      workspaceId: row.workspaceId,
      organizationId: row.organizationId,
      membershipId: row.membershipId,
      role: row.role,
    };

    return true;
  }
}

import { Injectable } from "@nestjs/common";
import { Inject } from "@nestjs/common";
import { and, eq, isNotNull } from "drizzle-orm";
import { memberships, workspaces } from "@frodo/db";
import type { FrodoDb } from "@frodo/db";
import { DRIZZLE } from "../database/database.module";

@Injectable()
export class WorkspacesService {
  constructor(@Inject(DRIZZLE) private readonly db: FrodoDb) {}

  async listForUser(userId: string) {
    const rows = await this.db
      .select({
        id: workspaces.id,
        name: workspaces.name,
        slug: workspaces.slug,
        organizationId: workspaces.organizationId,
        role: memberships.role,
      })
      .from(memberships)
      .innerJoin(workspaces, eq(workspaces.id, memberships.workspaceId))
      .where(
        and(eq(memberships.userId, userId), isNotNull(memberships.workspaceId)),
      );

    return { workspaces: rows };
  }
}

import { Injectable } from "@nestjs/common";
import { Inject } from "@nestjs/common";
import { eq, and } from "drizzle-orm";
import { featureFlags } from "@frodo/db";
import type { FrodoDb } from "@frodo/db";
import { DRIZZLE } from "../database/database.module";

@Injectable()
export class FeatureFlagsService {
  constructor(@Inject(DRIZZLE) private readonly db: FrodoDb) {}

  async list(workspaceId: string) {
    return this.db
      .select()
      .from(featureFlags)
      .where(eq(featureFlags.workspaceId, workspaceId));
  }

  async set(
    workspaceId: string,
    flagKey: string,
    enabled: boolean,
  ): Promise<void> {
    await this.db
      .insert(featureFlags)
      .values({ workspaceId, flagKey, enabled })
      .onConflictDoUpdate({
        target: [featureFlags.workspaceId, featureFlags.flagKey],
        set: { enabled, updatedAt: new Date() },
      });
  }

  async isEnabled(workspaceId: string, flagKey: string): Promise<boolean> {
    const [row] = await this.db
      .select({ enabled: featureFlags.enabled })
      .from(featureFlags)
      .where(
        and(
          eq(featureFlags.workspaceId, workspaceId),
          eq(featureFlags.flagKey, flagKey),
        ),
      )
      .limit(1);
    return row?.enabled ?? false;
  }
}

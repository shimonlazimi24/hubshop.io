import {
  BadRequestException,
  Controller,
  Get,
  Inject,
  Query,
  UseGuards,
} from "@nestjs/common";
import type { FrodoDb } from "@frodo/db";
import {
  validateShopConnectForWorkspace,
  type ShopConnectValidationResult,
} from "@frodo/db";
import { DRIZZLE } from "../database/database.module";
import { ShopConnectDebugGuard } from "./shop-connect-debug.guard";

const DETAIL_MAX = 280;

function scrubDetail(detail: string): string {
  if (detail.length <= DETAIL_MAX) {
    return detail;
  }
  return `${detail.slice(0, DETAIL_MAX)}…`;
}

export type ShopConnectDebugStatusResponse = Omit<
  ShopConnectValidationResult,
  "checks"
> & {
  checks: Array<{ name: string; ok: boolean; detail: string }>;
};

/**
 * Ops/validation endpoint — does **not** check JWT or WorkspaceMembershipGuard.
 * Non-production: open on local networks; production: hidden unless INTERNAL_CRON_SECRET + header (see ShopConnectDebugGuard).
 */
@Controller("internal/debug")
@UseGuards(ShopConnectDebugGuard)
export class InternalDebugShopConnectController {
  constructor(@Inject(DRIZZLE) private readonly db: FrodoDb) {}

  /** Redacted snapshot only — never returns tokens or vault ciphertext. */
  @Get("shop-connect-status")
  async shopConnectStatus(
    @Query("workspaceId") workspaceId?: string,
  ): Promise<ShopConnectDebugStatusResponse> {
    if (!workspaceId?.trim()) {
      throw new BadRequestException("workspaceId query parameter is required");
    }

    const result = await validateShopConnectForWorkspace(
      this.db,
      workspaceId.trim(),
    );

    return {
      workspaceId: result.workspaceId,
      summary: result.summary,
      meta: result.meta,
      checks: result.checks.map((c) => ({
        name: c.name,
        ok: c.ok,
        detail: scrubDetail(c.detail),
      })),
    };
  }
}

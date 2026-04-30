import { ForbiddenException } from "@nestjs/common";
import { describe, expect, it, vi } from "vitest";
import type { ExecutionContext } from "@nestjs/common";
import type { FrodoDb } from "@frodo/db";
import { WorkspaceMembershipGuard } from "./workspace-membership.guard";
import type { AccessJwtPayload } from "../auth/jwt.strategy";

function mockCtx(
  user: AccessJwtPayload | undefined,
  headers: Record<string, string>,
  query: Record<string, string> = {},
): ExecutionContext {
  const request = { user, headers, query, params: {} as Record<string, string> };
  return {
    switchToHttp: () => ({
      getRequest: () => request,
    }),
  } as ExecutionContext;
}

describe("WorkspaceMembershipGuard", () => {
  const ws = "11111111-1111-4111-8111-111111111111";
  const org = "22222222-2222-4222-8222-222222222222";
  const mid = "33333333-3333-4333-8333-333333333333";
  const uid = "44444444-4444-4444-8444-444444444444";

  const row = {
    membershipId: mid,
    organizationId: org,
    workspaceId: ws,
    role: "owner" as const,
  };

  function makeDb(returnRows: typeof row[] | "throw") {
    const limit = vi.fn().mockResolvedValue(returnRows === "throw" ? [] : returnRows);
    const where = vi.fn().mockReturnValue({ limit });
    const innerJoin = vi.fn().mockReturnValue({ where });
    const from = vi.fn().mockReturnValue({ innerJoin });
    const select = vi.fn().mockReturnValue({ from });
    return { select } as unknown as FrodoDb;
  }

  it("allows access when membership exists", async () => {
    const guard = new WorkspaceMembershipGuard(makeDb([row]));
    const ctx = mockCtx(
      { sub: uid, type: "access" },
      { "x-workspace-id": ws },
    );
    await expect(guard.canActivate(ctx)).resolves.toBe(true);
    const req = ctx.switchToHttp().getRequest() as {
      workspaceContext?: { workspaceId: string };
    };
    expect(req.workspaceContext?.workspaceId).toBe(ws);
  });

  it("denies when there is no active membership (other workspace, inactive user, or missing row)", async () => {
    const guard = new WorkspaceMembershipGuard(makeDb([]));
    const ctx = mockCtx(
      { sub: uid, type: "access" },
      { "x-workspace-id": ws },
    );
    await expect(guard.canActivate(ctx)).rejects.toThrow(ForbiddenException);
  });

  it("rejects missing workspace id", async () => {
    const guard = new WorkspaceMembershipGuard(makeDb([row]));
    const ctx = mockCtx({ sub: uid, type: "access" }, {});
    await expect(guard.canActivate(ctx)).rejects.toThrow(/Workspace scope/);
  });

  it("reads workspace id from query", async () => {
    const guard = new WorkspaceMembershipGuard(makeDb([row]));
    const ctx = mockCtx(
      { sub: uid, type: "access" },
      {},
      { workspaceId: ws },
    );
    await expect(guard.canActivate(ctx)).resolves.toBe(true);
  });
});

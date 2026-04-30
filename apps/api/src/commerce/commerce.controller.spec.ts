import { describe, expect, it, vi } from "vitest";
import type { WorkspaceRequestContext } from "../tenancy/workspace-context";
import { CommerceController } from "./commerce.controller";
import type { CommerceService } from "./commerce.service";

const WS: WorkspaceRequestContext = {
  workspaceId: "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
  organizationId: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
  membershipId: "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
  role: "owner",
};

describe("CommerceController", () => {
  it("delegates sync-status to service with workspace scope", async () => {
    const getShopSyncStatus = vi.fn().mockResolvedValue({
      shopId: "22222222-2222-4222-8222-222222222222",
      shopName: "Test",
      latestProductSync: null,
      latestOrderSync: null,
    });
    const ctrl = new CommerceController({
      getShopSyncStatus,
    } as unknown as CommerceService);

    const out = await ctrl.syncStatus(
      WS,
      "22222222-2222-4222-8222-222222222222",
    );

    expect(getShopSyncStatus).toHaveBeenCalledWith(
      WS.workspaceId,
      "22222222-2222-4222-8222-222222222222",
    );
    expect(out.shopName).toBe("Test");
  });
});

import { describe, expect, it } from "vitest";
import { parseJobEnvelope } from "@frodo/contracts";

describe("sync_shop_products envelope", () => {
  it("parses with connectedAccountId", () => {
    const j = parseJobEnvelope(
      JSON.stringify({
        type: "sync_shop_products",
        workspaceId: "11111111-1111-4111-8111-111111111111",
        shopId: "22222222-2222-4222-8222-222222222222",
        connectedAccountId: "33333333-3333-4333-8333-333333333333",
        dedupeKey: "a".repeat(32),
      }),
    );
    expect(j.type).toBe("sync_shop_products");
    expect(j.connectedAccountId).toBeDefined();
  });
});

describe("sync_shop_orders envelope", () => {
  it("parses optional time window", () => {
    const j = parseJobEnvelope(
      JSON.stringify({
        type: "sync_shop_orders",
        workspaceId: "11111111-1111-4111-8111-111111111111",
        shopId: "22222222-2222-4222-8222-222222222222",
        connectedAccountId: "33333333-3333-4333-8333-333333333333",
        dedupeKey: "b".repeat(32),
        createTimeGe: 100,
        createTimeLe: 200,
        cursor: "cur",
      }),
    );
    expect(j.type).toBe("sync_shop_orders");
    expect(j.createTimeGe).toBe(100);
    expect(j.cursor).toBe("cur");
  });
});

describe("shop_discovery_after_connect envelope", () => {
  it("parses from JSON", () => {
    const j = parseJobEnvelope(
      JSON.stringify({
        type: "shop_discovery_after_connect",
        workspaceId: "11111111-1111-4111-8111-111111111111",
        connectedAccountId: "22222222-2222-4222-8222-222222222222",
        dedupeKey: "shop_discovery:22222222-2222-4222-8222-222222222222",
      }),
    );
    expect(j.type).toBe("shop_discovery_after_connect");
    expect(j.dedupeKey.startsWith("shop_discovery:")).toBe(true);
  });
});

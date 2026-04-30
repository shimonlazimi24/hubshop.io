import { describe, expect, it } from "vitest";
import { shopDiscoveryDedupeKey } from "./connect.service";

describe("shopDiscoveryDedupeKey", () => {
  it("is stable per connected account", () => {
    const id = "33333333-3333-4333-8333-333333333333";
    expect(shopDiscoveryDedupeKey(id)).toBe(`shop_discovery:${id}`);
    expect(shopDiscoveryDedupeKey(id).length).toBeGreaterThanOrEqual(16);
  });
});

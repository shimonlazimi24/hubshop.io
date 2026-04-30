import { describe, expect, it } from "vitest";
import { generateShopSign } from "./shop-sign";

describe("generateShopSign", () => {
  it("matches TikTok sample shape (deterministic for fixed inputs)", () => {
    const sign = generateShopSign({
      pathname: "/product/202309/products/search",
      query: { app_key: "x", timestamp: "123" },
      body: { page_size: 20 },
      appSecret: "secret",
    });
    expect(sign).toHaveLength(64);
    expect(sign).toMatch(/^[a-f0-9]+$/);
  });

  it("matches deterministic vector for GET authorized shops path", () => {
    const sign = generateShopSign({
      pathname: "/authorization/202309/shops",
      query: { app_key: "testkey", timestamp: "1700000000" },
      appSecret: "mysecret",
    });
    expect(sign).toBe(
      "0c8a91b1e5136455c811b8c930d3debe92cde2cca218182cb0c30b722f4260eb",
    );
  });
});

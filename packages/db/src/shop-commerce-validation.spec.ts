import { describe, expect, it } from "vitest";
import {
  formatShopCommerceValidationReport,
  type ShopCommerceValidationResult,
} from "./shop-commerce-validation";

describe("formatShopCommerceValidationReport", () => {
  it("prints OVERALL line", () => {
    const result: ShopCommerceValidationResult = {
      workspaceId: "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
      shopInternalId: "22222222-2222-4222-8222-222222222222",
      summary: "PASS",
      checks: [{ name: "shop_in_workspace", ok: true, detail: "ok" }],
      meta: {
        shopTiktokId: "tiktok-shop-id",
        productRowCount: 1,
        orderRowCount: 0,
        productsWithSnapshot: 1,
        ordersWithSnapshot: 0,
        latestProductJobStatus: "completed",
        latestOrderJobStatus: null,
      },
    };
    const text = formatShopCommerceValidationReport(result);
    expect(text).toContain("OVERALL: PASS");
    expect(text).toContain("latest_jobs");
  });
});

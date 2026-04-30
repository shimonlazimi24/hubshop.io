import { describe, expect, it } from "vitest";
import {
  extractOrderSearchPage,
  extractProductSearchPage,
  normalizeOrderRecord,
  normalizeProductRecord,
} from "./commerce-parse";

describe("extractProductSearchPage", () => {
  it("reads products array and cursor", () => {
    const raw = {
      code: 0,
      data: {
        products: [{ id: "p1", product_name: "A" }],
        next_page_token: "nxt",
      },
    };
    const out = extractProductSearchPage(raw);
    expect(out.items).toHaveLength(1);
    expect(out.nextCursor).toBe("nxt");
  });
});

describe("extractOrderSearchPage", () => {
  it("reads order_list", () => {
    const raw = {
      code: 0,
      data: {
        order_list: [{ order_id: "o1", order_status: "UNPAID" }],
      },
    };
    const out = extractOrderSearchPage(raw);
    expect(out.items).toHaveLength(1);
  });

  it("uses data.orders when order_list empty", () => {
    const raw = {
      code: 0,
      data: {
        order_list: [],
        orders: [{ order_id: "from_orders" }],
      },
    };
    const out = extractOrderSearchPage(raw);
    expect(out.items).toHaveLength(1);
    expect((out.items[0] as { order_id?: string }).order_id).toBe(
      "from_orders",
    );
  });

  it("reads next_page_token as nextCursor", () => {
    const raw = {
      code: 0,
      data: {
        orders: [{ order_id: "o1" }],
        next_page_token: "tok-next",
      },
    };
    expect(extractOrderSearchPage(raw).nextCursor).toBe("tok-next");
  });

  it("reads cursor field as nextCursor when next_page_token absent", () => {
    const raw = {
      code: 0,
      data: {
        orders: [],
        cursor: "cursor-page-2",
      },
    };
    expect(extractOrderSearchPage(raw).nextCursor).toBe("cursor-page-2");
  });

  it("returns empty items for empty lists", () => {
    expect(
      extractOrderSearchPage({
        code: 0,
        data: { order_list: [], orders: [] },
      }).items,
    ).toEqual([]);
  });

  it("handles unexpected root shape without throwing", () => {
    expect(extractOrderSearchPage(null).items).toEqual([]);
    expect(extractOrderSearchPage("x").items).toEqual([]);
    expect(extractOrderSearchPage({ code: 0 }).items).toEqual([]);
  });
});

describe("normalizeProductRecord", () => {
  it("maps minimal fields", () => {
    const row = normalizeProductRecord({
      id: "pid",
      product_name: "Widget",
      status: "live",
    });
    expect(row?.platformProductId).toBe("pid");
    expect(row?.title).toBe("Widget");
    expect(row?.status).toBe("live");
  });
});

describe("normalizeOrderRecord", () => {
  it("maps minimal fields", () => {
    const row = normalizeOrderRecord({
      order_id: "oid",
      order_status: "completed",
      payment: { total_amount: "12.00", currency: "USD" },
    });
    expect(row?.platformOrderId).toBe("oid");
    expect(row?.status).toBe("completed");
    expect(row?.totalAmount).toBe("12.00");
  });

  it("accepts id as platform order id", () => {
    const row = normalizeOrderRecord({
      id: "alt-id",
      status: "delivered",
      currency: "EUR",
      total: "9.99",
    });
    expect(row?.platformOrderId).toBe("alt-id");
    expect(row?.status).toBe("delivered");
    expect(row?.totalAmount).toBe("9.99");
    expect(row?.currency).toBe("EUR");
  });

  it("uses defaults when payment and totals missing", () => {
    const row = normalizeOrderRecord({
      order_id: "o-min",
      order_status: "UNPAID",
    });
    expect(row?.totalAmount).toBe("0");
    expect(row?.currency).toBe("USD");
    expect(row?.itemCount).toBe(0);
    expect(row?.fulfillmentType).toBeNull();
  });

  it("uses item_count when line_items absent", () => {
    const row = normalizeOrderRecord({
      order_id: "o-c",
      order_status: "completed",
      item_count: 3,
    });
    expect(row?.itemCount).toBe(3);
  });

  it("maps unknown status to unpaid", () => {
    const row = normalizeOrderRecord({
      order_id: "o-x",
      order_status: "MYSTERY_STATUS",
    });
    expect(row?.status).toBe("unpaid");
  });

  it("returns null when no order id", () => {
    expect(normalizeOrderRecord({ status: "completed" })).toBeNull();
  });
});

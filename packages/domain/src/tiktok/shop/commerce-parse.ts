/** Defensive parsing for TikTok Shop product/order search responses (shapes vary by API version). */

function asRecord(v: unknown): Record<string, unknown> | null {
  return typeof v === "object" && v !== null ? (v as Record<string, unknown>) : null;
}

function str(v: unknown): string | undefined {
  return typeof v === "string" ? v : undefined;
}

function num(v: unknown): number | undefined {
  if (typeof v === "number" && Number.isFinite(v)) {
    return v;
  }
  if (typeof v === "string" && /^\d+$/.test(v)) {
    return Number(v);
  }
  return undefined;
}

function firstArray(value: unknown): unknown[] {
  if (Array.isArray(value)) {
    return value;
  }
  return [];
}

/** Pull list + cursor from search/list payloads. */
export function extractProductSearchPage(raw: unknown): {
  items: Record<string, unknown>[];
  nextCursor?: string;
} {
  const root = asRecord(raw);
  const data = asRecord(root?.data) ?? root;
  const candidates = [
    data?.products,
    data?.product_list,
    data?.items,
    root?.products,
  ];
  let items: unknown[] = [];
  for (const c of candidates) {
    const arr = firstArray(c);
    if (arr.length > 0) {
      items = arr;
      break;
    }
  }
  const next =
    str(data?.next_page_token) ??
    str(data?.page_token) ??
    str(data?.cursor) ??
    str(root?.next_page_token);
  const recs: Record<string, unknown>[] = [];
  for (const it of items) {
    const r = asRecord(it);
    if (r) {
      recs.push(r);
    }
  }
  return { items: recs, nextCursor: next };
}

export function extractOrderSearchPage(raw: unknown): {
  items: Record<string, unknown>[];
  nextCursor?: string;
} {
  const root = asRecord(raw);
  const data = asRecord(root?.data) ?? root;
  const candidates = [
    data?.order_list,
    data?.orders,
    data?.items,
    root?.orders,
  ];
  let items: unknown[] = [];
  for (const c of candidates) {
    const arr = firstArray(c);
    if (arr.length > 0) {
      items = arr;
      break;
    }
  }
  const next =
    str(data?.next_page_token) ??
    str(data?.cursor) ??
    str(root?.next_page_token);
  const recs: Record<string, unknown>[] = [];
  for (const it of items) {
    const r = asRecord(it);
    if (r) {
      recs.push(r);
    }
  }
  return { items: recs, nextCursor: next };
}

export type NormalizedProductRow = {
  platformProductId: string;
  title: string;
  status:
    | "draft"
    | "pending"
    | "live"
    | "seller_deactivated"
    | "platform_deactivated"
    | "frozen"
    | "deleted";
  mainImageUrl: string | null;
  priceAmount: string | null;
  currency: string | null;
  inventoryTotal: number;
  skuCount: number;
  detailJson: Record<string, unknown>;
};

export type NormalizedOrderRow = {
  platformOrderId: string;
  status:
    | "unpaid"
    | "on_hold"
    | "awaiting_shipment"
    | "awaiting_collection"
    | "partially_shipping"
    | "in_transit"
    | "delivered"
    | "completed"
    | "cancelled";
  totalAmount: string;
  currency: string;
  itemCount: number;
  fulfillmentType: string | null;
  detailJson: Record<string, unknown>;
};

const PRODUCT_STATUS_MAP: Record<string, NormalizedProductRow["status"]> = {
  draft: "draft",
  pending: "pending",
  live: "live",
  activate: "live",
  active: "live",
  seller_deactivated: "seller_deactivated",
  platform_deactivated: "platform_deactivated",
  frozen: "frozen",
  deleted: "deleted",
};

const ORDER_STATUS_MAP: Record<string, NormalizedOrderRow["status"]> = {
  unpaid: "unpaid",
  on_hold: "on_hold",
  awaiting_shipment: "awaiting_shipment",
  awaiting_collection: "awaiting_collection",
  partially_shipping: "partially_shipping",
  in_transit: "in_transit",
  delivered: "delivered",
  completed: "completed",
  cancelled: "cancelled",
  canceled: "cancelled",
};

export function normalizeProductRecord(
  item: Record<string, unknown>,
): NormalizedProductRow | null {
  const platformProductId =
    str(item.id) ??
    str(item.product_id) ??
    str(item["product_id"]);
  if (!platformProductId) {
    return null;
  }

  const title =
    str(item.product_name) ??
    str(item.title) ??
    str(item.name) ??
    "Product";

  const rawStatus =
    str(item.status) ?? str(item.product_status) ?? "draft";
  const normStatus = rawStatus.toLowerCase().replace(/-/g, "_");
  const status =
    PRODUCT_STATUS_MAP[normStatus] ??
    PRODUCT_STATUS_MAP[(normStatus.split(":")[0] ?? "").trim()] ??
    "draft";

  const mainImage =
    str(item.main_image_url) ??
    str(item.cover_image_url) ??
    (() => {
      const imgs = item.images ?? item.image_list;
      if (Array.isArray(imgs) && imgs.length > 0) {
        const first = imgs[0];
        if (typeof first === "string") {
          return first;
        }
        const r = asRecord(first);
        return str(r?.url) ?? str(r?.uri);
      }
      return undefined;
    })();

  let price: string | undefined;
  let currency: string | undefined;
  let priceObj = asRecord(item.price);
  if (!priceObj && Array.isArray(item.skus) && item.skus[0]) {
    priceObj = asRecord(item.skus[0]);
  }
  if (priceObj) {
    price =
      str(priceObj.sale_price) ??
      str(priceObj.price) ??
      str(priceObj.amount);
    currency = str(priceObj.currency) ?? str(priceObj.currency_code);
  }
  const skuList = item.skus ?? item.sku_list;
  const skuCount = Array.isArray(skuList) ? skuList.length : num(item.sku_count) ?? 0;
  const inventoryTotal =
    num(item.inventory_quantity) ??
    num(item.stock_quantity) ??
    num(item.total_inventory) ??
    0;

  return {
    platformProductId,
    title,
    status,
    mainImageUrl: mainImage ?? null,
    priceAmount: price ?? null,
    currency: currency ?? null,
    inventoryTotal,
    skuCount,
    detailJson: item,
  };
}

export function normalizeOrderRecord(
  item: Record<string, unknown>,
): NormalizedOrderRow | null {
  const platformOrderId =
    str(item.order_id) ??
    str(item.id) ??
    str(item["order_id"]);
  if (!platformOrderId) {
    return null;
  }

  const rawStatus =
    str(item.order_status) ?? str(item.status) ?? "unpaid";
  const norm = rawStatus.toLowerCase().replace(/-/g, "_");
  const status = ORDER_STATUS_MAP[norm] ?? "unpaid";

  const pay = asRecord(item.payment) ?? item;
  const totalAmount =
    str(pay?.total_amount) ??
    str(item.payment_amount) ??
    str(item.total) ??
    "0";
  const currency =
    str(pay?.currency) ??
    str(item.currency) ??
    "USD";

  const lines = item.line_items ?? item.items ?? item.sku_list;
  const itemCount = Array.isArray(lines)
    ? lines.length
    : num(item.item_count) ?? 0;

  const fulfillmentType =
    str(item.fulfillment_type) ?? str(item.delivery_type) ?? null;

  return {
    platformOrderId,
    status,
    totalAmount,
    currency,
    itemCount,
    fulfillmentType,
    detailJson: item,
  };
}

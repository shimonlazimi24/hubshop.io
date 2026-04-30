import { and, desc, eq, sql } from "drizzle-orm";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import * as schema from "./schema";
import { orders, products, shops, syncJobs } from "./schema";

type CommerceValidationDb = PostgresJsDatabase<typeof schema>;

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export type ShopCommerceValidationSummary = "PASS" | "FAIL";

export interface ShopCommerceValidationCheck {
  name: string;
  ok: boolean;
  detail: string;
}

export interface ShopCommerceValidationResult {
  workspaceId: string;
  shopInternalId: string;
  summary: ShopCommerceValidationSummary;
  checks: ShopCommerceValidationCheck[];
  meta: {
    shopTiktokId: string | null;
    productRowCount: number;
    orderRowCount: number;
    productsWithSnapshot: number;
    ordersWithSnapshot: number;
    latestProductJobStatus: string | null;
    latestOrderJobStatus: string | null;
  };
}

function push(
  checks: ShopCommerceValidationCheck[],
  name: string,
  ok: boolean,
  detail: string,
): void {
  checks.push({ name, ok, detail });
}

export async function validateShopCommerceForWorkspace(
  db: CommerceValidationDb,
  workspaceId: string,
  shopInternalId: string,
): Promise<ShopCommerceValidationResult> {
  const checks: ShopCommerceValidationCheck[] = [];

  if (!UUID_RE.test(workspaceId.trim()) || !UUID_RE.test(shopInternalId.trim())) {
    push(checks, "uuid_format", false, "workspaceId and shopId must be UUIDs");
    return {
      workspaceId,
      shopInternalId,
      summary: "FAIL",
      checks,
      meta: {
        shopTiktokId: null,
        productRowCount: 0,
        orderRowCount: 0,
        productsWithSnapshot: 0,
        ordersWithSnapshot: 0,
        latestProductJobStatus: null,
        latestOrderJobStatus: null,
      },
    };
  }

  const ws = workspaceId.trim();
  const sid = shopInternalId.trim();

  const [shop] = await db
    .select({
      id: shops.id,
      shopIdStr: shops.shopId,
      connectedAccountId: shops.connectedAccountId,
    })
    .from(shops)
    .where(and(eq(shops.workspaceId, ws), eq(shops.id, sid)))
    .limit(1);

  if (!shop) {
    push(checks, "shop_in_workspace", false, "no shops row for workspace + shop id");
    return {
      workspaceId: ws,
      shopInternalId: sid,
      summary: "FAIL",
      checks,
      meta: {
        shopTiktokId: null,
        productRowCount: 0,
        orderRowCount: 0,
        productsWithSnapshot: 0,
        ordersWithSnapshot: 0,
        latestProductJobStatus: null,
        latestOrderJobStatus: null,
      },
    };
  }

  push(
    checks,
    "shop_in_workspace",
    true,
    `shop tiktok_id=${shop.shopIdStr} connected_account=${shop.connectedAccountId}`,
  );

  const [latestProductJob] = await db
    .select({
      status: syncJobs.status,
      itemsSynced: syncJobs.itemsSynced,
      errorMessage: syncJobs.errorMessage,
    })
    .from(syncJobs)
    .where(
      and(
        eq(syncJobs.workspaceId, ws),
        eq(syncJobs.connectedAccountId, shop.connectedAccountId),
        eq(syncJobs.syncType, "products"),
      ),
    )
    .orderBy(desc(syncJobs.createdAt))
    .limit(1);

  const [latestOrderJob] = await db
    .select({
      status: syncJobs.status,
      itemsSynced: syncJobs.itemsSynced,
      errorMessage: syncJobs.errorMessage,
    })
    .from(syncJobs)
    .where(
      and(
        eq(syncJobs.workspaceId, ws),
        eq(syncJobs.connectedAccountId, shop.connectedAccountId),
        eq(syncJobs.syncType, "orders"),
      ),
    )
    .orderBy(desc(syncJobs.createdAt))
    .limit(1);

  const prodJobFailed = latestProductJob?.status === "failed";
  push(
    checks,
    "latest_product_sync_job",
    !prodJobFailed,
    latestProductJob
      ? `status=${latestProductJob.status} items=${latestProductJob.itemsSynced}${latestProductJob.errorMessage ? ` err=${JSON.stringify(latestProductJob.errorMessage.slice(0, 120))}` : ""}`
      : "no sync_jobs row with sync_type=products yet",
  );

  const ordJobFailed = latestOrderJob?.status === "failed";
  push(
    checks,
    "latest_order_sync_job",
    !ordJobFailed,
    latestOrderJob
      ? `status=${latestOrderJob.status} items=${latestOrderJob.itemsSynced}${latestOrderJob.errorMessage ? ` err=${JSON.stringify(latestOrderJob.errorMessage.slice(0, 120))}` : ""}`
      : "no sync_jobs row with sync_type=orders yet",
  );

  const [{ c: productRowCount }] = await db
    .select({ c: sql<number>`count(*)::int` })
    .from(products)
    .where(
      and(eq(products.workspaceId, ws), eq(products.shopId, sid)),
    );

  const [{ c: orderRowCount }] = await db
    .select({ c: sql<number>`count(*)::int` })
    .from(orders)
    .where(and(eq(orders.workspaceId, ws), eq(orders.shopId, sid)));

  push(
    checks,
    "product_rows",
    true,
    `${productRowCount} product row(s) for shop (informational)`,
  );

  push(
    checks,
    "order_rows",
    true,
    `${orderRowCount} order row(s) for shop (informational)`,
  );

  const [{ c: snapP }] = await db
    .select({ c: sql<number>`count(*)::int` })
    .from(products)
    .where(
      and(
        eq(products.workspaceId, ws),
        eq(products.shopId, sid),
        sql`${products.apiSnapshotJson} IS NOT NULL`,
      ),
    );

  const [{ c: snapO }] = await db
    .select({ c: sql<number>`count(*)::int` })
    .from(orders)
    .where(
      and(
        eq(orders.workspaceId, ws),
        eq(orders.shopId, sid),
        sql`${orders.apiSnapshotJson} IS NOT NULL`,
      ),
    );

  push(
    checks,
    "product_api_snapshots",
    snapP === productRowCount || productRowCount === 0,
    `${snapP}/${productRowCount} products have api_snapshot_json`,
  );

  push(
    checks,
    "order_api_snapshots",
    snapO === orderRowCount || orderRowCount === 0,
    `${snapO}/${orderRowCount} orders have api_snapshot_json`,
  );

  const failed = checks.filter((c) => !c.ok);
  const summary: ShopCommerceValidationSummary =
    failed.length === 0 ? "PASS" : "FAIL";

  return {
    workspaceId: ws,
    shopInternalId: sid,
    summary,
    checks,
    meta: {
      shopTiktokId: shop.shopIdStr,
      productRowCount,
      orderRowCount,
      productsWithSnapshot: snapP,
      ordersWithSnapshot: snapO,
      latestProductJobStatus: latestProductJob?.status ?? null,
      latestOrderJobStatus: latestOrderJob?.status ?? null,
    },
  };
}

export function formatShopCommerceValidationReport(
  result: ShopCommerceValidationResult,
): string {
  const lines: string[] = [
    "=== TikTok Shop Commerce — validation ===",
    `Workspace: ${result.workspaceId}`,
    `Shop (internal id): ${result.shopInternalId}`,
    "",
  ];

  for (const c of result.checks) {
    const mark = c.ok ? "PASS" : "FAIL";
    lines.push(`[${mark}] ${c.name}`);
    lines.push(`       ${c.detail}`);
    lines.push("");
  }

  lines.push("--- Summary ---");
  lines.push(`(meta) tiktok_shop_id=${result.meta.shopTiktokId}`);
  lines.push(
    `(meta) products=${result.meta.productRowCount} orders=${result.meta.orderRowCount} snapshots P/O=${result.meta.productsWithSnapshot}/${result.meta.ordersWithSnapshot}`,
  );
  lines.push(
    `(meta) latest_jobs products=${result.meta.latestProductJobStatus ?? "none"} orders=${result.meta.latestOrderJobStatus ?? "none"}`,
  );
  lines.push("");
  lines.push(`OVERALL: ${result.summary}`);
  return lines.join("\n");
}

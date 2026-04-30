import { and, eq } from "drizzle-orm";
import type { FrodoWorkerEnv } from "@frodo/config";
import { loadWorkerEnv } from "@frodo/config";
import type { JobEnvelope } from "@frodo/contracts";
import {
  connectedAccounts,
  orders,
  products,
  shops,
  syncJobs,
  tokenVault,
  workerDedupeKeys,
} from "@frodo/db";
import type { FrodoDb } from "@frodo/db";
import {
  decryptSecret,
  extractOrderSearchPage,
  extractProductSearchPage,
  FRODO_VAULT_DECRYPT_FAILED,
  normalizeOrderRecord,
  normalizeProductRecord,
  redactForLog,
  ShopApiClient,
  TIKTOK_SHOP_ORDER_SEARCH_PATH,
  TIKTOK_SHOP_PRODUCT_SEARCH_PATH,
} from "@frodo/domain";
import type Redis from "ioredis";
import { createShopApiClientForWorker } from "./shop-discovery";

const PRODUCTS_FAIL = "tiktok_shop_products_sync_failed";
const ORDERS_FAIL = "tiktok_shop_orders_sync_failed";

export interface CommerceSyncDeps {
  loadEnv?: () => FrodoWorkerEnv;
  shopApiClient?: ShopApiClient;
}

export async function handleCommerceSync(
  db: FrodoDb,
  job: Extract<
    JobEnvelope,
    { type: "sync_shop_orders" } | { type: "sync_shop_products" }
  >,
  redis: Redis | null,
  deps: CommerceSyncDeps = {},
): Promise<void> {
  const env = (deps.loadEnv ?? loadWorkerEnv)();
  const master = env.TOKEN_ENCRYPTION_KEY?.trim();
  if (!master) {
    throw new Error("Worker missing TOKEN_ENCRYPTION_KEY");
  }

  const claim = await db
    .insert(workerDedupeKeys)
    .values({ dedupeKey: job.dedupeKey })
    .onConflictDoNothing({ target: workerDedupeKeys.dedupeKey })
    .returning({ id: workerDedupeKeys.id });

  if (claim.length === 0) {
    console.info(`Commerce dedupe skip dedupeKey=${job.dedupeKey}`);
    return;
  }

  const [shop] = await db
    .select({
      id: shops.id,
      shopCipher: shops.shopCipher,
      connectedAccountId: shops.connectedAccountId,
      workspaceId: shops.workspaceId,
      productSyncCursor: shops.productSyncCursor,
      orderSyncCursor: shops.orderSyncCursor,
    })
    .from(shops)
    .where(
      and(
        eq(shops.id, job.shopId),
        eq(shops.workspaceId, job.workspaceId),
        eq(shops.connectedAccountId, job.connectedAccountId),
      ),
    )
    .limit(1);

  if (!shop) {
    console.warn(
      `Commerce sync: shop not found or workspace/account mismatch ${JSON.stringify(redactForLog({ workspaceId: job.workspaceId, shopId: job.shopId }))}`,
    );
    return;
  }

  const kind = job.type === "sync_shop_orders" ? "orders" : "products";
  const syncType = kind === "orders" ? "orders" : "products";

  const [vault] = await db
    .select()
    .from(tokenVault)
    .where(eq(tokenVault.connectedAccountId, shop.connectedAccountId))
    .limit(1);

  if (!vault) {
    throw new Error("token_vault missing for commerce sync");
  }

  const [acct] = await db
    .select({ id: connectedAccounts.id })
    .from(connectedAccounts)
    .where(
      and(
        eq(connectedAccounts.id, shop.connectedAccountId),
        eq(connectedAccounts.workspaceId, job.workspaceId),
      ),
    )
    .limit(1);

  if (!acct) {
    throw new Error("connected_account mismatch for commerce sync");
  }

  let accessToken: string;
  try {
    accessToken = decryptSecret(vault.encryptedAccessToken, master);
  } catch (e) {
    console.warn(
      `${FRODO_VAULT_DECRYPT_FAILED} commerce ${JSON.stringify(redactForLog({ detail: e instanceof Error ? e.message : String(e) }))}`,
    );
    throw Object.assign(new Error(FRODO_VAULT_DECRYPT_FAILED), {
      code: FRODO_VAULT_DECRYPT_FAILED,
    });
  }

  const startedAt = new Date();
  const [syncRow] = await db
    .insert(syncJobs)
    .values({
      workspaceId: job.workspaceId,
      connectedAccountId: shop.connectedAccountId,
      platform: "shop",
      syncType,
      status: "running",
      startedAt,
    })
    .returning({ id: syncJobs.id });

  if (!syncRow) {
    throw new Error("sync job insert failed");
  }

  const client =
    deps.shopApiClient ?? createShopApiClientForWorker(env);

  const failPrefix = kind === "orders" ? ORDERS_FAIL : PRODUCTS_FAIL;

  try {
    if (job.type === "sync_shop_products") {
      const pageToken =
        job.cursor?.trim() ||
        shop.productSyncCursor?.trim() ||
        undefined;
      const body: Record<string, unknown> = {
        page_size: 20,
      };
      if (pageToken) {
        body.page_token = pageToken;
      }

      const { raw } = await client.postShopOpenApi(
        TIKTOK_SHOP_PRODUCT_SEARCH_PATH,
        accessToken,
        shop.shopCipher,
        body,
      );

      const page = extractProductSearchPage(raw);
      let n = 0;
      for (const item of page.items) {
        const row = normalizeProductRecord(item);
        if (!row) {
          continue;
        }
        await db
          .insert(products)
          .values({
            workspaceId: job.workspaceId,
            shopId: shop.id,
            platformProductId: row.platformProductId,
            title: row.title,
            status: row.status,
            mainImageUrl: row.mainImageUrl,
            priceAmount: row.priceAmount,
            currency: row.currency,
            inventoryTotal: row.inventoryTotal,
            skuCount: row.skuCount,
            detailJson: row.detailJson,
            apiSnapshotJson: item,
          })
          .onConflictDoUpdate({
            target: [products.shopId, products.platformProductId],
            set: {
              title: row.title,
              status: row.status,
              mainImageUrl: row.mainImageUrl,
              priceAmount: row.priceAmount,
              currency: row.currency,
              inventoryTotal: row.inventoryTotal,
              skuCount: row.skuCount,
              detailJson: row.detailJson,
              apiSnapshotJson: item,
              updatedAt: new Date(),
            },
          });
        n += 1;
      }

      const completedAt = new Date();
      await db
        .update(shops)
        .set({
          productSyncCursor: page.nextCursor ?? null,
          lastProductSyncAt: completedAt,
          updatedAt: completedAt,
        })
        .where(eq(shops.id, shop.id));

      await db
        .update(syncJobs)
        .set({
          status: "completed",
          itemsSynced: n,
          completedAt,
          updatedAt: completedAt,
        })
        .where(eq(syncJobs.id, syncRow.id));

      await publishCommerceRedis(redis, job.workspaceId, {
        kind: "products",
        shopId: shop.id,
        status: "completed",
        itemsSynced: n,
      });
    } else {
      const nowSec = Math.floor(Date.now() / 1000);
      const createTimeLe = job.createTimeLe ?? nowSec;
      const createTimeGe =
        job.createTimeGe ?? createTimeLe - 90 * 24 * 3600;

      const body: Record<string, unknown> = {
        page_size: 20,
        create_time_ge: createTimeGe,
        create_time_le: createTimeLe,
      };
      const cursor =
        job.cursor?.trim() || shop.orderSyncCursor?.trim() || undefined;
      if (cursor) {
        body.cursor = cursor;
      }

      const { raw } = await client.postShopOpenApi(
        TIKTOK_SHOP_ORDER_SEARCH_PATH,
        accessToken,
        shop.shopCipher,
        body,
      );

      const page = extractOrderSearchPage(raw);
      let n = 0;
      for (const item of page.items) {
        const row = normalizeOrderRecord(item);
        if (!row) {
          continue;
        }
        await db
          .insert(orders)
          .values({
            workspaceId: job.workspaceId,
            shopId: shop.id,
            platformOrderId: row.platformOrderId,
            status: row.status,
            totalAmount: row.totalAmount,
            currency: row.currency,
            itemCount: row.itemCount,
            fulfillmentType: row.fulfillmentType,
            detailJson: row.detailJson,
            apiSnapshotJson: item,
          })
          .onConflictDoUpdate({
            target: [orders.shopId, orders.platformOrderId],
            set: {
              status: row.status,
              totalAmount: row.totalAmount,
              currency: row.currency,
              itemCount: row.itemCount,
              fulfillmentType: row.fulfillmentType,
              detailJson: row.detailJson,
              apiSnapshotJson: item,
              updatedAt: new Date(),
            },
          });
        n += 1;
      }

      const completedAt = new Date();
      await db
        .update(shops)
        .set({
          orderSyncCursor: page.nextCursor ?? null,
          lastOrderSyncAt: completedAt,
          updatedAt: completedAt,
        })
        .where(eq(shops.id, shop.id));

      await db
        .update(syncJobs)
        .set({
          status: "completed",
          itemsSynced: n,
          completedAt,
          updatedAt: completedAt,
        })
        .where(eq(syncJobs.id, syncRow.id));

      await publishCommerceRedis(redis, job.workspaceId, {
        kind: "orders",
        shopId: shop.id,
        status: "completed",
        itemsSynced: n,
      });
    }
  } catch (e) {
    const completedAt = new Date();
    const inner = e instanceof Error ? e.message : String(e);
    await db
      .update(syncJobs)
      .set({
        status: "failed",
        errorMessage: `${failPrefix}: ${inner}`.slice(0, 1000),
        completedAt,
        updatedAt: completedAt,
      })
      .where(eq(syncJobs.id, syncRow.id));
    throw e;
  }
}

async function publishCommerceRedis(
  redis: Redis | null,
  workspaceId: string,
  payload: {
    kind: "products" | "orders";
    shopId: string;
    status: string;
    itemsSynced: number;
  },
): Promise<void> {
  if (!redis) {
    return;
  }
  try {
    await redis.publish(
      `frodo:workspace:${workspaceId}`,
      JSON.stringify({
        channel: "commerce_sync",
        payload,
      }),
    );
  } catch (pubErr) {
    console.warn(
      `redis commerce publish failed (non-fatal) ${JSON.stringify(redactForLog({ detail: pubErr instanceof Error ? pubErr.message : String(pubErr) }))}`,
    );
  }
}

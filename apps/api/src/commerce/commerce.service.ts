import {
  Injectable,
  NotFoundException,
  ServiceUnavailableException,
} from "@nestjs/common";
import { Inject } from "@nestjs/common";
import { and, desc, eq } from "drizzle-orm";
import { orders, products, shops, syncJobs } from "@frodo/db";
import type { FrodoDb } from "@frodo/db";
import { DRIZZLE } from "../database/database.module";
import { SqsService } from "../jobs/sqs.service";
import { buildCommerceDedupeKey } from "./commerce-dedupe";

@Injectable()
export class CommerceService {
  constructor(
    @Inject(DRIZZLE) private readonly db: FrodoDb,
    private readonly sqs: SqsService,
  ) {}

  async getShopSyncStatus(workspaceId: string, shopInternalId: string) {
    const shop = await this.getShopForWorkspace(workspaceId, shopInternalId);
    const base = and(
      eq(syncJobs.workspaceId, workspaceId),
      eq(syncJobs.connectedAccountId, shop.connectedAccountId),
    );

    const [latestProductJob] = await this.db
      .select({
        id: syncJobs.id,
        status: syncJobs.status,
        itemsSynced: syncJobs.itemsSynced,
        errorMessage: syncJobs.errorMessage,
        completedAt: syncJobs.completedAt,
        createdAt: syncJobs.createdAt,
      })
      .from(syncJobs)
      .where(and(base, eq(syncJobs.syncType, "products")))
      .orderBy(desc(syncJobs.createdAt))
      .limit(1);

    const [latestOrderJob] = await this.db
      .select({
        id: syncJobs.id,
        status: syncJobs.status,
        itemsSynced: syncJobs.itemsSynced,
        errorMessage: syncJobs.errorMessage,
        completedAt: syncJobs.completedAt,
        createdAt: syncJobs.createdAt,
      })
      .from(syncJobs)
      .where(and(base, eq(syncJobs.syncType, "orders")))
      .orderBy(desc(syncJobs.createdAt))
      .limit(1);

    return {
      shopId: shopInternalId,
      shopName: shop.shopName,
      latestProductSync: latestProductJob ?? null,
      latestOrderSync: latestOrderJob ?? null,
    };
  }

  async getShopForWorkspace(workspaceId: string, shopId: string) {
    const [row] = await this.db
      .select({
        id: shops.id,
        workspaceId: shops.workspaceId,
        connectedAccountId: shops.connectedAccountId,
        shopIdStr: shops.shopId,
        shopName: shops.shopName,
        region: shops.region,
        lastProductSyncAt: shops.lastProductSyncAt,
        lastOrderSyncAt: shops.lastOrderSyncAt,
        productSyncCursor: shops.productSyncCursor,
        orderSyncCursor: shops.orderSyncCursor,
      })
      .from(shops)
      .where(and(eq(shops.id, shopId), eq(shops.workspaceId, workspaceId)))
      .limit(1);

    if (!row) {
      throw new NotFoundException("Shop not found in this workspace");
    }
    return row;
  }

  async listProducts(workspaceId: string, shopInternalId: string) {
    await this.getShopForWorkspace(workspaceId, shopInternalId);
    const rows = await this.db
      .select({
        id: products.id,
        platformProductId: products.platformProductId,
        title: products.title,
        status: products.status,
        priceAmount: products.priceAmount,
        currency: products.currency,
        inventoryTotal: products.inventoryTotal,
        skuCount: products.skuCount,
        mainImageUrl: products.mainImageUrl,
        apiSnapshotJson: products.apiSnapshotJson,
        updatedAt: products.updatedAt,
      })
      .from(products)
      .where(
        and(
          eq(products.workspaceId, workspaceId),
          eq(products.shopId, shopInternalId),
        ),
      )
      .orderBy(desc(products.updatedAt))
      .limit(500);

    return rows.map(({ apiSnapshotJson, ...rest }) => ({
      ...rest,
      hasApiSnapshot: apiSnapshotJson != null,
    }));
  }

  async listOrders(workspaceId: string, shopInternalId: string) {
    await this.getShopForWorkspace(workspaceId, shopInternalId);
    const rows = await this.db
      .select({
        id: orders.id,
        platformOrderId: orders.platformOrderId,
        status: orders.status,
        totalAmount: orders.totalAmount,
        currency: orders.currency,
        itemCount: orders.itemCount,
        fulfillmentType: orders.fulfillmentType,
        apiSnapshotJson: orders.apiSnapshotJson,
        updatedAt: orders.updatedAt,
      })
      .from(orders)
      .where(
        and(
          eq(orders.workspaceId, workspaceId),
          eq(orders.shopId, shopInternalId),
        ),
      )
      .orderBy(desc(orders.updatedAt))
      .limit(500);

    return rows.map(({ apiSnapshotJson, ...rest }) => ({
      ...rest,
      hasApiSnapshot: apiSnapshotJson != null,
    }));
  }

  async enqueueSyncProducts(workspaceId: string, shopInternalId: string) {
    const shop = await this.getShopForWorkspace(workspaceId, shopInternalId);
    const dedupeKey = buildCommerceDedupeKey(
      workspaceId,
      shopInternalId,
      "products",
    );
    try {
      await this.sqs.sendJob({
        type: "sync_shop_products",
        workspaceId,
        shopId: shopInternalId,
        connectedAccountId: shop.connectedAccountId,
        dedupeKey,
      });
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      throw new ServiceUnavailableException(
        msg.includes("sqs") || msg.includes("SQS")
          ? "sqs_enqueue_failed"
          : "enqueue_failed",
      );
    }
    return {
      ok: true,
      enqueued: "sync_shop_products" as const,
      dedupeKey,
      shopId: shopInternalId,
    };
  }

  async enqueueSyncOrders(workspaceId: string, shopInternalId: string) {
    const shop = await this.getShopForWorkspace(workspaceId, shopInternalId);
    const dedupeKey = buildCommerceDedupeKey(
      workspaceId,
      shopInternalId,
      "orders",
    );
    try {
      await this.sqs.sendJob({
        type: "sync_shop_orders",
        workspaceId,
        shopId: shopInternalId,
        connectedAccountId: shop.connectedAccountId,
        dedupeKey,
      });
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      throw new ServiceUnavailableException(
        msg.includes("sqs") || msg.includes("SQS")
          ? "sqs_enqueue_failed"
          : "enqueue_failed",
      );
    }
    return {
      ok: true,
      enqueued: "sync_shop_orders" as const,
      dedupeKey,
      shopId: shopInternalId,
    };
  }
}

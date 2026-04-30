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
import type { ShopApiClient } from "@frodo/domain";
import {
  encryptSecret,
  TikTokShopApiError,
  TIKTOK_SHOP_ORDER_SEARCH_PATH,
} from "@frodo/domain";
import { afterEach, describe, expect, it, vi } from "vitest";
import { handleCommerceSync } from "./commerce";

const TOKEN_MASTER = "token-encryption-master-key-32chars-min";
const WS_ID = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee";
const CA_ID = "11111111-1111-4111-8111-111111111111";
const SHOP_INTERNAL_ID = "22222222-2222-4222-8222-222222222222";

function stubWorkerEnv() {
  return {
    APP_ENV: "development" as const,
    DATABASE_URL: "postgresql://localhost/x",
    AWS_REGION: "us-east-1",
    SQS_QUEUE_URL: "https://sqs/x",
    TOKEN_ENCRYPTION_KEY: TOKEN_MASTER,
    TIKTOK_SHOP_APP_KEY: "k",
    TIKTOK_SHOP_APP_SECRET: "secretsecretsecretsecret",
    TIKTOK_OPEN_API_BASE: "https://open-api.test",
  };
}

describe("handleCommerceSync products", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("dedupe skip leaves client uncalled", async () => {
    const post = vi.fn();
    const mockDb = {
      insert: vi.fn((table: unknown) => ({
        values: vi.fn(() => {
          if (table === workerDedupeKeys) {
            return {
              onConflictDoNothing: vi.fn(() => ({
                returning: vi.fn(() => Promise.resolve([])),
              })),
            };
          }
          throw new Error("unexpected insert");
        }),
      })),
    } as never;

    const job = {
      type: "sync_shop_products" as const,
      workspaceId: WS_ID,
      shopId: SHOP_INTERNAL_ID,
      connectedAccountId: CA_ID,
      dedupeKey: "commerce:products:test",
    };

    await handleCommerceSync(mockDb, job, null, {
      loadEnv: () => stubWorkerEnv() as never,
      shopApiClient: { postShopOpenApi: post } as unknown as ShopApiClient,
    });

    expect(post).not.toHaveBeenCalled();
  });

  it("upserts products from TikTok search response", async () => {
    const enc = encryptSecret("tok", TOKEN_MASTER);
    const productUpserts: unknown[] = [];

    let dedupeRound = 0;
    const mockDb = {
      insert: vi.fn((table: unknown) => ({
        values: vi.fn((vals: unknown) => {
          if (table === workerDedupeKeys) {
            return {
              onConflictDoNothing: vi.fn(() => ({
                returning: vi.fn(() => {
                  dedupeRound += 1;
                  return Promise.resolve(dedupeRound === 1 ? [{ id: "d" }] : []);
                }),
              })),
            };
          }
          if (table === syncJobs) {
            return {
              returning: vi.fn(() =>
                Promise.resolve([{ id: "job-row-1" }]),
              ),
            };
          }
          if (table === products) {
            productUpserts.push(vals);
            return {
              onConflictDoUpdate: vi.fn(() => Promise.resolve()),
            };
          }
          throw new Error(`unexpected insert ${String(table)}`);
        }),
      })),
      select: vi.fn(() => ({
        from: vi.fn((table: unknown) => ({
          where: vi.fn(() => ({
            limit: vi.fn(() => {
              if (table === shops) {
                return Promise.resolve([
                  {
                    id: SHOP_INTERNAL_ID,
                    shopCipher: "cipher",
                    connectedAccountId: CA_ID,
                    workspaceId: WS_ID,
                    productSyncCursor: null,
                    orderSyncCursor: null,
                  },
                ]);
              }
              if (table === tokenVault) {
                return Promise.resolve([
                  {
                    encryptedAccessToken: enc,
                    connectedAccountId: CA_ID,
                  },
                ]);
              }
              if (table === connectedAccounts) {
                return Promise.resolve([{ id: CA_ID }]);
              }
              return Promise.resolve([]);
            }),
          })),
        })),
      })),
      update: vi.fn(() => ({
        set: vi.fn(() => ({
          where: vi.fn(() => Promise.resolve()),
        })),
      })),
    } as never;

    const postShopOpenApi = vi.fn().mockResolvedValue({
      raw: {
        code: 0,
        data: {
          products: [
            { id: "tp1", product_name: "One", status: "live" },
          ],
        },
      },
    });

    const job: Extract<JobEnvelope, { type: "sync_shop_products" }> = {
      type: "sync_shop_products",
      workspaceId: WS_ID,
      shopId: SHOP_INTERNAL_ID,
      connectedAccountId: CA_ID,
      dedupeKey: "commerce:products:once",
    };

    await handleCommerceSync(mockDb, job, null, {
      loadEnv: () => stubWorkerEnv() as never,
      shopApiClient: {
        postShopOpenApi,
      } as unknown as ShopApiClient,
    });

    expect(postShopOpenApi).toHaveBeenCalled();
    expect(productUpserts.length).toBe(1);
    expect((productUpserts[0] as { platformProductId: string }).platformProductId).toBe(
      "tp1",
    );
  });
});

const ORDERS_FAIL_PREFIX = "tiktok_shop_orders_sync_failed";

describe("handleCommerceSync orders", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  const ACCESS_PLAINTEXT = "plain-tts-token-for-commerce-test";

  function createOrdersMockDb(
    encryptedToken: string,
    orderUpserts: unknown[],
    syncJobSets: unknown[],
  ) {
    let dedupeRound = 0;
    return {
      insert: vi.fn((table: unknown) => ({
        values: vi.fn((vals: unknown) => {
          if (table === workerDedupeKeys) {
            return {
              onConflictDoNothing: vi.fn(() => ({
                returning: vi.fn(() => {
                  dedupeRound += 1;
                  return Promise.resolve(
                    dedupeRound === 1 ? [{ id: "d" }] : [],
                  );
                }),
              })),
            };
          }
          if (table === syncJobs) {
            return {
              returning: vi.fn(() =>
                Promise.resolve([{ id: "job-row-orders-1" }]),
              ),
            };
          }
          if (table === orders) {
            orderUpserts.push(vals);
            return {
              onConflictDoUpdate: vi.fn(() => Promise.resolve()),
            };
          }
          throw new Error(`unexpected insert ${String(table)}`);
        }),
      })),
      select: vi.fn(() => ({
        from: vi.fn((table: unknown) => ({
          where: vi.fn(() => ({
            limit: vi.fn(() => {
              if (table === shops) {
                return Promise.resolve([
                  {
                    id: SHOP_INTERNAL_ID,
                    shopCipher: "cipher",
                    connectedAccountId: CA_ID,
                    workspaceId: WS_ID,
                    productSyncCursor: null,
                    orderSyncCursor: null,
                  },
                ]);
              }
              if (table === tokenVault) {
                return Promise.resolve([
                  {
                    encryptedAccessToken: encryptedToken,
                    connectedAccountId: CA_ID,
                  },
                ]);
              }
              if (table === connectedAccounts) {
                return Promise.resolve([{ id: CA_ID }]);
              }
              return Promise.resolve([]);
            }),
          })),
        })),
      })),
      update: vi.fn((table: unknown) => ({
        set: vi.fn((vals: unknown) => ({
          where: vi.fn(() => {
            if (table === syncJobs) {
              syncJobSets.push(vals);
            }
            return Promise.resolve();
          }),
        })),
      })),
    } as never;
  }

  it("upserts orders, passes window to ShopApiClient, completes sync_jobs", async () => {
    const enc = encryptSecret(ACCESS_PLAINTEXT, TOKEN_MASTER);
    const orderUpserts: unknown[] = [];
    const syncJobSets: unknown[] = [];
    const mockDb = createOrdersMockDb(enc, orderUpserts, syncJobSets);

    const rawOrder = {
      order_id: "tiktok-order-1",
      order_status: "AWAITING_SHIPMENT",
      payment: { total_amount: "44.00", currency: "GBP" },
      line_items: [{}, {}],
    };

    const postShopOpenApi = vi.fn().mockResolvedValue({
      raw: {
        code: 0,
        data: {
          order_list: [rawOrder],
        },
      },
    });

    const createTimeGe = 1_700_000_000;
    const createTimeLe = 1_700_086_400;

    const job: Extract<JobEnvelope, { type: "sync_shop_orders" }> = {
      type: "sync_shop_orders",
      workspaceId: WS_ID,
      shopId: SHOP_INTERNAL_ID,
      connectedAccountId: CA_ID,
      dedupeKey: "commerce:orders:once",
      createTimeGe,
      createTimeLe,
    };

    await handleCommerceSync(mockDb, job, null, {
      loadEnv: () => stubWorkerEnv() as never,
      shopApiClient: {
        postShopOpenApi,
      } as unknown as ShopApiClient,
    });

    expect(postShopOpenApi).toHaveBeenCalledTimes(1);
    expect(postShopOpenApi).toHaveBeenCalledWith(
      TIKTOK_SHOP_ORDER_SEARCH_PATH,
      ACCESS_PLAINTEXT,
      "cipher",
      expect.objectContaining({
        page_size: 20,
        create_time_ge: createTimeGe,
        create_time_le: createTimeLe,
      }),
    );

    expect(orderUpserts).toHaveLength(1);
    const inserted = orderUpserts[0] as {
      platformOrderId: string;
      apiSnapshotJson: unknown;
      workspaceId: string;
      shopId: string;
    };
    expect(inserted.platformOrderId).toBe("tiktok-order-1");
    expect(inserted.workspaceId).toBe(WS_ID);
    expect(inserted.shopId).toBe(SHOP_INTERNAL_ID);
    expect(inserted.apiSnapshotJson).toEqual(rawOrder);

    const completed = syncJobSets.find(
      (p) => (p as { status?: string }).status === "completed",
    ) as { status: string; itemsSynced: number } | undefined;
    expect(completed?.status).toBe("completed");
    expect(completed?.itemsSynced).toBe(1);
  });

  it("passes cursor from job when set", async () => {
    const enc = encryptSecret(ACCESS_PLAINTEXT, TOKEN_MASTER);
    const postShopOpenApi = vi.fn().mockResolvedValue({
      raw: { code: 0, data: { order_list: [] } },
    });

    const job: Extract<JobEnvelope, { type: "sync_shop_orders" }> = {
      type: "sync_shop_orders",
      workspaceId: WS_ID,
      shopId: SHOP_INTERNAL_ID,
      connectedAccountId: CA_ID,
      dedupeKey: "commerce:orders:cursor",
      cursor: "  page-cursor-99  ",
      createTimeGe: 100,
      createTimeLe: 200,
    };

    await handleCommerceSync(
      createOrdersMockDb(enc, [], []),
      job,
      null,
      {
        loadEnv: () => stubWorkerEnv() as never,
        shopApiClient: { postShopOpenApi } as unknown as ShopApiClient,
      },
    );

    expect(postShopOpenApi).toHaveBeenCalledWith(
      TIKTOK_SHOP_ORDER_SEARCH_PATH,
      ACCESS_PLAINTEXT,
      "cipher",
      expect.objectContaining({
        cursor: "page-cursor-99",
        create_time_ge: 100,
        create_time_le: 200,
      }),
    );
  });

  it("completes with itemsSynced 0 when order list empty", async () => {
    const enc = encryptSecret(ACCESS_PLAINTEXT, TOKEN_MASTER);
    const syncJobSets: unknown[] = [];
    const mockDb = createOrdersMockDb(enc, [], syncJobSets);

    const postShopOpenApi = vi.fn().mockResolvedValue({
      raw: {
        code: 0,
        data: { order_list: [] },
      },
    });

    const job: Extract<JobEnvelope, { type: "sync_shop_orders" }> = {
      type: "sync_shop_orders",
      workspaceId: WS_ID,
      shopId: SHOP_INTERNAL_ID,
      connectedAccountId: CA_ID,
      dedupeKey: "commerce:orders:empty",
      createTimeGe: 1,
      createTimeLe: 2,
    };

    await handleCommerceSync(mockDb, job, null, {
      loadEnv: () => stubWorkerEnv() as never,
      shopApiClient: {
        postShopOpenApi,
      } as unknown as ShopApiClient,
    });

    const completed = syncJobSets.find(
      (p) => (p as { status?: string }).status === "completed",
    ) as { itemsSynced: number } | undefined;
    expect(completed?.itemsSynced).toBe(0);
  });

  it("records failure prefix and rethrows on TikTok Shop API error", async () => {
    const enc = encryptSecret(ACCESS_PLAINTEXT, TOKEN_MASTER);
    const syncJobSets: unknown[] = [];
    const mockDb = createOrdersMockDb(enc, [], syncJobSets);

    const postShopOpenApi = vi.fn().mockRejectedValue(
      new TikTokShopApiError("rate_limited", { tiktokCode: 980_010 }),
    );

    const job: Extract<JobEnvelope, { type: "sync_shop_orders" }> = {
      type: "sync_shop_orders",
      workspaceId: WS_ID,
      shopId: SHOP_INTERNAL_ID,
      connectedAccountId: CA_ID,
      dedupeKey: "commerce:orders:fail",
      createTimeGe: 1,
      createTimeLe: 2,
    };

    await expect(
      handleCommerceSync(mockDb, job, null, {
        loadEnv: () => stubWorkerEnv() as never,
        shopApiClient: {
          postShopOpenApi,
        } as unknown as ShopApiClient,
      }),
    ).rejects.toThrow(TikTokShopApiError);

    const failed = syncJobSets.find(
      (p) => (p as { status?: string }).status === "failed",
    ) as { errorMessage?: string } | undefined;
    expect(failed?.errorMessage?.startsWith(ORDERS_FAIL_PREFIX)).toBe(true);
    expect(failed?.errorMessage).toContain("rate_limited");
  });

  it("does not log plaintext access token or signed URL patterns", async () => {
    const enc = encryptSecret(ACCESS_PLAINTEXT, TOKEN_MASTER);
    const logChunks: string[] = [];
    for (const level of ["info", "warn", "log", "error", "debug"] as const) {
      vi.spyOn(console, level).mockImplementation((...args: unknown[]) => {
        logChunks.push(
          args
            .map((a) =>
              typeof a === "string" ? a : JSON.stringify(a),
            )
            .join(" "),
        );
      });
    }

    const postShopOpenApi = vi.fn().mockResolvedValue({
      raw: { code: 0, data: { order_list: [] } },
    });

    const job: Extract<JobEnvelope, { type: "sync_shop_orders" }> = {
      type: "sync_shop_orders",
      workspaceId: WS_ID,
      shopId: SHOP_INTERNAL_ID,
      connectedAccountId: CA_ID,
      dedupeKey: "commerce:orders:logcheck",
      createTimeGe: 1,
      createTimeLe: 2,
    };

    await handleCommerceSync(
      createOrdersMockDb(enc, [], []),
      job,
      null,
      {
        loadEnv: () => stubWorkerEnv() as never,
        shopApiClient: { postShopOpenApi } as unknown as ShopApiClient,
      },
    );

    const combined = logChunks.join("\n");
    expect(combined).not.toContain(ACCESS_PLAINTEXT);
    expect(combined).not.toMatch(/access_token=/i);
    expect(combined).not.toMatch(/x-tts-access-token/i);
  });
});

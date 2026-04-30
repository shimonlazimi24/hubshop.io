import type { FrodoWorkerEnv } from "@frodo/config";
import type { JobEnvelope } from "@frodo/contracts";
import {
  connectedAccounts,
  shops,
  syncJobs,
  tokenVault,
  workerDedupeKeys,
} from "@frodo/db";
import type { FrodoDb } from "@frodo/db";
import {
  decryptSecret,
  encryptSecret,
  FRODO_TIKTOK_SHOP_DISCOVERY_FAILED,
  FRODO_VAULT_DECRYPT_FAILED,
} from "@frodo/domain";
import type { ShopApiClient } from "@frodo/domain";
import { afterEach, describe, expect, it, vi } from "vitest";
import { handleShopDiscovery } from "./shop-discovery";

const TOKEN_MASTER = "token-encryption-master-key-32chars-min";
const WS_ID = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee";
const CA_ID = "11111111-1111-4111-8111-111111111111";

function stubWorkerEnv(): FrodoWorkerEnv {
  return {
    APP_ENV: "development",
    DATABASE_URL: "postgresql://localhost/frodo_test",
    AWS_REGION: "us-east-1",
    SQS_QUEUE_URL: "https://sqs.us-east-1.amazonaws.com/123/q",
    TOKEN_ENCRYPTION_KEY: TOKEN_MASTER,
    TIKTOK_SHOP_APP_KEY: "appkey",
    TIKTOK_SHOP_APP_SECRET: "secretsecretsecretsecret",
    TIKTOK_OPEN_API_BASE: "https://open-api.test",
  } as FrodoWorkerEnv;
}

function baseJob(): Extract<
  JobEnvelope,
  { type: "shop_discovery_after_connect" }
> {
  return {
    type: "shop_discovery_after_connect",
    workspaceId: WS_ID,
    connectedAccountId: CA_ID,
    dedupeKey: `shop_discovery:${CA_ID}`,
  };
}

describe("handleShopDiscovery", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("dedupe prevents duplicate processing", async () => {
    let dedupeRound = 0;
    const getAuthorizedShops = vi.fn().mockResolvedValue({
      raw: { code: 0, data: { shops: [] } },
      shops: [],
    });

    const mockDb = {
      insert: vi.fn((table: unknown) => ({
        values: vi.fn(() => {
          if (table === workerDedupeKeys) {
            return {
              onConflictDoNothing: vi.fn(() => ({
                returning: vi.fn(() => {
                  dedupeRound += 1;
                  return Promise.resolve(dedupeRound === 1 ? [{ id: "dk1" }] : []);
                }),
              })),
            };
          }
          if (table === syncJobs) {
            return Promise.resolve();
          }
          return {
            onConflictDoUpdate: vi.fn(() => Promise.resolve()),
          };
        }),
      })),
      select: vi.fn(() => ({
        from: vi.fn((table: unknown) => ({
          where: vi.fn(() => ({
            limit: vi.fn(() => {
              if (table === connectedAccounts) {
                return Promise.resolve([
                  { id: CA_ID, workspaceId: WS_ID, metadataJson: {} },
                ]);
              }
              if (table === tokenVault) {
                return Promise.resolve([
                  {
                    connectedAccountId: CA_ID,
                    encryptedAccessToken: encryptSecret("tok", TOKEN_MASTER),
                  },
                ]);
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
    } as unknown as FrodoDb;

    await handleShopDiscovery(mockDb, baseJob(), null, {
      shopApiClient: { getAuthorizedShops } as unknown as ShopApiClient,
      loadEnv: stubWorkerEnv,
    });
    expect(getAuthorizedShops).toHaveBeenCalledTimes(1);

    await handleShopDiscovery(mockDb, baseJob(), null, {
      shopApiClient: { getAuthorizedShops } as unknown as ShopApiClient,
      loadEnv: stubWorkerEnv,
    });
    expect(getAuthorizedShops).toHaveBeenCalledTimes(1);
  });

  it("decrypts vault token, upserts shops, stores snapshot, completes sync_jobs", async () => {
    const shopSnap = {
      id: "sid-99",
      cipher: "cipher-99",
      name: "Test Shop",
      region: "GB",
    };
    const getAuthorizedShops = vi.fn().mockResolvedValue({
      raw: { code: 0, data: { shops: [shopSnap] } },
      shops: [
        {
          shopId: "sid-99",
          shopCipher: "cipher-99",
          shopCode: "",
          shopName: "Test Shop",
          region: "GB",
          raw: shopSnap as Record<string, unknown>,
        },
      ],
    });
    const decryptSpy = vi.fn((cipher: string, master: string) =>
      decryptSecret(cipher, master),
    );

    const shopUpserts: unknown[] = [];
    const syncInserts: unknown[] = [];

    const enc = encryptSecret("real-tiktok-access", TOKEN_MASTER);

    const mockDb = {
      insert: vi.fn((table: unknown) => ({
        values: vi.fn((vals: unknown) => {
          if (table === workerDedupeKeys) {
            return {
              onConflictDoNothing: vi.fn(() => ({
                returning: vi.fn(() => Promise.resolve([{ id: "d1" }])),
              })),
            };
          }
          if (table === shops) {
            shopUpserts.push(vals);
            return {
              onConflictDoUpdate: vi.fn(() => Promise.resolve()),
            };
          }
          if (table === syncJobs) {
            syncInserts.push(vals);
            return Promise.resolve();
          }
          throw new Error("unexpected insert table");
        }),
      })),
      select: vi.fn(() => ({
        from: vi.fn((table: unknown) => ({
          where: vi.fn(() => ({
            limit: vi.fn(() => {
              if (table === connectedAccounts) {
                return Promise.resolve([
                  {
                    id: CA_ID,
                    workspaceId: WS_ID,
                    metadataJson: {},
                  },
                ]);
              }
              if (table === tokenVault) {
                return Promise.resolve([
                  {
                    connectedAccountId: CA_ID,
                    encryptedAccessToken: enc,
                  },
                ]);
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
    } as unknown as FrodoDb;

    await handleShopDiscovery(mockDb, baseJob(), null, {
      shopApiClient: { getAuthorizedShops } as unknown as ShopApiClient,
      loadEnv: stubWorkerEnv,
      decryptAccessToken: decryptSpy,
    });

    expect(decryptSpy).toHaveBeenCalledWith(enc, TOKEN_MASTER);
    expect(shopUpserts).toHaveLength(1);
    expect((shopUpserts[0] as { discoverySnapshotJson: unknown }).discoverySnapshotJson).toEqual(
      shopSnap,
    );
    const completed = syncInserts.find(
      (row) => (row as { status: string }).status === "completed",
    );
    expect(completed).toMatchObject({
      syncType: "shop_discovery",
      status: "completed",
      itemsSynced: 1,
    });
  });

  it("Redis publish failure does not fail the handler", async () => {
    const redis = {
      publish: vi.fn().mockRejectedValue(new Error("redis down")),
    };

    const getAuthorizedShops = vi.fn().mockResolvedValue({
      raw: { code: 0, data: { shops: [] } },
      shops: [],
    });

    const mockDb = {
      insert: vi.fn((table: unknown) => ({
        values: vi.fn(() => {
          if (table === workerDedupeKeys) {
            return {
              onConflictDoNothing: vi.fn(() => ({
                returning: vi.fn(() => Promise.resolve([{ id: "d1" }])),
              })),
            };
          }
          if (table === syncJobs) {
            return Promise.resolve();
          }
          return {
            onConflictDoUpdate: vi.fn(() => Promise.resolve()),
          };
        }),
      })),
      select: vi.fn(() => ({
        from: vi.fn((table: unknown) => ({
          where: vi.fn(() => ({
            limit: vi.fn(() => {
              if (table === connectedAccounts) {
                return Promise.resolve([
                  { id: CA_ID, workspaceId: WS_ID, metadataJson: {} },
                ]);
              }
              if (table === tokenVault) {
                return Promise.resolve([
                  {
                    connectedAccountId: CA_ID,
                    encryptedAccessToken: encryptSecret("tok", TOKEN_MASTER),
                  },
                ]);
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
    } as unknown as FrodoDb;

    await expect(
      handleShopDiscovery(mockDb, baseJob(), redis as never, {
        shopApiClient: { getAuthorizedShops } as unknown as ShopApiClient,
        loadEnv: stubWorkerEnv,
      }),
    ).resolves.toBeUndefined();

    expect(redis.publish).toHaveBeenCalled();
  });

  it("records tiktok_shop_discovery_failed on API error", async () => {
    const getAuthorizedShops = vi
      .fn()
      .mockRejectedValue(new Error("authorized_shops_http_500"));

    const syncInserts: unknown[] = [];

    const mockDb = {
      insert: vi.fn((table: unknown) => ({
        values: vi.fn((vals: unknown) => {
          if (table === workerDedupeKeys) {
            return {
              onConflictDoNothing: vi.fn(() => ({
                returning: vi.fn(() => Promise.resolve([{ id: "d1" }])),
              })),
            };
          }
          if (table === syncJobs) {
            syncInserts.push(vals);
            return Promise.resolve();
          }
          return {
            onConflictDoUpdate: vi.fn(() => Promise.resolve()),
          };
        }),
      })),
      select: vi.fn(() => ({
        from: vi.fn((table: unknown) => ({
          where: vi.fn(() => ({
            limit: vi.fn(() => {
              if (table === connectedAccounts) {
                return Promise.resolve([
                  { id: CA_ID, workspaceId: WS_ID, metadataJson: {} },
                ]);
              }
              if (table === tokenVault) {
                return Promise.resolve([
                  {
                    connectedAccountId: CA_ID,
                    encryptedAccessToken: encryptSecret("tok", TOKEN_MASTER),
                  },
                ]);
              }
              return Promise.resolve([]);
            }),
          })),
        })),
      })),
      update: vi.fn(),
    } as unknown as FrodoDb;

    await expect(
      handleShopDiscovery(mockDb, baseJob(), null, {
        shopApiClient: { getAuthorizedShops } as unknown as ShopApiClient,
        loadEnv: stubWorkerEnv,
      }),
    ).rejects.toThrow();

    const failed = syncInserts.find(
      (row) => (row as { status: string }).status === "failed",
    );
    expect((failed as { errorMessage: string }).errorMessage).toContain(
      FRODO_TIKTOK_SHOP_DISCOVERY_FAILED,
    );
  });

  it("throws vault_decrypt_failed when decrypt fails", async () => {
    const getAuthorizedShops = vi.fn();
    const mockDb = {
      insert: vi.fn((table: unknown) => ({
        values: vi.fn(() => {
          if (table === workerDedupeKeys) {
            return {
              onConflictDoNothing: vi.fn(() => ({
                returning: vi.fn(() => Promise.resolve([{ id: "d1" }])),
              })),
            };
          }
          throw new Error("unexpected");
        }),
      })),
      select: vi.fn(() => ({
        from: vi.fn((table: unknown) => ({
          where: vi.fn(() => ({
            limit: vi.fn(() => {
              if (table === connectedAccounts) {
                return Promise.resolve([
                  { id: CA_ID, workspaceId: WS_ID, metadataJson: {} },
                ]);
              }
              if (table === tokenVault) {
                return Promise.resolve([
                  {
                    connectedAccountId: CA_ID,
                    encryptedAccessToken: "not-valid-cipher",
                  },
                ]);
              }
              return Promise.resolve([]);
            }),
          })),
        })),
      })),
    } as unknown as FrodoDb;

    await expect(
      handleShopDiscovery(mockDb, baseJob(), null, {
        shopApiClient: {
          getAuthorizedShops,
        } as unknown as ShopApiClient,
        loadEnv: stubWorkerEnv,
      }),
    ).rejects.toThrow(FRODO_VAULT_DECRYPT_FAILED);

    expect(getAuthorizedShops).not.toHaveBeenCalled();
  });
});

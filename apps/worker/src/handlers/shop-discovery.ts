import { and, eq } from "drizzle-orm";
import type { FrodoWorkerEnv } from "@frodo/config";
import { loadWorkerEnv } from "@frodo/config";
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
  FRODO_TIKTOK_SHOP_DISCOVERY_FAILED,
  FRODO_VAULT_DECRYPT_FAILED,
  redactForLog,
  ShopApiClient,
} from "@frodo/domain";
import type Redis from "ioredis";

export interface ShopDiscoveryDeps {
  loadEnv?: () => FrodoWorkerEnv;
  /** Injected client for tests; defaults to env-built ShopApiClient. */
  shopApiClient?: ShopApiClient;
  decryptAccessToken?: (cipherText: string, masterKey: string) => string;
}

export function createShopApiClientForWorker(env: FrodoWorkerEnv): ShopApiClient {
  const appKey = env.TIKTOK_SHOP_APP_KEY?.trim() ?? "";
  const appSecret = env.TIKTOK_SHOP_APP_SECRET?.trim() ?? "";
  const openBase =
    env.TIKTOK_OPEN_API_BASE ?? "https://open-api.tiktokglobalshop.com";
  return new ShopApiClient({
    openApiBase: openBase,
    appKey,
    appSecret,
    logger: {
      debug: (msg, meta) =>
        console.info(`shop_api ${msg} ${JSON.stringify(redactForLog(meta ?? {}))}`),
    },
  });
}

export async function handleShopDiscovery(
  db: FrodoDb,
  job: Extract<JobEnvelope, { type: "shop_discovery_after_connect" }>,
  redis: Redis | null,
  deps: ShopDiscoveryDeps = {},
): Promise<void> {
  const env = (deps.loadEnv ?? loadWorkerEnv)();
  const master = env.TOKEN_ENCRYPTION_KEY?.trim();
  const appKey = env.TIKTOK_SHOP_APP_KEY?.trim();
  const appSecret = env.TIKTOK_SHOP_APP_SECRET?.trim();
  if (!master || !appKey || !appSecret) {
    throw new Error(
      "Worker missing TOKEN_ENCRYPTION_KEY or TIKTOK_SHOP_APP_KEY / TIKTOK_SHOP_APP_SECRET",
    );
  }

  const shopClient =
    deps.shopApiClient ?? createShopApiClientForWorker(env);

  const claim = await db
    .insert(workerDedupeKeys)
    .values({ dedupeKey: job.dedupeKey })
    .onConflictDoNothing({ target: workerDedupeKeys.dedupeKey })
    .returning({ id: workerDedupeKeys.id });

  if (claim.length === 0) {
    console.info(`Shop discovery dedupe skip ${job.dedupeKey}`);
    return;
  }

  const [acct] = await db
    .select()
    .from(connectedAccounts)
    .where(
      and(
        eq(connectedAccounts.id, job.connectedAccountId),
        eq(connectedAccounts.workspaceId, job.workspaceId),
      ),
    )
    .limit(1);

  if (!acct) {
    throw new Error("connected_account not found for shop discovery");
  }

  const [vault] = await db
    .select()
    .from(tokenVault)
    .where(eq(tokenVault.connectedAccountId, job.connectedAccountId))
    .limit(1);

  if (!vault) {
    throw new Error("token_vault missing for shop discovery");
  }

  const decrypt = deps.decryptAccessToken ?? decryptSecret;
  let accessToken: string;
  try {
    accessToken = decrypt(vault.encryptedAccessToken, master);
  } catch (e) {
    const detail = e instanceof Error ? e.message : String(e);
    console.warn(
      `${FRODO_VAULT_DECRYPT_FAILED} ${JSON.stringify(redactForLog({ detail }))}`,
    );
    const err = new Error(FRODO_VAULT_DECRYPT_FAILED);
    Object.assign(err, { code: FRODO_VAULT_DECRYPT_FAILED });
    throw err;
  }

  const startedAt = new Date();

  try {
    const { raw, shops: rows } =
      await shopClient.getAuthorizedShops(accessToken);

    console.info(
      `shop_discovery authorized_shops redacted=${JSON.stringify(redactForLog(raw))}`,
    );

    for (const s of rows) {
      await db
        .insert(shops)
        .values({
          workspaceId: job.workspaceId,
          connectedAccountId: job.connectedAccountId,
          shopId: s.shopId,
          shopCipher: s.shopCipher,
          shopName: s.shopName,
          region: s.region,
          discoverySnapshotJson: s.raw,
        })
        .onConflictDoUpdate({
          target: shops.shopId,
          set: {
            shopCipher: s.shopCipher,
            shopName: s.shopName,
            region: s.region,
            discoverySnapshotJson: s.raw,
            connectedAccountId: job.connectedAccountId,
            updatedAt: new Date(),
          },
        });
    }

    const completedAt = new Date();
    await db.insert(syncJobs).values({
      workspaceId: job.workspaceId,
      connectedAccountId: job.connectedAccountId,
      platform: "shop",
      syncType: "shop_discovery",
      status: "completed",
      itemsSynced: rows.length,
      startedAt,
      completedAt,
    });

    const prevMeta =
      (acct.metadataJson as Record<string, unknown> | null) ?? {};
    await db
      .update(connectedAccounts)
      .set({
        metadataJson: {
          ...prevMeta,
          last_shop_discovery_at: completedAt.toISOString(),
          last_discovery_shop_count: rows.length,
        },
        updatedAt: completedAt,
      })
      .where(eq(connectedAccounts.id, job.connectedAccountId));

    if (redis) {
      try {
        await redis.publish(
          `frodo:workspace:${job.workspaceId}`,
          JSON.stringify({
            channel: "shop_connect",
            payload: {
              status: "discovery_complete",
              shopCount: rows.length,
              connectedAccountId: job.connectedAccountId,
            },
          }),
        );
      } catch (pubErr) {
        console.warn(
          `redis publish failed (non-fatal) ${JSON.stringify(redactForLog({ detail: pubErr instanceof Error ? pubErr.message : String(pubErr) }))}`,
        );
      }
    }
  } catch (e) {
    const completedAt = new Date();
    const inner = e instanceof Error ? e.message : String(e);
    await db.insert(syncJobs).values({
      workspaceId: job.workspaceId,
      connectedAccountId: job.connectedAccountId,
      platform: "shop",
      syncType: "shop_discovery",
      status: "failed",
      errorMessage:
        `${FRODO_TIKTOK_SHOP_DISCOVERY_FAILED}: ${inner}`.slice(0, 1000),
      startedAt,
      completedAt,
    });
    throw e;
  }
}

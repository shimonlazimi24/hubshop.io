import type { JobEnvelope } from "@frodo/contracts";
import type { FrodoDb } from "@frodo/db";
import type Redis from "ioredis";
import { handleCommerceSync } from "./handlers/commerce";
import { handleTokenRefreshTick } from "./handlers/tokens";
import { handleWebhook } from "./handlers/webhook";
import { handleEmitRealtime } from "./handlers/realtime";
import { handleShopDiscovery } from "./handlers/shop-discovery";

export async function dispatch(
  db: FrodoDb,
  env: JobEnvelope,
  redis: Redis | null,
): Promise<void> {
  switch (env.type) {
    case "process_webhook_event":
      await handleWebhook(db, env);
      break;
    case "token_refresh_tick":
      await handleTokenRefreshTick(db);
      break;
    case "refresh_workspace_tokens":
      console.info(
        `refresh_workspace_tokens workspace=${env.workspaceId} account=${env.connectedAccountId}`,
      );
      break;
    case "sync_shop_orders":
    case "sync_shop_products":
      await handleCommerceSync(db, env, redis);
      break;
    case "emit_realtime_event":
      await handleEmitRealtime(redis, env);
      break;
    case "shop_discovery_after_connect":
      await handleShopDiscovery(db, env, redis);
      break;
    default: {
      const _exhaustive: never = env;
      return _exhaustive;
    }
  }
}

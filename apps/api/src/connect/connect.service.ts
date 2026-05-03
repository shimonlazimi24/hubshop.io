import {
  BadRequestException,
  Injectable,
  Logger,
  ServiceUnavailableException,
} from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { Inject } from "@nestjs/common";
import {
  connectedAccounts,
  tokenVault,
  shops,
  syncJobs,
} from "@frodo/db";
import type { FrodoDb } from "@frodo/db";
import {
  encryptSecret,
  exchangeShopAuthorizedCode,
  FRODO_SQS_ENQUEUE_FAILED,
  FRODO_TIKTOK_STATE_INVALID,
  FRODO_TIKTOK_TOKEN_EXCHANGE_FAILED,
  FRODO_TIKTOK_TOKEN_MISSING_SELLER_IDENTITY,
  redactForLog,
  signShopOAuthState,
  verifyShopOAuthState,
} from "@frodo/domain";
import { and, desc, eq } from "drizzle-orm";
import { DRIZZLE } from "../database/database.module";
import { SqsService } from "../jobs/sqs.service";

function isoFromExpireSeconds(sec?: number): string | undefined {
  if (sec === undefined || !Number.isFinite(sec) || sec <= 0) {
    return undefined;
  }
  return new Date(Date.now() + sec * 1000).toISOString();
}

export function shopDiscoveryDedupeKey(connectedAccountId: string): string {
  return `shop_discovery:${connectedAccountId}`;
}

@Injectable()
export class ConnectService {
  private readonly logger = new Logger(ConnectService.name);

  constructor(
    @Inject(DRIZZLE) private readonly db: FrodoDb,
    private readonly config: ConfigService,
    private readonly sqs: SqsService,
  ) {}

  private stateSecret(): string {
    return (
      this.config.get<string>("SHOP_OAUTH_STATE_SECRET") ??
      this.config.get<string>("JWT_SECRET") ??
      ""
    );
  }

  private requireShopConfig(): {
    appKey: string;
    appSecret: string;
    serviceId: string;
    redirectUri: string;
    authBase: string;
    tokenUrl: string;
  } {
    const appKey = this.config.get<string>("TIKTOK_SHOP_APP_KEY")?.trim();
    const appSecret = this.config.get<string>("TIKTOK_SHOP_APP_SECRET")?.trim();
    const serviceId = this.config.get<string>("TIKTOK_SHOP_SERVICE_ID")?.trim();
    const redirectUri = this.config.get<string>(
      "TIKTOK_SHOP_REDIRECT_URI",
    )?.trim();
    if (!appKey || !appSecret || !serviceId || !redirectUri) {
      throw new BadRequestException(
        "TikTok Shop OAuth is not configured (TIKTOK_SHOP_APP_KEY, TIKTOK_SHOP_APP_SECRET, TIKTOK_SHOP_SERVICE_ID, TIKTOK_SHOP_REDIRECT_URI)",
      );
    }
    if (serviceId.toLowerCase() === "svc") {
      throw new BadRequestException(
        "TIKTOK_SHOP_SERVICE_ID must be the real Service ID from TikTok Partner Center (Applications → your app). The value \"svc\" is invalid and TikTok will show \"This service does not exist\".",
      );
    }
    const authBase =
      this.config.get<string>("TIKTOK_SHOP_AUTH_BASE")?.trim() ??
      "https://services.tiktokshop.com/open/authorize";
    const tokenUrl =
      this.config.get<string>("TIKTOK_TOKEN_URL")?.trim() ??
      "https://auth.tiktok-shops.com/api/v2/token/get";
    return { appKey, appSecret, serviceId, redirectUri, authBase, tokenUrl };
  }

  /** Start OAuth: signed state + real Partner authorize URL. */
  buildShopAuthorizeForWorkspace(input: {
    workspaceId: string;
    userId: string;
  }): { authorize_url: string; state: string } {
    const secret = this.stateSecret();
    if (!secret) {
      throw new BadRequestException("JWT_SECRET or SHOP_OAUTH_STATE_SECRET required for OAuth state");
    }
    const cfg = this.requireShopConfig();
    const { token } = signShopOAuthState(
      { workspaceId: input.workspaceId, userId: input.userId },
      secret,
    );

    const redirect = encodeURIComponent(cfg.redirectUri);
    const authorize_url = `${cfg.authBase}?service_id=${encodeURIComponent(cfg.serviceId)}&state=${encodeURIComponent(token)}&redirect_uri=${redirect}`;

    return { authorize_url, state: token };
  }

  /** Exchange code, persist vault, enqueue discovery (rolls back account/vault if enqueue fails). */
  async completeShopOAuth(code: string, stateToken: string): Promise<void> {
    const secret = this.stateSecret();
    if (!secret) {
      throw new BadRequestException("OAuth state secret not configured");
    }
    const cfg = this.requireShopConfig();
    const master = this.config.get<string>("TOKEN_ENCRYPTION_KEY");
    if (!master?.trim()) {
      throw new ServiceUnavailableException(
        "TOKEN_ENCRYPTION_KEY is required to store Shop tokens",
      );
    }

    let payload;
    try {
      payload = verifyShopOAuthState(stateToken, secret);
    } catch {
      this.logger.debug(
        `OAuth state rejected ${JSON.stringify(redactForLog({ stateLen: stateToken.length }))}`,
      );
      throw new BadRequestException(FRODO_TIKTOK_STATE_INVALID);
    }

    let tokens;
    try {
      tokens = await exchangeShopAuthorizedCode({
        tokenUrl: cfg.tokenUrl,
        appKey: cfg.appKey,
        appSecret: cfg.appSecret,
        authCode: code,
      });
    } catch (e) {
      const msg = e instanceof Error ? e.message : "unknown";
      this.logger.warn(
        `Shop token exchange failed ${JSON.stringify(redactForLog({ detail: msg }))}`,
      );
      throw new BadRequestException(FRODO_TIKTOK_TOKEN_EXCHANGE_FAILED);
    }

    this.logger.log(
      `Shop token exchange ok ${JSON.stringify(redactForLog(tokens.raw))}`,
    );

    const sellerKey = tokens.sellerOpenId?.trim();

    if (!sellerKey) {
      this.logger.warn(
        `TikTok token payload missing seller identifier ${JSON.stringify(redactForLog(tokens.raw))}`,
      );
      throw new BadRequestException(
        FRODO_TIKTOK_TOKEN_MISSING_SELLER_IDENTITY,
      );
    }

    const platformAccountId = sellerKey;
    const metadataJson = {
      oauth_completed_at: new Date().toISOString(),
      token_exchange_request_id:
        typeof tokens.raw === "object" &&
        tokens.raw !== null &&
        "request_id" in tokens.raw
          ? String((tokens.raw as { request_id?: unknown }).request_id)
          : undefined,
    };

    const [upserted] = await this.db
      .insert(connectedAccounts)
      .values({
        workspaceId: payload.workspaceId,
        platform: "shop",
        platformAccountId,
        platformAccountName: platformAccountId,
        status: "active",
        metadataJson,
      })
      .onConflictDoUpdate({
        target: [
          connectedAccounts.workspaceId,
          connectedAccounts.platform,
          connectedAccounts.platformAccountId,
        ],
        set: {
          status: "active",
          metadataJson,
          updatedAt: new Date(),
        },
      })
      .returning({ id: connectedAccounts.id });

    if (!upserted?.id) {
      throw new ServiceUnavailableException("connected_account_upsert_failed");
    }

    const connectedAccountId = upserted.id;

    const encAccess = encryptSecret(tokens.accessToken, master);
    const encRefresh = tokens.refreshToken
      ? encryptSecret(tokens.refreshToken, master)
      : null;

    await this.db
      .insert(tokenVault)
      .values({
        connectedAccountId,
        encryptedAccessToken: encAccess,
        encryptedRefreshToken: encRefresh,
        accessTokenExpiresAt: isoFromExpireSeconds(
          tokens.accessTokenExpireInSec,
        ),
        refreshTokenExpiresAt: isoFromExpireSeconds(
          tokens.refreshTokenExpireInSec,
        ),
        scopes: tokens.scope ?? null,
      })
      .onConflictDoUpdate({
        target: tokenVault.connectedAccountId,
        set: {
          encryptedAccessToken: encAccess,
          encryptedRefreshToken: encRefresh,
          accessTokenExpiresAt: isoFromExpireSeconds(
            tokens.accessTokenExpireInSec,
          ),
          refreshTokenExpiresAt: isoFromExpireSeconds(
            tokens.refreshTokenExpireInSec,
          ),
          scopes: tokens.scope ?? null,
          updatedAt: new Date(),
        },
      });

    const dedupeKey = shopDiscoveryDedupeKey(connectedAccountId);

    try {
      await this.sqs.sendJob({
        type: "shop_discovery_after_connect",
        workspaceId: payload.workspaceId,
        connectedAccountId,
        dedupeKey,
      });
    } catch (e) {
      this.logger.error(
        `Enqueue shop_discovery failed for account=${connectedAccountId}, rolling back connected account ${JSON.stringify(redactForLog({ cause: e instanceof Error ? e.message : String(e) }))}`,
      );
      await this.db
        .delete(connectedAccounts)
        .where(eq(connectedAccounts.id, connectedAccountId));
      throw new ServiceUnavailableException(FRODO_SQS_ENQUEUE_FAILED);
    }
  }

  async listConnectedShops(workspaceId: string) {
    const accounts = await this.db
      .select({
        id: connectedAccounts.id,
        platformAccountId: connectedAccounts.platformAccountId,
        status: connectedAccounts.status,
        updatedAt: connectedAccounts.updatedAt,
        metadataJson: connectedAccounts.metadataJson,
      })
      .from(connectedAccounts)
      .where(
        and(
          eq(connectedAccounts.workspaceId, workspaceId),
          eq(connectedAccounts.platform, "shop"),
        ),
      );

    const shopRows = await this.db
      .select({
        id: shops.id,
        shopId: shops.shopId,
        shopName: shops.shopName,
        region: shops.region,
        connectedAccountId: shops.connectedAccountId,
        updatedAt: shops.updatedAt,
      })
      .from(shops)
      .where(eq(shops.workspaceId, workspaceId));

    const jobs = await this.db
      .select({
        id: syncJobs.id,
        syncType: syncJobs.syncType,
        status: syncJobs.status,
        itemsSynced: syncJobs.itemsSynced,
        errorMessage: syncJobs.errorMessage,
        connectedAccountId: syncJobs.connectedAccountId,
        completedAt: syncJobs.completedAt,
      })
      .from(syncJobs)
      .where(eq(syncJobs.workspaceId, workspaceId))
      .orderBy(desc(syncJobs.createdAt))
      .limit(20);

    return { connectedAccounts: accounts, shops: shopRows, recentSyncJobs: jobs };
  }
}

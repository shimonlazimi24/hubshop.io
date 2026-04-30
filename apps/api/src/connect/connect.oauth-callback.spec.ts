import {
  BadRequestException,
  HttpException,
  ServiceUnavailableException,
} from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import { connectedAccounts, tokenVault } from "@frodo/db";
import type { FrodoDb } from "@frodo/db";
import type { Response } from "express";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { SqsService } from "../jobs/sqs.service";
import { ConnectController } from "./connect.controller";
import { ConnectService } from "./connect.service";

const { exchangeShopAuthorizedCodeMock } = vi.hoisted(() => ({
  exchangeShopAuthorizedCodeMock: vi.fn(),
}));

vi.mock("@frodo/domain", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@frodo/domain")>();
  /** Vitest `importOriginal` can omit newer barrel exports; keep literals in sync with `error-codes.ts`. */
  const codes = {
    FRODO_TIKTOK_STATE_INVALID:
      actual.FRODO_TIKTOK_STATE_INVALID ?? "tiktok_state_invalid",
    FRODO_TIKTOK_TOKEN_EXCHANGE_FAILED:
      actual.FRODO_TIKTOK_TOKEN_EXCHANGE_FAILED ??
      "tiktok_token_exchange_failed",
    FRODO_TIKTOK_TOKEN_MISSING_SELLER_IDENTITY:
      actual.FRODO_TIKTOK_TOKEN_MISSING_SELLER_IDENTITY ??
      "tiktok_token_missing_seller_identity",
    FRODO_SQS_ENQUEUE_FAILED:
      actual.FRODO_SQS_ENQUEUE_FAILED ?? "sqs_enqueue_failed",
    FRODO_TIKTOK_SHOP_DISCOVERY_FAILED:
      actual.FRODO_TIKTOK_SHOP_DISCOVERY_FAILED ??
      "tiktok_shop_discovery_failed",
    FRODO_VAULT_DECRYPT_FAILED:
      actual.FRODO_VAULT_DECRYPT_FAILED ?? "vault_decrypt_failed",
  };
  return {
    ...actual,
    ...codes,
    exchangeShopAuthorizedCode: exchangeShopAuthorizedCodeMock,
  };
});

import {
  decryptSecret,
  FRODO_SQS_ENQUEUE_FAILED,
  signShopOAuthState,
} from "@frodo/domain";

const OAUTH_SECRET = "oauth-secret-at-least-32-characters-long-for-tests";
const TOKEN_MASTER = "token-encryption-master-key-32chars-min";
const WS_ID = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee";
const USER_ID = "ffffffff-ffff-4fff-8fff-ffffffffffff";

function configMap(): Record<string, string | boolean> {
  return {
    SHOP_OAUTH_STATE_SECRET: OAUTH_SECRET,
    TIKTOK_SHOP_APP_KEY: "app-key",
    TIKTOK_SHOP_APP_SECRET: "app-secret-32-chars-minimum-pad-00",
    TIKTOK_SHOP_SERVICE_ID: "svc",
    TIKTOK_SHOP_REDIRECT_URI: "http://localhost:8001/api/connect/shop/callback",
    TOKEN_ENCRYPTION_KEY: TOKEN_MASTER,
    TIKTOK_SHOP_AUTH_BASE: "https://auth.example/authorize",
    TIKTOK_TOKEN_URL: "https://auth.example/token",
  };
}

function mockConfig(): ConfigService {
  const m = configMap();
  return { get: (key: string) => m[key] } as ConfigService;
}

function nestExceptionMessage(e: HttpException): string {
  const r = e.getResponse();
  if (typeof r === "string") {
    return r;
  }
  if (typeof r === "object" && r !== null && "message" in r) {
    const m = (r as { message: string | string[] }).message;
    return Array.isArray(m) ? String(m[0]) : String(m);
  }
  return "";
}

function buildConnectServiceWithDb(mockDb: FrodoDb) {
  const cfg = mockConfig();
  const sqs = {
    sendJob: vi.fn().mockResolvedValue(undefined),
  } as unknown as SqsService;
  return { service: new ConnectService(mockDb, cfg, sqs), sqs };
}

describe("ConnectService.completeShopOAuth", () => {
  beforeEach(() => {
    exchangeShopAuthorizedCodeMock.mockReset();
  });

  it("creates account, encrypts vault token, enqueues SQS", async () => {
    exchangeShopAuthorizedCodeMock.mockResolvedValue({
      accessToken: "plain-access-token",
      refreshToken: "plain-refresh",
      sellerOpenId: "seller-open-1",
      raw: { code: 0, data: { open_id: "seller-open-1" } },
    });

    const vaultRows: Array<Record<string, unknown>> = [];
    const connectedRows: Array<Record<string, unknown>> = [];

    const mockDb = {
      insert: vi.fn((table: unknown) => ({
        values: (vals: Record<string, unknown>) => {
          if (table === connectedAccounts) {
            connectedRows.push(vals);
            return {
              onConflictDoUpdate: vi.fn(() => ({
                returning: vi.fn(() =>
                  Promise.resolve([{ id: "conn-account-id-1" }]),
                ),
              })),
            };
          }
          if (table === tokenVault) {
            vaultRows.push(vals);
            return {
              onConflictDoUpdate: vi.fn(() => Promise.resolve()),
            };
          }
          throw new Error("unexpected insert");
        },
      })),
      delete: vi.fn(() => ({
        where: vi.fn(() => Promise.resolve()),
      })),
    } as unknown as FrodoDb;

    const { token } = signShopOAuthState(
      { workspaceId: WS_ID, userId: USER_ID },
      OAUTH_SECRET,
    );

    const { service, sqs } = buildConnectServiceWithDb(mockDb);
    await service.completeShopOAuth("auth-code-xyz", token);

    expect(connectedRows[0]?.workspaceId).toBe(WS_ID);
    expect(connectedRows[0]?.platform).toBe("shop");
    expect(vaultRows[0]?.encryptedAccessToken).toBeTruthy();
    expect(String(vaultRows[0]?.encryptedAccessToken)).not.toContain(
      "plain-access-token",
    );
    expect(
      decryptSecret(
        String(vaultRows[0]?.encryptedAccessToken),
        TOKEN_MASTER,
      ),
    ).toBe("plain-access-token");

    expect(sqs.sendJob).toHaveBeenCalledWith({
      type: "shop_discovery_after_connect",
      workspaceId: WS_ID,
      connectedAccountId: "conn-account-id-1",
      dedupeKey: "shop_discovery:conn-account-id-1",
    });
  });

  it("rejects tampered state with tiktok_state_invalid", async () => {
    const mockDb = {
      insert: vi.fn(),
      delete: vi.fn(),
    } as unknown as FrodoDb;

    const { service } = buildConnectServiceWithDb(mockDb);
    try {
      await service.completeShopOAuth("code", "not-a-valid-state");
      expect.fail("expected BadRequestException");
    } catch (e) {
      expect(e).toBeInstanceOf(BadRequestException);
      expect(nestExceptionMessage(e as BadRequestException)).toBe(
        "tiktok_state_invalid",
      );
    }
    expect(exchangeShopAuthorizedCodeMock).not.toHaveBeenCalled();
  });

  it("rolls back connected account when SQS enqueue fails", async () => {
    exchangeShopAuthorizedCodeMock.mockResolvedValue({
      accessToken: "at",
      sellerOpenId: "seller",
      raw: {},
    });

    const deleteWhere = vi.fn(() => Promise.resolve());
    const mockDb = {
      insert: vi.fn((table: unknown) => ({
        values: () => {
          if (table === connectedAccounts) {
            return {
              onConflictDoUpdate: vi.fn(() => ({
                returning: vi.fn(() =>
                  Promise.resolve([{ id: "conn-to-rollback" }]),
                ),
              })),
            };
          }
          if (table === tokenVault) {
            return {
              onConflictDoUpdate: vi.fn(() => Promise.resolve()),
            };
          }
          throw new Error("unexpected insert");
        },
      })),
      delete: vi.fn(() => ({
        where: deleteWhere,
      })),
    } as unknown as FrodoDb;

    const cfg = mockConfig();
    const sqs = {
      sendJob: vi.fn().mockRejectedValue(new Error("sqs down")),
    } as unknown as SqsService;
    const service = new ConnectService(mockDb, cfg, sqs);

    const { token } = signShopOAuthState(
      { workspaceId: WS_ID, userId: USER_ID },
      OAUTH_SECRET,
    );

    try {
      await service.completeShopOAuth("c", token);
      expect.fail("expected ServiceUnavailableException");
    } catch (e) {
      expect(e).toBeInstanceOf(ServiceUnavailableException);
      expect(nestExceptionMessage(e as ServiceUnavailableException)).toBe(
        FRODO_SQS_ENQUEUE_FAILED,
      );
    }

    expect(deleteWhere).toHaveBeenCalled();
  });
});

describe("ConnectController.shopCallback", () => {
  const completeShopOAuth = vi.fn();

  function controller(): ConnectController {
    return new ConnectController(
      { completeShopOAuth } as unknown as ConnectService,
      {
        get: (k: string) =>
          k === "PUBLIC_WEB_ORIGIN" ? "https://app.test" : undefined,
      } as ConfigService,
    );
  }

  it("redirects to PUBLIC_WEB_ORIGIN/connect/shop/result?status=connected", async () => {
    completeShopOAuth.mockResolvedValueOnce(undefined);
    const redirect = vi.fn();
    const res = { redirect } as unknown as Response;
    await controller().shopCallback("cc", "ss", res);
    expect(redirect).toHaveBeenCalledWith(
      302,
      "https://app.test/connect/shop/result?status=connected",
    );
  });

  it("redirects stable error code when service rejects state", async () => {
    completeShopOAuth.mockRejectedValueOnce(
      new BadRequestException("tiktok_state_invalid"),
    );
    const redirect = vi.fn();
    const res = { redirect } as unknown as Response;
    await controller().shopCallback("cc", "bad", res);
    expect(redirect).toHaveBeenCalledWith(
      302,
      `https://app.test/connect/shop/result?error=${encodeURIComponent("tiktok_state_invalid")}`,
    );
  });
});

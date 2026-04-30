import { fetchWithRetry } from "../http-client";

export interface ShopTokenExchangeResult {
  accessToken: string;
  refreshToken?: string;
  accessTokenExpireInSec?: number;
  refreshTokenExpireInSec?: number;
  /** TikTok seller / user identifier when present */
  sellerOpenId?: string;
  scope?: string;
  raw: unknown;
}

function pickString(obj: Record<string, unknown>, keys: string[]): string | undefined {
  for (const k of keys) {
    const v = obj[k];
    if (typeof v === "string" && v.length > 0) {
      return v;
    }
  }
  return undefined;
}

function pickNumber(obj: Record<string, unknown>, keys: string[]): number | undefined {
  for (const k of keys) {
    const v = obj[k];
    if (typeof v === "number" && Number.isFinite(v)) {
      return v;
    }
    if (typeof v === "string" && /^\d+$/.test(v)) {
      return Number(v);
    }
  }
  return undefined;
}

function asRecord(v: unknown): Record<string, unknown> | null {
  return typeof v === "object" && v !== null ? (v as Record<string, unknown>) : null;
}

/**
 * Exchange TikTok Shop authorization code for tokens (real Partner Open API flow).
 * @see GET https://auth.tiktok-shops.com/api/v2/token/get
 */
export async function exchangeShopAuthorizedCode(params: {
  tokenUrl: string;
  appKey: string;
  appSecret: string;
  authCode: string;
  grantType?: string;
  fetchImpl?: typeof fetch;
}): Promise<ShopTokenExchangeResult> {
  const url = new URL(params.tokenUrl);
  url.searchParams.set("app_key", params.appKey);
  url.searchParams.set("app_secret", params.appSecret);
  url.searchParams.set("auth_code", params.authCode);
  url.searchParams.set("grant_type", params.grantType ?? "authorized_code");

  const res = await fetchWithRetry(
    url.toString(),
    { method: "GET" },
    undefined,
    params.fetchImpl ?? fetch,
  );
  const raw: unknown = await res.json().catch(() => ({}));

  if (!res.ok) {
    const msg =
      typeof raw === "object" &&
      raw !== null &&
      "message" in raw &&
      typeof (raw as { message?: unknown }).message === "string"
        ? (raw as { message: string }).message
        : `token_exchange_http_${res.status}`;
    throw new Error(msg);
  }

  const root = asRecord(raw);
  const code = root ? pickNumber(root, ["code"]) : undefined;
  if (code !== undefined && code !== 0) {
    const msg =
      pickString(root ?? {}, ["message"]) ?? `token_exchange_code_${code}`;
    throw new Error(msg);
  }

  const dataRec = asRecord(root?.data);
  const flat: Record<string, unknown> = {
    ...(root ?? {}),
    ...(dataRec ?? {}),
  };

  const accessToken = pickString(flat, [
    "access_token",
    "accessToken",
  ]);
  if (!accessToken) {
    throw new Error("token_exchange_missing_access_token");
  }

  return {
    accessToken,
    refreshToken: pickString(flat, ["refresh_token", "refreshToken"]),
    accessTokenExpireInSec: pickNumber(flat, [
      "access_token_expire_in",
      "accessTokenExpireIn",
      "expires_in",
    ]),
    refreshTokenExpireInSec: pickNumber(flat, [
      "refresh_token_expire_in",
      "refreshTokenExpireIn",
    ]),
    sellerOpenId: pickString(flat, [
      "open_id",
      "seller_open_id",
      "seller_id",
      "user_open_id",
    ]),
    scope: pickString(flat, ["scope", "scopes"]),
    raw,
  };
}

import { fetchWithRetry, type RetryPolicy } from "../http-client";
import {
  buildSignedShopGetUrl,
  buildSignedShopPostUrl,
  normalizeShop,
  type AuthorizedShopRow,
} from "./authorized-shops-core";
import { redactForLog } from "./redact";

export { type AuthorizedShopRow } from "./authorized-shops-core";

/** Read-only list/search endpoints (versioned paths may need updates per TikTok changelog). */
export const TIKTOK_SHOP_PRODUCT_SEARCH_PATH =
  "/product/202309/products/search";
export const TIKTOK_SHOP_ORDER_SEARCH_PATH = "/order/202309/orders/search";

function asRecord(v: unknown): Record<string, unknown> | null {
  return typeof v === "object" && v !== null
    ? (v as Record<string, unknown>)
    : null;
}

function str(v: unknown): string | undefined {
  return typeof v === "string" ? v : undefined;
}

/** Parsed TikTok Shop Open API business error (HTTP 200 with code !== 0). */
export class TikTokShopApiError extends Error {
  readonly tiktokCode?: number;
  readonly requestId?: string;

  constructor(message: string, opts?: { tiktokCode?: number; requestId?: string }) {
    super(message);
    this.name = "TikTokShopApiError";
    this.tiktokCode = opts?.tiktokCode;
    this.requestId = opts?.requestId;
  }
}

export function parseAuthorizedShopsSearchParams(url: string): {
  pathname: string;
  safeQueryForLog: Record<string, unknown>;
} {
  const u = new URL(url);
  const q: Record<string, unknown> = {};
  u.searchParams.forEach((value, key) => {
    q[key] = value;
  });
  return {
    pathname: u.pathname,
    safeQueryForLog: redactForLog(q) as Record<string, unknown>,
  };
}

export interface ShopApiMiddleware {
  /** Hook point for future rate limiting / circuit breaking. */
  beforeFetch?(ctx: {
    pathname: string;
    safeQueryForLog: Record<string, unknown>;
  }): void | Promise<void>;
  afterFetch?(ctx: {
    pathname: string;
    status: number;
    redactedBody: unknown;
  }): void | Promise<void>;
}

export interface ShopApiClientOptions {
  openApiBase: string;
  appKey: string;
  appSecret: string;
  fetchImpl?: typeof fetch;
  retryPolicy?: RetryPolicy;
  /** Never log full request URLs — use pathname + redacted query only. */
  logger?: {
    debug?: (msg: string, meta?: Record<string, unknown>) => void;
    warn?: (msg: string, meta?: Record<string, unknown>) => void;
  };
  middleware?: ShopApiMiddleware[];
}

const AUTHORIZED_SHOPS_PATH = "/authorization/202309/shops";

function assertTikTokBusinessOk(
  raw: unknown,
  res: Response,
  httpPrefix: string,
): void {
  if (!res.ok) {
    const root = asRecord(raw);
    throw new TikTokShopApiError(
      str(root?.message) ?? `${httpPrefix}_http_${res.status}`,
    );
  }
  const root = asRecord(raw);
  const code = root ? Number(root.code) : NaN;
  const requestId =
    str(root?.request_id) ?? str(root?.requestId) ?? undefined;
  if (root && "code" in root && code !== 0) {
    throw new TikTokShopApiError(
      str(root.message) ?? `${httpPrefix}_code_${String(root.code)}`,
      { tiktokCode: code, requestId },
    );
  }
}

/**
 * Thin TikTok Shop Open API client: signed GET/POST, retry, response parsing, redacted logs.
 * Dependency-injectable; middleware reserved for future rate limits / circuit breakers.
 */
export class ShopApiClient {
  private readonly opts: ShopApiClientOptions;

  constructor(opts: ShopApiClientOptions) {
    this.opts = opts;
  }

  /** Signed POST with JSON body (shop_cipher in query). */
  async postShopOpenApi(
    pathname: string,
    accessToken: string,
    shopCipher: string,
    body: Record<string, unknown>,
  ): Promise<{ raw: unknown }> {
    const url = buildSignedShopPostUrl({
      openApiBase: this.opts.openApiBase,
      pathname,
      appKey: this.opts.appKey,
      appSecret: this.opts.appSecret,
      accessToken,
      shopCipher,
      body,
    });

    const { pathname: pathLogged, safeQueryForLog } =
      parseAuthorizedShopsSearchParams(url);

    for (const m of this.opts.middleware ?? []) {
      await m.beforeFetch?.({
        pathname: pathLogged,
        safeQueryForLog,
      });
    }

    this.opts.logger?.debug?.("shop_api post request", {
      pathname: pathLogged,
      query: safeQueryForLog,
    });

    const bodyStr = JSON.stringify(body);
    const res = await fetchWithRetry(
      url,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-tts-access-token": accessToken,
        },
        body: bodyStr,
      },
      this.opts.retryPolicy,
      this.opts.fetchImpl ?? fetch,
    );

    const raw: unknown = await res.json().catch(() => ({}));
    const redactedBody = redactForLog(raw);

    for (const m of this.opts.middleware ?? []) {
      await m.afterFetch?.({
        pathname: pathLogged,
        status: res.status,
        redactedBody,
      });
    }

    assertTikTokBusinessOk(raw, res, "shop_api_post");

    this.opts.logger?.debug?.("shop_api post ok", {
      pathname: pathLogged,
      response: redactedBody,
    });

    return { raw };
  }

  async getAuthorizedShops(
    accessToken: string,
  ): Promise<{ raw: unknown; shops: AuthorizedShopRow[] }> {
    const pathname = AUTHORIZED_SHOPS_PATH;
    const url = buildSignedShopGetUrl({
      openApiBase: this.opts.openApiBase,
      pathname,
      appKey: this.opts.appKey,
      appSecret: this.opts.appSecret,
      accessToken,
    });

    const { pathname: pathLogged, safeQueryForLog } =
      parseAuthorizedShopsSearchParams(url);

    for (const m of this.opts.middleware ?? []) {
      await m.beforeFetch?.({
        pathname: pathLogged,
        safeQueryForLog,
      });
    }

    this.opts.logger?.debug?.("shop_api authorized_shops request", {
      pathname: pathLogged,
      query: safeQueryForLog,
    });

    const res = await fetchWithRetry(
      url,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "x-tts-access-token": accessToken,
        },
      },
      this.opts.retryPolicy,
      this.opts.fetchImpl ?? fetch,
    );

    const raw: unknown = await res.json().catch(() => ({}));
    const redactedBody = redactForLog(raw);

    for (const m of this.opts.middleware ?? []) {
      await m.afterFetch?.({
        pathname: pathLogged,
        status: res.status,
        redactedBody,
      });
    }

    assertTikTokBusinessOk(raw, res, "authorized_shops");

    const root = asRecord(raw);
    const data = asRecord(root?.data);
    const listRaw = data?.shops ?? data?.shop_list ?? [];
    const shops: AuthorizedShopRow[] = [];
    if (Array.isArray(listRaw)) {
      for (const item of listRaw) {
        const rec = asRecord(item);
        if (!rec) {
          continue;
        }
        const row = normalizeShop(rec);
        if (row) {
          shops.push(row);
        }
      }
    }

    this.opts.logger?.debug?.("shop_api authorized_shops ok", {
      pathname: pathLogged,
      shopCount: shops.length,
      response: redactedBody,
    });

    return { raw, shops };
  }
}

import { generateShopSign } from "../shop-sign";

export interface AuthorizedShopRow {
  /** TikTok internal shop id */
  shopId: string;
  shopCipher: string;
  shopCode: string;
  shopName: string;
  region: string;
  sellerType?: string;
  raw: Record<string, unknown>;
}

function str(v: unknown): string | undefined {
  return typeof v === "string" ? v : undefined;
}

/**
 * Build signed GET URL for TikTok Shop Open API (matches tiktok-shop-sdk sidecar rules).
 */
export function buildSignedShopGetUrl(input: {
  openApiBase: string;
  pathname: string;
  appKey: string;
  appSecret: string;
  accessToken: string;
  shopCipher?: string;
  extraQuery?: Record<string, string>;
  timestampSec?: number;
}): string {
  const base = input.openApiBase.replace(/\/$/, "");
  const pathname =
    input.pathname.startsWith("/") ? input.pathname : `/${input.pathname}`;
  const timestamp = input.timestampSec ?? Math.floor(Date.now() / 1000);

  const query: Record<string, string | number | boolean | undefined> = {
    app_key: input.appKey,
    timestamp: String(timestamp),
  };
  if (input.shopCipher) {
    query.shop_cipher = input.shopCipher;
  }
  if (input.extraQuery) {
    for (const [k, v] of Object.entries(input.extraQuery)) {
      query[k] = v;
    }
  }

  const sign = generateShopSign({
    pathname,
    query,
    body: undefined,
    appSecret: input.appSecret,
  });

  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(query)) {
    if (v === undefined) {
      continue;
    }
    params.set(k, String(v));
  }
  params.set("sign", sign);
  params.set("access_token", input.accessToken);

  return `${base}${pathname}?${params.toString()}`;
}

/** Signed POST URL (query carries app_key, timestamp, shop_cipher, sign, access_token; body is JSON). */
export function buildSignedShopPostUrl(input: {
  openApiBase: string;
  pathname: string;
  appKey: string;
  appSecret: string;
  accessToken: string;
  shopCipher: string;
  body: Record<string, unknown>;
  timestampSec?: number;
}): string {
  const base = input.openApiBase.replace(/\/$/, "");
  const pathname =
    input.pathname.startsWith("/") ? input.pathname : `/${input.pathname}`;
  const timestamp = input.timestampSec ?? Math.floor(Date.now() / 1000);

  const query: Record<string, string | number | boolean | undefined> = {
    app_key: input.appKey,
    timestamp: String(timestamp),
    shop_cipher: input.shopCipher,
  };

  const sign = generateShopSign({
    pathname,
    query,
    body: input.body,
    appSecret: input.appSecret,
  });

  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(query)) {
    if (v === undefined) {
      continue;
    }
    params.set(k, String(v));
  }
  params.set("sign", sign);
  params.set("access_token", input.accessToken);

  return `${base}${pathname}?${params.toString()}`;
}

export function normalizeShop(
  entry: Record<string, unknown>,
): AuthorizedShopRow | null {
  const shopId =
    str(entry.id) ?? str(entry.shop_id) ?? str(entry["shop_id"]);
  const cipher =
    str(entry.cipher) ??
    str(entry.shop_cipher) ??
    str(entry["shop_cipher"]);
  const code =
    str(entry.code) ?? str(entry.shop_code) ?? "";
  const name =
    str(entry.name) ?? str(entry.shop_name) ?? "Shop";
  const region =
    str(entry.region) ?? str(entry.region_code) ?? "UN";

  if (!shopId || !cipher) {
    return null;
  }

  return {
    shopId,
    shopCipher: cipher,
    shopCode: code,
    shopName: name,
    region,
    sellerType:
      str(entry.seller_type) ?? str(entry.sellerType) ?? undefined,
    raw: entry,
  };
}

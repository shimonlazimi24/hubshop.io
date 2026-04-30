import { createHmac } from "node:crypto";

const EXCLUDE = new Set(["access_token", "sign"]);

/**
 * TikTok Shop Open API HMAC-SHA256 signing (ported from tiktok-shop-sdk).
 * @see tiktok-shop-sdk/sdk/utils/generate-sign.ts
 */
export function generateShopSign(params: {
  pathname: string;
  query: Record<string, string | number | boolean | undefined>;
  body?: unknown;
  appSecret: string;
}): string {
  const { pathname, query, body, appSecret } = params;
  const sortedKeys = Object.keys(query)
    .filter((k) => !EXCLUDE.has(k))
    .sort();
  const paramString = sortedKeys
    .map((key) => {
      const v = query[key];
      return `${key}${v ?? ""}`;
    })
    .join("");

  let signString = `${pathname}${paramString}`;
  const isMultipart = false;
  if (
    !isMultipart &&
    body !== undefined &&
    body !== null &&
    typeof body === "object" &&
    Object.keys(body as object).length > 0
  ) {
    signString += JSON.stringify(body);
  }

  signString = `${appSecret}${signString}${appSecret}`;
  return createHmac("sha256", appSecret).update(signString).digest("hex");
}

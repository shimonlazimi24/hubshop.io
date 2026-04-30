import type { AuthorizedShopRow } from "./authorized-shops-core";
import { ShopApiClient } from "./shop-api-client";

export type { AuthorizedShopRow } from "./authorized-shops-core";
export {
  buildSignedShopGetUrl,
  buildSignedShopPostUrl,
  normalizeShop,
} from "./authorized-shops-core";

/** GET /authorization/202309/shops — read-only shop discovery. */
export async function fetchAuthorizedShops(params: {
  openApiBase: string;
  appKey: string;
  appSecret: string;
  accessToken: string;
  fetchImpl?: typeof fetch;
}): Promise<{ raw: unknown; shops: AuthorizedShopRow[] }> {
  const client = new ShopApiClient({
    openApiBase: params.openApiBase,
    appKey: params.appKey,
    appSecret: params.appSecret,
    fetchImpl: params.fetchImpl,
  });
  return client.getAuthorizedShops(params.accessToken);
}

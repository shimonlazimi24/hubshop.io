import { describe, expect, it, vi } from "vitest";
import {
  parseAuthorizedShopsSearchParams,
  ShopApiClient,
  TikTokShopApiError,
} from "./shop-api-client";

describe("ShopApiClient", () => {
  it("normalizes shop rows and never logs raw URL with secrets", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          code: 0,
          data: {
            shops: [
              {
                id: "sid1",
                cipher: "cipher1",
                code: "SC01",
                name: "My Shop",
                region: "US",
              },
            ],
          },
          request_id: "r",
        }),
        { status: 200 },
      ),
    );

    const debug = vi.fn();
    const client = new ShopApiClient({
      openApiBase: "https://open-api.test",
      appKey: "k",
      appSecret: "secretsecretsecretsecret",
      fetchImpl: fetchMock,
      logger: { debug },
    });

    const out = await client.getAuthorizedShops("super-secret-token");

    expect(out.shops).toHaveLength(1);
    expect(out.shops[0]?.shopId).toBe("sid1");

    const url = fetchMock.mock.calls[0]?.[0] as string;
    expect(url).toContain("access_token=super-secret-token");

    const logged = debug.mock.calls.find(
      (c) => c[0] === "shop_api authorized_shops request",
    );
    expect(logged).toBeDefined();
    const meta = logged?.[1] as { query?: Record<string, unknown> };
    expect(JSON.stringify(meta)).not.toContain("super-secret-token");
    expect(meta.query?.access_token).toBe("[redacted]");
    expect(meta.query?.sign).toBe("[redacted]");
  });

  it("throws TikTokShopApiError on business code !== 0", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({ code: 36009003, message: "bad", request_id: "x" }),
        { status: 200 },
      ),
    );

    const client = new ShopApiClient({
      openApiBase: "https://open-api.test",
      appKey: "k",
      appSecret: "secretsecretsecretsecret",
      fetchImpl: fetchMock,
    });

    await expect(client.getAuthorizedShops("tok")).rejects.toBeInstanceOf(
      TikTokShopApiError,
    );
  });
});

describe("parseAuthorizedShopsSearchParams", () => {
  it("redacts access_token and sign in log snapshot", () => {
    const url =
      "https://x.test/path?app_key=a&access_token=sekret&sign=abc123&timestamp=1";
    const { pathname, safeQueryForLog } = parseAuthorizedShopsSearchParams(url);
    expect(pathname).toBe("/path");
    expect(safeQueryForLog.access_token).toBe("[redacted]");
    expect(safeQueryForLog.sign).toBe("[redacted]");
    expect(safeQueryForLog.app_key).toBe("a");
  });
});
